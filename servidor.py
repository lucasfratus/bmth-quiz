import re
import time
import logging
import argparse
import sqlite3
import sys
from pathlib import Path
from concurrent import futures
from contextlib import closing
from datetime import datetime


log = logging.getLogger("servidor")

import grpc

import quiz_pb2 as pb
import quiz_pb2_grpc as pb_grpc



NIVEIS_DA_PARTIDA = [
    "Fácil", "Fácil", "Fácil",
    "Médio", "Médio", "Médio",
    "Difícil", "Difícil", "Difícil",
    "Final",
]
TOTAL_PERGUNTAS = len(NIVEIS_DA_PARTIDA)
 
PONTOS_BASE = {"Fácil": 100, "Médio": 200, "Difícil": 300, "Final": 1000}


JANELA_DE_BONUS = 60
FATOR_BONUS = {"Fácil": 1, "Médio": 1.5, "Difícil": 2, "Final": 10}

NICKNAME_REGEX = re.compile(r"^[A-Za-z0-9_.\-]{3,20}$")


def valida_nickname(nickname: str) -> bool:
    return bool(NICKNAME_REGEX.match(nickname))


def bonus_maximo(nivel: str, segundos: float) -> int:
    segundos_completos = int(segundos)
    return int(max(0, JANELA_DE_BONUS - segundos_completos) * FATOR_BONUS[nivel])


NIVEL_DO_BANCO = {"facil": "Fácil", "medio": "Médio", "dificil": "Difícil", "final": "Final"}
NIVEL_PARA_BANCO = {"Fácil": "facil", "Médio": "medio", "Difícil": "dificil", "Final": "final"}
 
STATUS_DO_BANCO = {"andamento": pb.EM_ANDAMENTO, "vitoria": pb.VITORIA, "derrota": pb.DERROTA}
 
# (tipo no proto, nome, descrição, coluna da flag na tabela jogo)
AJUDAS = [
    (pb.MEIO_A_MEIO, "Meio a meio", "Elimina 2 alternativas erradas", "usou_meio"),
    (pb.PULO, "Pulo", "Troca por outra pergunta do mesmo nível", "usou_pulo"),
    (pb.PASSE_LIVRE, "Passe livre", "Acerta esta pergunta, sem bônus de tempo", "usou_passe"),
]


SQL_RANKING = """
    SELECT j.nickname, g.pontuacao, g.finalizado_em
    FROM jogo g JOIN jogador j ON j.id = g.jogador_id
    WHERE g.status = 'vitoria'
    ORDER BY g.pontuacao DESC, g.finalizado_em ASC
    LIMIT ?
"""
 
SQL_JOGO = """
    SELECT g.*, j.nickname FROM jogo g JOIN jogador j ON j.id = g.jogador_id WHERE g.id = ?
"""
 
SQL_PERGUNTA_ATUAL = """
    SELECT p.*, a.criado_em AS exibida_em
    FROM acao a JOIN pergunta p ON p.id = a.pergunta_id
    WHERE a.jogo_id = ? AND a.ordem = ? AND a.tipo = 'exibicao'
    ORDER BY a.id DESC
    LIMIT 1
"""
 
SQL_SORTEAR = """
    SELECT id FROM pergunta
    WHERE nivel = ?
      AND id NOT IN (SELECT pergunta_id FROM acao WHERE jogo_id = ? AND tipo = 'exibicao')
    ORDER BY random()
    LIMIT 1
"""


def agora_ms() -> int:
    return int(time.time() * 1000)
 
 
class ErroRpc(Exception):
 
    def __init__(self, codigo: grpc.StatusCode, mensagem: str):
        super().__init__(mensagem)
        self.codigo, self.mensagem = codigo, mensagem
 
 
def resumir_request(request) -> str:
    request = str(request).replace("\n", " ").strip()
    if request == "":
        request = "(vazio)"
    return request


def abortar_com_erro(context, nome_rpc: str, request, erro: Exception):
    """escreve no log e encerra a chamada com um status.
 
    - ErroRpc (erro de regra do jogo) vira o código que o rpc escolheu, como NOT_FOUND.
    - Qualquer outro erro vira INTERNAL
    """
    pedido = resumir_request(request)
    if isinstance(erro, ErroRpc):
        log.info("%s %s -> %s: %s", nome_rpc, pedido, erro.codigo.name, erro.mensagem)
        context.abort(erro.codigo, erro.mensagem)
    log.error("%s %s -> erro inesperado", nome_rpc, pedido, exc_info=erro)
    context.abort(grpc.StatusCode.INTERNAL, "Erro interno no servidor.")
 
 
