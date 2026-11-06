"""
Execução:
    python balanceador.py                       # porta 50050, servidores 50051 a 50053
    python balanceador.py --porta 50050 --servidores 127.0.0.1:50051 127.0.0.1:50052
"""

from __future__ import annotations

import argparse
import itertools
import logging
import threading
from concurrent import futures

import grpc

LOG = logging.getLogger("balanceador")

SERVIDORES_PADRAO = ["127.0.0.1:50051", "127.0.0.1:50052", "127.0.0.1:50053"]
TEMPO_LIMITE_S = 5  # segundos para um servidor responder antes de ser considerado lento


def _dados(dados: bytes) -> bytes:
    return dados


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

    def encaminhar(self, metodo: str, requisicao: bytes, contexto: grpc.ServicerContext) -> bytes:
        inicio = self.proximo_inicio()
        for deslocamento in range(len(self.canais)):
            i = (inicio + deslocamento) % len(self.canais)
            chamada = self.canais[i].unary_unary(
                metodo,
                request_serializer=_dados,
                response_deserializer=_dados,
            )
            try:
                resposta = chamada(requisicao, timeout=TEMPO_LIMITE_S)
                LOG.info("%s -> %s", metodo.rsplit("/", 1)[-1], self.destinos[i])
                return resposta
            except grpc.RpcError as erro:
                if erro.code() == grpc.StatusCode.UNAVAILABLE:
                    LOG.warning("%s indisponível, tentando o próximo", self.destinos[i])
                    continue
                # Erros que incluem regras de jogo, como id inválido
                LOG.info("%s -> %s (%s)", metodo.rsplit("/", 1)[-1], self.destinos[i], erro.code().name)
                contexto.abort(erro.code(), erro.details())
        contexto.abort(grpc.StatusCode.UNAVAILABLE, "nenhum servidor disponível")


class Roteador(grpc.GenericRpcHandler):
    """Recebe qualquer rpc e entrega ao balanceador"""

    def __init__(self, balanceador: Balanceador) -> None:
        self._b = balanceador

    def service(self, detalhes: grpc.HandlerCallDetails):
        metodo = detalhes.method

        def tratar(requisicao: bytes, contexto: grpc.ServicerContext) -> bytes:
            return self._b.encaminhar(metodo, requisicao, contexto)

        return grpc.unary_unary_rpc_method_handler(
            tratar,
            request_deserializer=_dados,
            response_serializer=_dados,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Balanceador Round-Robin do quiz")
    ap.add_argument("--host", default="127.0.0.1", help="padrão: 127.0.0.1")
    ap.add_argument("--porta", type=int, default=50050)
    ap.add_argument("--servidores", nargs="+", default=SERVIDORES_PADRAO,
                    help="endereços dos servidores, ex.: 127.0.0.1:50051 127.0.0.1:50052")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    balanceador = Balanceador(args.servidores)
    servidor = grpc.server(
        futures.ThreadPoolExecutor(max_workers=20),
        handlers=[Roteador(balanceador)],
    )
    servidor.add_insecure_port(f"{args.host}:{args.porta}")
    servidor.start()
    LOG.info("balanceador ouvindo em %s:%s, servidores: %s",
             args.host, args.porta, ", ".join(args.servidores))
    servidor.wait_for_termination()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())