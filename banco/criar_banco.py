"""
Uso:
    python banco/criar_banco.py                 # cria banco/quiz.db
    python banco/criar_banco.py --banco teste.db

Faz o mesmo que os comandos do sqlite3:
    sqlite3 banco/quiz.db ".read banco/schema.sql"
    sqlite3 banco/quiz.db ".read banco/perguntas.sql"

"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Cria o quiz.db a partir dos arquivos .sql")
    ap.add_argument("--banco", type=Path, default=PASTA / "quiz.db")
    args = ap.parse_args()

    con = sqlite3.connect(args.banco)
    con.execute("PRAGMA foreign_keys = ON")
    for nome in ("schema.sql", "perguntas.sql"):
        con.executescript((PASTA / nome).read_text(encoding="utf-8"))

    por_nivel = dict(con.execute("SELECT nivel, count(*) FROM pergunta GROUP BY nivel"))
    con.close()

    print(f"Banco: {args.banco.resolve()}")
    for nivel in ("facil", "medio", "dificil", "final"):
        print(f"  {nivel:<8} {por_nivel.get(nivel, 0):>3} perguntas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
