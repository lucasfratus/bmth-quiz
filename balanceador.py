"""
Execução:
    python balanceador.py                       # porta 50050, servidores 50051 a 50053
    python balanceador.py --porta 50050 --servidores 127.0.0.1:50051 127.0.0.1:50052
"""

from __future__ import annotations

import argparse
import itertools
import logging
from datetime import datetime
from pathlib import Path
import threading
from concurrent import futures
from urllib.parse import unquote

import grpc

LOG = logging.getLogger("balanceador")

LOG_REQUISICOES = logging.getLogger("balanceador.requisicoes")

SERVIDORES_PADRAO = ["127.0.0.1:50051", "127.0.0.1:50052", "127.0.0.1:50053"]
TEMPO_LIMITE_S = 5  # segundos para um servidor responder antes de ser considerado lento

ARQUIVO_LOG_PADRAO = Path(__file__).resolve().parent / "balanceador.log"
CABECALHO_LOG = "IP/porta cliente; tipo requisicao; horario; servidor atribuido"

def dados(dados: bytes) -> bytes:
    return dados


def configurar_log_requisicoes(caminho: Path) -> None:
    if not caminho.exists() or caminho.stat().st_size == 0:
        with open(caminho, "a", encoding="utf-8") as arquivo:
            arquivo.write(CABECALHO_LOG + "\n")

    manipulador = logging.FileHandler(caminho, mode="a", encoding="utf-8")
    manipulador.setFormatter(logging.Formatter("%(message)s"))
    LOG_REQUISICOES.addHandler(manipulador)
    LOG_REQUISICOES.setLevel(logging.INFO)
    LOG_REQUISICOES.propagate = False  # não repete a linha no console


def endereco_do_cliente(contexto: grpc.ServicerContext) -> str:
    """
    com o ngrok, a conexão vem do agente do ngrok (na própria máquina).
    """
    origem = unquote(contexto.peer())  # ex: ipv4:127.0.0.1:53422
    for prefixo in ("ipv4:", "ipv6:"):
        if origem.startswith(prefixo):
            origem = origem[len(prefixo):]

    for chave, valor in contexto.invocation_metadata():
        if chave == "x-forwarded-for":
            return f"{valor} (via {origem})"
    return origem


class Balanceador:
    def __init__(self, destinos: list[str]) -> None:
        if not destinos:
            raise ValueError("é preciso informar pelo menos um servidor")
        self.destinos = list(destinos)
        self.canais = []
        for destino in self.destinos:
            self.canais.append(grpc.insecure_channel(destino))
        self._contador = itertools.count()
        self._trava = threading.Lock()

    def proximo_inicio(self) -> int:
        # garante que duas threads não peguem o mesmo índice ao mesmo tempo.
        with self._trava:
            return next(self._contador) % len(self.canais)


    def registrar(self, contexto: grpc.ServicerContext, metodo: str, servidor: str) -> None:
        """Escreve uma linha no log de requisições."""
        tipo = metodo.rsplit("/", 1)[-1]  # "/quiz.Quiz/IniciarPartida" -> "IniciarPartida"
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LOG_REQUISICOES.info("%s; %s; %s; %s", endereco_do_cliente(contexto), tipo, horario, servidor)


    def encaminhar(self, metodo: str, requisicao: bytes, contexto: grpc.ServicerContext) -> bytes:
        inicio = self.proximo_inicio()
        for deslocamento in range(len(self.canais)):
            i = (inicio + deslocamento) % len(self.canais)
            chamada = self.canais[i].unary_unary(
                metodo,
                request_serializer=dados,
                response_deserializer=dados,
            )
            try:
                resposta = chamada(requisicao, timeout=TEMPO_LIMITE_S)
                LOG.info("%s -> %s", metodo.rsplit("/", 1)[-1], self.destinos[i])
                self.registrar(contexto, metodo, self.destinos[i])

                return resposta
            except grpc.RpcError as erro:
                if erro.code() == grpc.StatusCode.UNAVAILABLE:
                    LOG.warning("%s indisponível, tentando o próximo", self.destinos[i])
                    continue
                # erros que incluem regras de jogo, como id inválido
                LOG.info("%s -> %s (%s)", metodo.rsplit("/", 1)[-1], self.destinos[i], erro.code().name)
                self.registrar(contexto, metodo, self.destinos[i])
                contexto.abort(erro.code(), erro.details())
        self.registrar(contexto, metodo, "nenhum (todos indisponíveis)")
        contexto.abort(grpc.StatusCode.UNAVAILABLE, "nenhum servidor disponível")


class Roteador(grpc.GenericRpcHandler):
    """Recebe qualquer rpc e entrega ao balanceador"""

    def __init__(self, balanceador: Balanceador) -> None:
        self._b = balanceador

    def service(self, detalhes:
        grpc.HandlerCallDetails):
        metodo = detalhes.method

        def tratar(requisicao: bytes, contexto: grpc.ServicerContext) -> bytes:
            return self._b.encaminhar(metodo, requisicao, contexto)

        return grpc.unary_unary_rpc_method_handler(
            tratar,
            request_deserializer=dados,
            response_serializer=dados,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Balanceador Round-Robin")
    ap.add_argument("--host", default="127.0.0.1", help="padrão: 127.0.0.1")
    ap.add_argument("--porta", type=int, default=50050)
    ap.add_argument("--servidores", nargs="+", default=SERVIDORES_PADRAO,
                    help="endereços dos servidores, ex.: 127.0.0.1:50051 127.0.0.1:50052")
    ap.add_argument("--log", type=Path, default=ARQUIVO_LOG_PADRAO,
                    help="arquivo do log de requisições")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    configurar_log_requisicoes(args.log)
    
    balanceador = Balanceador(args.servidores)
    servidor = grpc.server(
        futures.ThreadPoolExecutor(max_workers=20),
        handlers=[Roteador(balanceador)],
    )
    servidor.add_insecure_port(f"{args.host}:{args.porta}")
    servidor.start()
    LOG.info("balanceador ouvindo em %s:%s, servidores: %s",
             args.host, args.porta, ", ".join(args.servidores))
    LOG.info("log de requisições em %s", args.log.resolve())
    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        LOG.info("desligando")
        servidor.stop(grace=1)
    return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())