def registrar_sucesso(nome_rpc: str, request, inicio: float):
    """Escreve no log que o rpc deu certo e quanto tempo levou."""
    milissegundos = (time.perf_counter() - inicio) * 1000
    log.info("%s %s -> ok (%.0f ms)", nome_rpc, resumir_request(request), milissegundos)


class ServidorQuiz(pb_grpc.QuizServicer):
    def __init__(self, caminho_banco: Path):
        self.caminho_banco = caminho_banco
 
    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho_banco, timeout=5, isolation_level=None)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao


    def ListarRanking(self, request, context):
        inicio = time.perf_counter()
        try:
            limite = request.limite if 0 < request.limite <= 100 else 10
            with closing(self._conectar()) as conexao:
                linhas = conexao.execute(SQL_RANKING, (limite,)).fetchall()
            entradas = []
            for linha in linhas:
                data = datetime.fromtimestamp(linha["finalizado_em"] / 1000).strftime("%d/%m/%Y")
                entradas.append(pb.EntradaRanking(
                    nickname=linha["nickname"],
                    pontuacao=linha["pontuacao"],
                    data=data,
                ))
            resposta = pb.ListarRankingResponse(entradas=entradas)
        except Exception as erro:
            abortar_com_erro(context, "ListarRanking", request, erro)
        registrar_sucesso("ListarRanking", request, inicio)
        return resposta

 
    def IniciarPartida(self, request, context):
        inicio = time.perf_counter()
        try:
            nickname = request.nickname.strip()
            if not valida_nickname(nickname):
                raise ErroRpc(grpc.StatusCode.INVALID_ARGUMENT,
                              "Use de 3 a 20 caracteres: letras sem acento, números, ponto, hífen ou underline.")
            with closing(self._conectar()) as conexao:
                conexao.execute("BEGIN IMMEDIATE")
                try:
                    jogador_id = conexao.execute(
                        "INSERT INTO jogador (nickname, criado_em) VALUES (?, ?)", (nickname, agora_ms())
                    ).lastrowid
                except sqlite3.IntegrityError:
                    raise ErroRpc(grpc.StatusCode.ALREADY_EXISTS,
                                  f"O nickname “{nickname}” já foi usado. Escolha outro.")
                jogo_id = conexao.execute(
                    "INSERT INTO jogo (jogador_id, iniciado_em) VALUES (?, ?)", (jogador_id, agora_ms())
                ).lastrowid
                conexao.execute("COMMIT")
                resposta = self._estado(conexao, jogo_id)
        except Exception as erro:
            abortar_com_erro(context, "IniciarPartida", request, erro)
        registrar_sucesso("IniciarPartida", request, inicio)
        return resposta

 
    def ObterEstado(self, request, context):
        inicio = time.perf_counter()
        try:
            with closing(self._conectar()) as conexao:
                resposta = self._estado(conexao, request.id_partida)
        except Exception as erro:
            abortar_com_erro(context, "ObterEstado", request, erro)
        registrar_sucesso("ObterEstado", request, inicio)
        return resposta

 
    def Responder(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Entrega Final.")

 
    def UsarAjuda(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Entrega Final.")


    def _estado(self, conexao: sqlite3.Connection, jogo_id: int) -> pb.EstadoPartida:
        """Lê a partida e, se a posição atual ainda não tem uma pergunta, sorteia.
 
        Tudo dentro de BEGIN IMMEDIATE: se dois servidores receberem o mesmo
        ObterEstado ao mesmo tempo, o segundo espera o primeiro e encontra a
        pergunta já sorteada, em vez de sortear outra.
        """
        if jogo_id <= 0:
            raise ErroRpc(grpc.StatusCode.NOT_FOUND, "Informe o id da partida.")
 
        conexao.execute("BEGIN IMMEDIATE")
        jogo = conexao.execute(SQL_JOGO, (jogo_id,)).fetchone()
        if jogo is None:
            raise ErroRpc(grpc.StatusCode.NOT_FOUND, "Essa partida não existe. Comece um novo jogo.")
 
        ordem = jogo["ordem_atual"]
        nivel = NIVEIS_DA_PARTIDA[ordem - 1]
        atual = conexao.execute(SQL_PERGUNTA_ATUAL, (jogo_id, ordem)).fetchone()
 
        if atual is None and jogo["status"] == "andamento":
            sorteada = conexao.execute(SQL_SORTEAR, (NIVEL_PARA_BANCO[nivel], jogo_id)).fetchone()
            if sorteada is None:
                raise ErroRpc(grpc.StatusCode.FAILED_PRECONDITION, f"Acabaram as perguntas do nível {nivel}.")
            conexao.execute(
                "INSERT INTO acao (jogo_id, ordem, pergunta_id, tipo, criado_em) VALUES (?, ?, ?, 'exibicao', ?)",
                (jogo_id, ordem, sorteada["id"], agora_ms()),
            )
            atual = conexao.execute(SQL_PERGUNTA_ATUAL, (jogo_id, ordem)).fetchone()
        conexao.execute("COMMIT")
 
        linha_meio = conexao.execute(
            "SELECT eliminadas FROM acao WHERE jogo_id = ? AND tipo = 'meio_a_meio' AND pergunta_id = ?",
            (jogo_id, atual["id"]),
        ).fetchone()
 
        alternativas = []
        for letra in ["A", "B", "C", "D"]:
            texto = atual["alt_" + letra.lower()]
            alternativas.append(pb.Alternativa(letra=letra, texto=texto))
 
        eliminadas = []
        if linha_meio is not None:
            eliminadas = linha_meio["eliminadas"].split(",")
 
        return pb.EstadoPartida(
            id_partida=jogo_id,
            nickname=jogo["nickname"],
            status=STATUS_DO_BANCO[jogo["status"]],
            nivel=nivel,
            ordem=ordem,
            total=TOTAL_PERGUNTAS,
            enunciado=atual["enunciado"],
            alternativas=alternativas,
            eliminadas=eliminadas,
            pontuacao=jogo["pontuacao"],
            pontos_base=PONTOS_BASE[nivel],
            bonus_maximo=bonus_maximo(nivel),
            janela_bonus_s=JANELA_DE_BONUS,
            segundos_decorridos=max(0, agora_ms() - atual["exibida_em"]) / 1000,
            ajudas=self._ajudas(jogo, nivel),
            niveis_da_partida=NIVEIS_DA_PARTIDA,
        )
 
    @staticmethod
    def _ajudas(jogo: sqlite3.Row, nivel: str) -> list[pb.Ajuda]:
        ajudas = []
        for tipo, nome, descricao, coluna in AJUDAS:
            motivo = ""
            if jogo[coluna]:
                motivo = "Já usada"
            elif tipo == pb.PASSE_LIVRE and nivel == "Final":
                motivo = "Não vale na pergunta final"
            ajudas.append(pb.Ajuda(tipo=tipo, nome=nome, descricao=descricao,
                                   esta_disponivel=not motivo, motivo=motivo))
        return ajudas
 
 
def main() -> int:
    ap = argparse.ArgumentParser(description="Servidor gRPC do Show do Horizonte")
    ap.add_argument("--id", type=int, required=True, help="número do servidor (1, 2, 3...)")
    ap.add_argument("--porta", type=int, help="padrão: 50050 + id")
    ap.add_argument("--host", default="127.0.0.1",
                    help="padrão: 127.0.0.1, apenas o balanceador na mesma máquina é permitido")
    ap.add_argument("--banco", type=Path, default=Path(__file__).resolve().parent / "quiz.db")
    args = ap.parse_args()
    porta = args.porta or 50050 + args.id
 
    logging.basicConfig(level=logging.INFO, format=f"%(asctime)s [servidor {args.id}] %(message)s",
                        datefmt="%H:%M:%S")
 
    if not args.banco.exists():
        log.error("Banco %s não encontrado. Crie com: python banco/criar_banco.py", args.banco)
        return 1
 
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_QuizServicer_to_server(ServidorQuiz(args.banco), servidor)
    servidor.add_insecure_port(f"{args.host}:{porta}")
    servidor.start()
    log.info("ouvindo em %s:%d, banco %s", args.host, porta, args.banco.resolve())
    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        log.info("desligando")
        servidor.stop(grace=1)
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())

