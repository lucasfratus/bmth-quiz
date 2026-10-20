-- Perguntas do Show do Horizonte (48: 12 por nível).
-- Rode depois do schema.sql:
--   sqlite3 quiz.db < banco/schema.sql
--   sqlite3 quiz.db < banco/perguntas.sql
-- No DB Browser for SQLite: aba "Executar SQL", cole o arquivo e execute.
-- Pode rodar de novo: pergunta com o mesmo enunciado é atualizada, não duplicada.

BEGIN;

-- Fácil
INSERT INTO pergunta (nivel, enunciado, alt_a, alt_b, alt_c, alt_d, alt_correta) VALUES
  ('facil', 'Quem é o vocalista do Bring Me the Horizon?',
   'Lee Malia', 'Matt Kean', 'Jordan Fish', 'Oli Sykes', 'D'),
  ('facil', 'A frase que inspirou o nome da banda vem de qual filme?',
   'Piratas do Caribe: A Maldição do Pérola Negra', 'O Senhor dos Anéis: A Sociedade do Anel', 'Harry Potter e a Pedra Filosofal', 'Matrix', 'A'),
  ('facil', 'Em qual cidade inglesa a banda foi formada?',
   'Londres', 'Sheffield', 'Manchester', 'Liverpool', 'B'),
  ('facil', 'Em que ano a banda foi formada?',
   '2001', '2004', '2006', '2008', 'B'),
  ('facil', '"Throne" e "Happy Song" fazem parte de qual álbum?',
   'Sempiternal', 'amo', 'That''s the Spirit', 'Suicide Season', 'C'),
  ('facil', '"Shadow Moses" e "Sleepwalking" fazem parte de qual álbum?',
   'Sempiternal', 'That''s the Spirit', 'Count Your Blessings', 'Post Human: Nex Gen', 'A'),
  ('facil', 'Qual é o primeiro álbum de estúdio da banda?',
   'Suicide Season', 'Sempiternal', 'amo', 'Count Your Blessings', 'D'),
  ('facil', 'Qual álbum de 2019 tem como título uma palavra em português?',
   'Sempiternal', 'amo', 'Suicide Season', 'Count Your Blessings', 'B'),
  ('facil', 'Com qual artista a banda gravou "Obey" (2020)?',
   'YUNGBLUD', 'Machine Gun Kelly', 'Post Malone', 'Oliver Tree', 'A'),
  ('facil', 'Quem é o baterista da banda?',
   'Matt Kean', 'Lee Malia', 'Matt Nicholls', 'Jordan Fish', 'C'),
  ('facil', 'Qual destas músicas faz parte de Post Human: Survival Horror?',
   'Avalanche', 'Medicine', 'Antivist', 'Teardrops', 'D'),
  ('facil', 'Com qual cantor pop a banda gravou uma versão rock de "Bad Habits"?',
   'Harry Styles', 'Justin Bieber', 'Ed Sheeran', 'Shawn Mendes', 'C')
ON CONFLICT (enunciado) DO UPDATE SET
  nivel = excluded.nivel,
  alt_a = excluded.alt_a, alt_b = excluded.alt_b,
  alt_c = excluded.alt_c, alt_d = excluded.alt_d,
  alt_correta = excluded.alt_correta;

