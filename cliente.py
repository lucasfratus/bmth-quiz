"""
Uso:
    python cliente.py                          # fala com o balanceador local, 127.0.0.1:50050
    python cliente.py --endereco 127.0.0.1:50051   # fala direto com um servidor
    python cliente.py --endereco <endereço>.ngrok-free.app:443 --seguro   # pelo ngrok

"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap

import grpc

import quiz_pb2 as pb
import quiz_pb2_grpc as pb_grpc

LARGURA = 64
TEMPO_LIMITE_S = 10  # quanto esperar por uma resposta do servidor

# Cores ANSI (códigos que o terminal entende). Desligadas quando a saída não é um
# terminal (ex.: redirecionada para arquivo) ou quando a variável NO_COLOR existe.
USAR_COR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
ROXO = "35"
VERMELHO = "31"
VERDE = "32"
AMARELO = "33"
CINZA = "90"


AJUDA_DA_TECLA = {"M": pb.MEIO_A_MEIO, "P": pb.PULO, "L": pb.PASSE_LIVRE}
TECLA_DA_AJUDA = {pb.MEIO_A_MEIO: "M", pb.PULO: "P", pb.PASSE_LIVRE: "L"}


def colorir(texto, codigo):
    if not USAR_COR:
        return texto
    return "\033[" + codigo + "m" + texto + "\033[0m"


def limpar_tela():
    if USAR_COR:
        print("\033[2J\033[H", end="")
    else:
        print("\n" + "-" * LARGURA)


def linha(caractere="═"):
    return colorir(caractere * LARGURA, ROXO)


def pausar():
    input(colorir("\nEnter para continuar...", CINZA))


def quebrar(texto, recuo="  "):
    """Quebra um texto longo em várias linhas que cabem na tela."""
    return textwrap.fill(texto, width=LARGURA, initial_indent=recuo, subsequent_indent=recuo)


def texto_do_erro(erro):
    """Traduz um erro do gRPC em uma frase para o jogador."""
    codigo = erro.code()
    if codigo == grpc.StatusCode.UNAVAILABLE:
        return "Não consegui falar com o servidor. Confira se o balanceador está no ar."
    if codigo == grpc.StatusCode.DEADLINE_EXCEEDED:
        return "O servidor demorou demais para responder."
    if codigo == grpc.StatusCode.UNIMPLEMENTED:
        return "O servidor ainda não tem essa função (" + erro.details() + ")"
    return erro.details()



def tela_inicial(stub):
    while True:
        limpar_tela()
        print(linha())
        print(colorir("   ☠  S H O W   D O   H O R I Z O N T E  ☠", ROXO))
        print(colorir("   o quiz de Bring Me the Horizon", CINZA))
        print(linha())
        print()
        print("   [1] Novo jogo")
        print("   [2] Maiores pontuações")
        print("   [0] Sair")
        print()
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            tela_novo_jogo(stub)
        elif opcao == "2":
            tela_ranking(stub)
        elif opcao == "0":
            print("Até mais!")
            return
        else:
            print("Opção inválida.")
            pausar()


def tela_ranking(stub):
    limpar_tela()
    print(linha())
    print(colorir("   MAIORES PONTUAÇÕES", AMARELO))
    print(linha())
    print()
    try:
        resposta = stub.ListarRanking(pb.ListarRankingRequest(limite=10), timeout=TEMPO_LIMITE_S)
    except grpc.RpcError as erro:
        print(colorir(texto_do_erro(erro), VERMELHO))
        pausar()
        return

    if len(resposta.entradas) == 0:
        print("   Ninguém zerou o jogo ainda. Seja o primeiro!")
    else:
        posicao = 1
        for entrada in resposta.entradas:
            print(f"   {posicao:>2}. {entrada.nickname:<20} {entrada.pontuacao:>6} pts   {entrada.data}")
            posicao += 1
    pausar()



def tela_novo_jogo(stub):
    limpar_tela()
    print(linha())
    print(colorir("   NOVO JOGO", AMARELO))
    print(linha())
    print()
    print("   Nickname: de 3 a 20 caracteres (letras sem acento, números, . - _).")
    print()
    while True:
        nickname = input("Nickname (Enter em branco volta ao menu): ").strip()
        if nickname == "":
            return
        try:
            estado = stub.IniciarPartida(pb.IniciarPartidaRequest(nickname=nickname), timeout=TEMPO_LIMITE_S)
        except grpc.RpcError as erro:
            codigo = erro.code()
            if codigo == grpc.StatusCode.ALREADY_EXISTS or codigo == grpc.StatusCode.INVALID_ARGUMENT:
                print(colorir(erro.details(), VERMELHO))
                continue
            print(colorir(texto_do_erro(erro), VERMELHO))
            pausar()
            return
        jogar(stub, estado)
        return


def achar_ajuda(estado, tipo):
    for ajuda in estado.ajudas:
        if ajuda.tipo == tipo:
            return ajuda
    return None


def mostrar_pergunta(estado):
    limpar_tela()
    print(linha())
    print(f" {estado.nivel.upper()}   |   Pergunta {estado.ordem} de {estado.total}"
          f"   |   {estado.nickname}   |   {estado.pontuacao} pts")
    print(linha())
    print()
    print(quebrar(estado.enunciado))
    print()
    for alternativa in estado.alternativas:
        if alternativa.letra in estado.eliminadas:
            print(colorir(f"    {alternativa.letra}) {alternativa.texto}  (eliminada)", CINZA))
        else:
            print(f"    {alternativa.letra}) {alternativa.texto}")
    print()
    print(colorir("  Ajudas:", AMARELO))
    for ajuda in estado.ajudas:
        tecla = TECLA_DA_AJUDA[ajuda.tipo]
        if ajuda.esta_disponivel:
            print(f"    [{tecla}] {ajuda.nome}: {ajuda.descricao}")
        else:
            print(colorir(f"    [{tecla}] {ajuda.nome}: indisponível ({ajuda.motivo})", CINZA))
    print()
    print(f"  Vale {estado.pontos_base} pontos + bônus de até {estado.bonus_maximo}.")
    print(f"  O bônus diminui com o tempo e zera em {estado.janela_bonus_s} segundos.")
    print()
    print("  Responda com A, B, C ou D. Para uma ajuda, use M, P ou L.")


def ler_jogada(estado):
    """Pede a jogada até receber uma válida. Devolve a tecla em maiúscula."""
    while True:
        jogada = input("Sua jogada: ").strip().upper()
        if jogada in ("A", "B", "C", "D"):
            if jogada in estado.eliminadas:
                print("Essa alternativa foi eliminada pelo meio a meio. Escolha outra.")
                continue
            return jogada
        if jogada in AJUDA_DA_TECLA:
            ajuda = achar_ajuda(estado, AJUDA_DA_TECLA[jogada])
            if ajuda is None or not ajuda.esta_disponivel:
                motivo = ""
                if ajuda is not None:
                    motivo = ajuda.motivo
                print("Essa ajuda não pode ser usada agora. " + motivo)
                continue
            return jogada
        print("Digite A, B, C ou D para responder, ou M, P ou L para usar uma ajuda.")


def buscar_estado(stub, id_partida):
    """Pede ao servidor a pergunta atual. Devolve None se não conseguir."""
    try:
        return stub.ObterEstado(pb.PartidaRequest(id_partida=id_partida), timeout=TEMPO_LIMITE_S)
    except grpc.RpcError as erro:
        print(colorir(texto_do_erro(erro), VERMELHO))
        print("A partida continua salva no servidor.")
        pausar()
        return None


def jogar(stub, estado):
    """Repete: mostra a pergunta, lê a jogada e executa. Termina no fim do jogo."""
    while estado is not None:
        if estado.status != pb.EM_ANDAMENTO:
            print("Essa partida já terminou.")
            pausar()
            return
        mostrar_pergunta(estado)
        jogada = ler_jogada(estado)
        if jogada in AJUDA_DA_TECLA:
            estado = usar_ajuda(stub, estado, AJUDA_DA_TECLA[jogada])
        else:
            estado = responder(stub, estado, jogada)



def responder(stub, estado, letra):
    """Envia a resposta. Devolve a próxima pergunta, ou None se o jogo acabou."""
    pedido = pb.ResponderRequest(id_partida=estado.id_partida, letra=letra)
    try:
        resultado = stub.Responder(pedido, timeout=TEMPO_LIMITE_S)
    except grpc.RpcError as erro:
        print(colorir(texto_do_erro(erro), VERMELHO))
        pausar()
        return estado  # volta para a mesma pergunta

    mostrar_resultado(resultado)
    if resultado.status == pb.DERROTA:
        tela_fim_de_jogo(resultado)
        return None
    if resultado.status == pb.VITORIA:
        tela_vencedor(resultado)
        return None
    return buscar_estado(stub, estado.id_partida)


def mostrar_resultado(resultado):
    limpar_tela()
    print(linha())
    if resultado.correta:
        print(colorir("   ACERTOU!", VERDE))
    else:
        print(colorir("   ERROU!", VERMELHO))
    print(linha())
    print()
    print(f"  Você respondeu: {resultado.letra_alt_escolhida}) {resultado.texto_alt_escolhida}")
    if not resultado.correta:
        print(f"  A correta era:  {resultado.letra_alt_correta}) {resultado.texto_alt_correta}")
    else:
        print(f"  Você ganhou {resultado.pontos_ganhos} pontos (bônus de tempo: {resultado.bonus}).")
    print(f"  Pontuação: {resultado.pontuacao}")
    pausar()


def tela_fim_de_jogo(resultado):
    limpar_tela()
    print(linha())
    print(colorir("   FIM DE JOGO", VERMELHO))
    print(linha())
    print()
    print(f"  Você errou a pergunta {resultado.ordem} de {resultado.total} ({resultado.nivel}):")
    print()
    print(quebrar(resultado.enunciado))
    print()
    print(f"  Resposta certa: {resultado.letra_alt_correta}) {resultado.texto_alt_correta}")
    print()
    print(f"  Pontuação final: {resultado.pontuacao}")
    pausar()


def tela_vencedor(resultado):
    limpar_tela()
    print(linha())
    print(colorir("   ★  VOCÊ ZEROU O SHOW DO HORIZONTE  ★", VERDE))
    print(linha())
    print()
    print(f"  Pontuação final: {resultado.pontuacao}")
    if resultado.posicao_ranking > 0:
        print(f"  Você entrou no ranking em {resultado.posicao_ranking}º lugar!")
    else:
        print("  Sua pontuação ficou fora do top 10.")
    pausar()


def usar_ajuda(stub, estado, tipo):
    """Usa uma ajuda. Devolve a pergunta atualizada (ou a nova, se o pulo é utilizado)."""
    pedido = pb.UsarAjudaRequest(id_partida=estado.id_partida, ajuda=tipo)
    try:
        resultado = stub.UsarAjuda(pedido, timeout=TEMPO_LIMITE_S)
    except grpc.RpcError as erro:
        print(colorir(texto_do_erro(erro), VERMELHO))
        pausar()
        return estado  # volta para a mesma pergunta

    limpar_tela()
    print(linha())
    if tipo == pb.MEIO_A_MEIO:
        print(colorir("   MEIO A MEIO", AMARELO))
        print(linha())
        print()
        print("  Alternativas eliminadas: " + " e ".join(resultado.eliminadas))
    elif tipo == pb.PULO:
        print(colorir("   PULO", AMARELO))
        print(linha())
        print()
        print("  Você pulou esta pergunta:")
        print(quebrar(resultado.enunciado_pulado))
        print()
        print(f" Vem aí uma outra pergunta do nível {resultado.nivel} (continua a pergunta {resultado.ordem} de {resultado.total}).")
    elif tipo == pb.PASSE_LIVRE:
        print(colorir("   PASSE LIVRE", AMARELO))
        print(linha())
        print()
        print(f"  A resposta certa era {resultado.letra_alt_correta}) {resultado.texto_alt_correta}")
        print(f"  Você ganhou {resultado.pontos_ganhos} pontos (sem bônus de tempo).")
    print(f"  Pontuação: {resultado.pontuacao}")
    pausar()
    return buscar_estado(stub, estado.id_partida)



def main():
    ap = argparse.ArgumentParser(description="Cliente")
    ap.add_argument("--endereco", default="127.0.0.1:50050",
                    help="endereço do balanceador (padrão: 127.0.0.1:50050)")
    ap.add_argument("--seguro", action="store_true",
                    help="usa TLS. necessário com o ngrok, porta 443")
    args = ap.parse_args()

    if args.seguro:
        canal = grpc.secure_channel(args.endereco, grpc.ssl_channel_credentials())
    else:
        canal = grpc.insecure_channel(args.endereco)
    stub = pb_grpc.QuizStub(canal)

    try:
        tela_inicial(stub)
    except (KeyboardInterrupt, EOFError):
        print("\nAté mais!")
    finally:
        canal.close()


if __name__ == "__main__":
    main()
