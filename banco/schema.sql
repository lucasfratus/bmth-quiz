-- Banco do Show do Horizonte (SQLite 3)
--
-- Convenções
--   * Datas em INTEGER: milissegundos desde 01/01/1970 UTC (epoch em ms).
--   * Valores de domínio sem acento e em minúsculas: 'facil', 'andamento', 'meio_a_meio'.
--   * Toda conexão precisa ligar as chaves estrangeiras, o SQLite vem com elas desligadas:
--       PRAGMA foreign_keys = ON;

-- WAL (write-ahead log): leitores não bloqueiam o escritor. Ajuda quando os
-- três servidores abrem o mesmo arquivo. A configuração fica gravada no arquivo.
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS pergunta (
  id          INTEGER PRIMARY KEY,
  nivel       TEXT NOT NULL CHECK (nivel IN ('facil', 'medio', 'dificil', 'final')),
  enunciado   TEXT NOT NULL UNIQUE,  -- permite rodar a carga de novo sem duplicar
  alt_a       TEXT NOT NULL,
  alt_b       TEXT NOT NULL,
  alt_c       TEXT NOT NULL,
  alt_d       TEXT NOT NULL,
  alt_correta TEXT NOT NULL CHECK (alt_correta IN ('A', 'B', 'C', 'D'))
);

CREATE INDEX IF NOT EXISTS idx_pergunta_nivel ON pergunta (nivel);

CREATE TABLE IF NOT EXISTS jogador (
  id        INTEGER PRIMARY KEY,
  nickname  TEXT    NOT NULL UNIQUE COLLATE NOCASE,  -- 'Lucas' e 'lucas' contam como o mesmo
  criado_em INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS jogo (
  id            INTEGER PRIMARY KEY,
  jogador_id    INTEGER NOT NULL REFERENCES jogador (id),
  status        TEXT    NOT NULL DEFAULT 'andamento'
                        CHECK (status IN ('andamento', 'vitoria', 'derrota')),
  ordem_atual   INTEGER NOT NULL DEFAULT 1 CHECK (ordem_atual BETWEEN 1 AND 10),
  pontuacao     INTEGER NOT NULL DEFAULT 0 CHECK (pontuacao >= 0),
  usou_meio     INTEGER NOT NULL DEFAULT 0 CHECK (usou_meio IN (0, 1)),
  usou_pulo     INTEGER NOT NULL DEFAULT 0 CHECK (usou_pulo IN (0, 1)),
  usou_passe    INTEGER NOT NULL DEFAULT 0 CHECK (usou_passe IN (0, 1)),
  iniciado_em   INTEGER NOT NULL,
  finalizado_em INTEGER,
  -- partida em andamento não tem data de fim; partida encerrada tem
  CHECK ((status = 'andamento') = (finalizado_em IS NULL))
);

CREATE INDEX IF NOT EXISTS idx_jogo_jogador ON jogo (jogador_id);

-- Índice parcial: só guarda as linhas de vitória, já na ordem do ranking.
CREATE INDEX IF NOT EXISTS idx_jogo_ranking
  ON jogo (pontuacao DESC, finalizado_em) WHERE status = 'vitoria';

CREATE TABLE IF NOT EXISTS acao (
  id          INTEGER PRIMARY KEY,
  jogo_id     INTEGER NOT NULL REFERENCES jogo (id) ON DELETE CASCADE,
  ordem       INTEGER NOT NULL CHECK (ordem BETWEEN 1 AND 10),
  pergunta_id INTEGER NOT NULL REFERENCES pergunta (id),
  tipo        TEXT    NOT NULL
                      CHECK (tipo IN ('exibicao', 'resposta', 'meio_a_meio', 'pulo', 'passe_livre')),
  alternativa TEXT    CHECK (alternativa IN ('A', 'B', 'C', 'D')),
  acertou     INTEGER CHECK (acertou IN (0, 1)),
  eliminadas  TEXT    CHECK (eliminadas GLOB '[ABCD],[ABCD]'),  -- ex.: 'B,D'
  pontos      INTEGER NOT NULL DEFAULT 0 CHECK (pontos >= 0),
  criado_em   INTEGER NOT NULL,

  -- cada tipo preenche só os campos que fazem sentido para ele
  CHECK (CASE tipo
           WHEN 'resposta' THEN alternativa IS NOT NULL AND acertou IS NOT NULL
           ELSE alternativa IS NULL AND acertou IS NULL
         END),
  CHECK ((tipo = 'meio_a_meio') = (eliminadas IS NOT NULL)),
  CHECK (pontos = 0 OR tipo IN ('resposta', 'passe_livre'))
);

CREATE INDEX IF NOT EXISTS idx_acao_jogo ON acao (jogo_id, ordem);

-- Índices únicos parciais: valem só para as linhas que passam no WHERE.
-- O banco recusa o INSERT que quebraria a regra, mesmo que dois servidores
-- tentem ao mesmo tempo (ex.: duplo clique caindo em servidores diferentes).

-- Uma pergunta não aparece duas vezes na mesma partida (o pulo sorteia outra).
CREATE UNIQUE INDEX IF NOT EXISTS uq_acao_exibicao
  ON acao (jogo_id, pergunta_id) WHERE tipo = 'exibicao';

-- Cada posição da partida é decidida uma vez: ou por resposta, ou por passe livre.
CREATE UNIQUE INDEX IF NOT EXISTS uq_acao_decisao
  ON acao (jogo_id, ordem) WHERE tipo IN ('resposta', 'passe_livre');

-- Cada ajuda uma vez por partida.
CREATE UNIQUE INDEX IF NOT EXISTS uq_acao_ajuda
  ON acao (jogo_id, tipo) WHERE tipo IN ('meio_a_meio', 'pulo', 'passe_livre');