-- Médio
INSERT INTO pergunta (nivel, enunciado, alt_a, alt_b, alt_c, alt_d, alt_correta) VALUES
  ('medio', 'Qual integrante, tecladista que entrou na época de Sempiternal, deixou a banda em dezembro de 2023?',
   'Jordan Fish', 'Jona Weinhofen', 'Curtis Ward', 'Matt Kean', 'A'),
  ('medio', 'Qual é o nome da marca de roupas fundada por Oli Sykes?',
   'Killstar', 'Drop Dead', 'Thrasher', 'Supreme', 'B'),
  ('medio', 'Qual música da banda foi lançada no álbum Death Stranding: Timefall, ligado ao jogo de Hideo Kojima?',
   'Obey', '1x1', 'Ludens', 'Teardrops', 'C'),
  ('medio', 'Com qual grupo japonês a banda gravou "Kingslayer"?',
   'ONE OK ROCK', 'Crossfaith', 'X Japan', 'BABYMETAL', 'D'),
  ('medio', 'Em qual casa de shows de Londres a banda gravou um álbum ao vivo com orquestra, em 2016?',
   'Wembley Stadium', 'Royal Albert Hall', 'O2 Arena', 'Brixton Academy', 'B'),
  ('medio', 'Qual música do álbum amo tem um trecho cantado em português?',
   'Medicine', 'In the Dark', 'Mother Tongue', 'Mantra', 'C'),
  ('medio', '"Chelsea Smile" e "Diamonds Aren''t Forever" fazem parte de qual álbum?',
   'Suicide Season', 'Count Your Blessings', 'Sempiternal', 'There Is a Hell...', 'A'),
  ('medio', 'Qual gênero marcou o início da carreira da banda, no álbum Count Your Blessings?',
   'Power metal', 'Grunge', 'Glam metal', 'Deathcore', 'D'),
  ('medio', 'Qual single de 2020, escrito sobre um vírus, ganhou novo significado com a pandemia de COVID-19?',
   'Teardrops', 'Parasite Eve', 'Obey', 'Kingslayer', 'B'),
  ('medio', 'Complete o título do álbum de 2010: "There Is a Hell Believe Me I''ve Seen It. There Is a Heaven..."',
   'Let''s Go There Together.', 'But It''s Not for Us.', 'Let''s Keep It a Secret.', 'I''ve Never Been There.', 'C'),
  ('medio', 'Em que ano foi lançado o álbum Post Human: Nex Gen?',
   '2021', '2022', '2023', '2024', 'D'),
  ('medio', 'Qual música de That''s the Spirit foi lançada como single em 2014, antes de o álbum ser anunciado?',
   'Drown', 'Throne', 'Happy Song', 'Avalanche', 'A')
ON CONFLICT (enunciado) DO UPDATE SET
  nivel = excluded.nivel,
  alt_a = excluded.alt_a, alt_b = excluded.alt_b,
  alt_c = excluded.alt_c, alt_d = excluded.alt_d,
  alt_correta = excluded.alt_correta;

-- Difícil
INSERT INTO pergunta (nivel, enunciado, alt_a, alt_b, alt_c, alt_d, alt_correta) VALUES
  ('dificil', 'Qual cantora participa de "Nihilist Blues"?',
   'Halsey', 'Grimes', 'Billie Eilish', 'Lorde', 'B'),
  ('dificil', 'Qual faixa abre o álbum Sempiternal?',
   'Shadow Moses', 'The House of Wolves', 'Antivist', 'Can You Feel My Heart', 'D'),
  ('dificil', 'Qual vocalista participa de "One Day the Only Butterflies Left Will Be in Your Chest as You March Towards Your Death"?',
   'Amy Lee', 'Lzzy Hale', 'Taylor Momsen', 'Cristina Scabbia', 'A'),
  ('dificil', 'Qual produtor, conhecido por trabalhos com Deftones e Pantera, produziu Sempiternal?',
   'Rick Rubin', 'Ross Robinson', 'Terry Date', 'Bob Rock', 'C'),
  ('dificil', 'O que significa a palavra "Sempiternal"?',
   'Sagrado', 'Eterno', 'Proibido', 'Esquecido', 'B'),
  ('dificil', 'Em qual cidade brasileira foi gravado o clipe de "Mother Tongue"?',
   'Rio de Janeiro', 'Curitiba', 'São Paulo', 'Florianópolis', 'C'),
  ('dificil', 'Em 2022, a banda foi headliner pela primeira vez de qual festival britânico, ao lado do Arctic Monkeys?',
   'Glastonbury', 'Download Festival', 'Isle of Wight', 'Reading & Leeds', 'D'),
  ('dificil', 'Qual prêmio a banda venceu no BRIT Awards de 2024?',
   'Melhor Grupo Britânico', 'Melhor Artista de Rock/Alternativo', 'Álbum do Ano', 'Revelação Britânica', 'B'),
  ('dificil', 'Por qual música a banda foi indicada ao Grammy de Melhor Canção de Rock, em 2019?',
   'Mantra', 'Medicine', 'Throne', 'Parasite Eve', 'A'),
  ('dificil', 'Qual cantora participa de "Crucify Me" e "Don''t Go"?',
   'Avril Lavigne', 'Hayley Williams', 'Lights', 'Lzzy Hale', 'C'),
  ('dificil', 'Qual foi o primeiro álbum da banda a chegar ao 1º lugar no Reino Unido?',
   'amo', 'That''s the Spirit', 'Sempiternal', 'Post Human: Survival Horror', 'A'),
  ('dificil', 'Qual integrante original deixou a banda em 2009?',
   'Jona Weinhofen', 'Matt Kean', 'Jordan Fish', 'Curtis Ward', 'D')
