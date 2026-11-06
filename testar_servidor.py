"""
Uso:
    python testar_servidor.py                         # servidor 1, localhost:50051
    python testar_servidor.py --alvo localhost:50052  # outro servidor
    python testar_servidor.py --alvo localhost:50050  # o balanceador
"""

from __future__ import annotations

import argparse
import random
import string
import sys

import grpc

import quiz_pb2 as pb
import quiz_pb2_grpc as pb_grpc


def chamar(descricao, funcao, pedido, espera_erro=None):
    try:
        resposta = funcao(pedido, timeout=5)
    except grpc.RpcError as e:
        ok = e.code() == espera_erro
        print(f"[{'ok' if ok else 'FALHOU'}] {descricao}: {e.code().name} | {e.details()}")
        return None if ok else False
    if espera_erro:
        print(f"[FALHOU] {descricao}: esperava {espera_erro.name} e veio resposta")
        return False
    print(f"[ok] {descricao}")
    return resposta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo", default="localhost:50051")
    args = ap.parse_args()

    stub = pb_grpc.QuizStub(grpc.insecure_channel(args.alvo))
    nickname = "teste_" + "".join(random.choices(string.ascii_lowercase, k=5))
    falhas = 0

    r = chamar("ListarRanking", stub.ListarRanking, pb.ListarRankingRequest(limite=10))
    if r is False:
        falhas += 1
    elif r is not None:
        print(f"     {len(r.entradas)} vencedores no ranking")

    e = chamar(f"IniciarPartida '{nickname}'", stub.IniciarPartida, pb.IniciarPartidaRequest(nickname=nickname))
    if not e:
        print("Sem partida criada.")
        return 1
    print(f"     partida {e.id_partida} | {pb.Status.Name(e.status)} | pergunta {e.ordem} de {e.total} ({e.nivel})")
    print(f"     {e.enunciado}")
    for alt in e.alternativas:
        print(f"       {alt.letra}) {alt.texto}")
    print(f"     ajudas: {', '.join(a.nome for a in e.ajudas if a.esta_disponivel)}")

    e2 = chamar("ObterEstado da mesma partida", stub.ObterEstado, pb.PartidaRequest(id_partida=e.id_partida))
    if e2 and e2.enunciado == e.enunciado:
        print(f"     mesma pergunta (o F5 não sorteia outra), relógio em {e2.segundos_decorridos:.2f} s")
    else:
        print("[FALHOU] ObterEstado trouxe outra pergunta")
        falhas += 1

    testes_de_erro = [
        ("nickname repetido (maiúsculas)", stub.IniciarPartida,
         pb.IniciarPartidaRequest(nickname=nickname.upper()), grpc.StatusCode.ALREADY_EXISTS),
        ("nickname curto", stub.IniciarPartida,
         pb.IniciarPartidaRequest(nickname="ab"), grpc.StatusCode.INVALID_ARGUMENT),
        ("partida inexistente", stub.ObterEstado,
         pb.PartidaRequest(id_partida=999_999), grpc.StatusCode.NOT_FOUND),
        ("id não informado (0)", stub.ObterEstado,
         pb.PartidaRequest(), grpc.StatusCode.NOT_FOUND),
        ("Responder", stub.Responder,
         pb.ResponderRequest(id_partida=e.id_partida, letra="A"), grpc.StatusCode.UNIMPLEMENTED),
    ]
    for descricao, funcao, pedido, codigo in testes_de_erro:
        if chamar(descricao, funcao, pedido, espera_erro=codigo) is False:
            falhas += 1

    print(r"OK" if not falhas else f"\n{falhas} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