ON CONFLICT (enunciado) DO UPDATE SET
  nivel = excluded.nivel,
  alt_a = excluded.alt_a, alt_b = excluded.alt_b,
  alt_c = excluded.alt_c, alt_d = excluded.alt_d,
  alt_correta = excluded.alt_correta;

-- Final
INSERT INTO pergunta (nivel, enunciado, alt_a, alt_b, alt_c, alt_d, alt_correta) VALUES
  ('final', 'Qual é o nome do primeiro EP da banda, lançado em 2004?',
   'Diamonds Aren''t Forever', 'This Is What the Edge of Your Seat Was Made For', 'Hospital for Souls', 'Count Your Blessings', 'B'),
  ('final', 'Qual produtor trabalhou nos álbuns Suicide Season e There Is a Hell...?',
   'Terry Date', 'Max Martin', 'Jens Bogren', 'Fredrik Nordström', 'D'),
  ('final', 'Qual orquestra acompanhou a banda no show do Royal Albert Hall, em 2016?',
   'London Symphony Orchestra', 'Parallax Orchestra', 'Royal Philharmonic Orchestra', 'BBC Concert Orchestra', 'B'),
  ('final', 'Qual faixa do álbum amo conta com a participação do beatboxer Rahzel?',
   'Ouch', 'Fresh Bruises', 'Heavy Metal', 'Sugar Honey Ice & Tea', 'C'),
  ('final', 'A que se refere o nome da música "Ludens"?',
   'Ao protagonista de Death Stranding', 'Ao mascote da Kojima Productions', 'A uma cidade de Death Stranding', 'A um chefe de Metal Gear Solid', 'B'),
  ('final', 'Qual banda impediu That''s the Spirit de estrear em 1º lugar no Reino Unido?',
   'Stereophonics', 'Muse', 'Coldplay', 'Arctic Monkeys', 'A'),
  ('final', 'Qual símbolo geométrico estampa a capa de Sempiternal?',
   'Cubo de Metatron', 'Espiral de Fibonacci', 'Pentagrama', 'Flor da Vida', 'D'),
  ('final', 'Quantos lançamentos estavam previstos originalmente para a série Post Human?',
   '2', '3', '4', '5', 'C'),
  ('final', 'Qual DJ e produtor participou do álbum de remixes Suicide Season: Cut Up!?',
   'Skrillex', 'deadmau5', 'Diplo', 'Calvin Harris', 'A'),
  ('final', 'Qual banda participa de "A Bullet w/ My Name On", do álbum Post Human: Nex Gen?',
   'Architects', 'While She Sleeps', 'Underoath', 'Bleeding Through', 'C'),
  ('final', 'Em qual cidade inglesa nasceu o vocalista Oli Sykes?',
   'Sheffield', 'Manchester', 'Leeds', 'Ashford', 'D'),
  ('final', 'Qual música, lançada em 2021, foi o primeiro single de Post Human: Nex Gen?',
   'Die4U', 'Strangers', 'Lost', 'Kool-Aid', 'A')
ON CONFLICT (enunciado) DO UPDATE SET
  nivel = excluded.nivel,
  alt_a = excluded.alt_a, alt_b = excluded.alt_b,
  alt_c = excluded.alt_c, alt_d = excluded.alt_d,
  alt_correta = excluded.alt_correta;

COMMIT;
