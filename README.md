# Show do Horizonte

Quiz online no estilo "Show do Milhão" com o tema **Bring Me the Horizon**. Trabalho prático de Sistemas Distribuídos

## Arquivos

| Item | Arquivo(s) |
|---|---|
| Interface do cliente (tela inicial, novo jogo e primeira pergunta) | `cliente.py` (interface de terminal) |
| Balanceador de carga operante (Round-Robin) | `balanceador.py` |
| Servidores operantes | `servidor.py` |
| Banco de dados com as tabelas | `banco/schema.sql`, `banco/perguntas.sql`, `banco/criar_banco.py` |
| Comunicação cliente x balanceador | gRPC, contrato em `proto/quiz.proto` |

O cliente já tem também as telas de ranking, fim de jogo, vencedor e ajudas. Os rpcs `Responder` e `UsarAjuda` ainda não estão implementados (respondem `UNIMPLEMENTED`) no servidor.

## Versão da linguagem e bibliotecas

- **Python 3.13**
- Os arquivos `quiz_pb2*.py` já estão gerados; o comando para gerá-los de novo está no fim deste arquivo.
- **Bibliotecas adicionais** (`requirements.txt`):
  - `grpcio` e `grpcio-tools` (gRPC)
  - `protobuf` (formato das mensagens).
- **SQLite** (banco de dados)
- **ngrok**


## Como executar

Todos os comandos são executados dentro pasta do projeto.

### 1. Ambiente

```bash
python -m venv .venv
source .venv/bin/activate         
pip install -r requirements.txt
```

### 2. Banco de dados

```bash
python banco/criar_banco.py
```

Cria `banco/quiz.db` com as 4 tabelas e as 48 perguntas

Para reiniciar o estado do banco, apague `banco/quiz.db` e rode de novo.

### 3. Servidores e balanceador (execute cada um em terminais diferentes)

```bash
python servidor.py --id 1          # porta 50051
python servidor.py --id 2          # porta 50052
python servidor.py --id 3          # porta 50053
python balanceador.py              # porta 50050
```

### 4. Cliente

Na mesma máquina, se comunicando com o balanceador:

```bash
python cliente.py
```

Pelo ngrok, de outro dispositivo (verifique a próxima seção):

```bash
python cliente.py --endereco SEU-DOMINIO.ngrok-free.dev:443 --seguro
```


### 5. Acesso externo com ngrok
 
**No dispositivo do servidor**, aponte o seu túnel para a porta `50050` (onde o balanceador escuta) usando o protocolo HTTP/2, que o gRPC exige. No arquivo de configuração do ngrok, o endpoint fica:
 
```yaml
endpoints:
  - name: quiz
    url: https://SEU-DOMINIO.ngrok-free.dev
    upstream:
      url: 50050
      protocol: http2
```
 
Com o balanceador rodando, suba o túnel apontando para esse endpoint.
 
**No dispositivo do cliente**, passe o link gerado pelo ngrok no parâmetro `--endereco`, com `:443` no fim e a flag `--seguro` (liga o TLS, que o ngrok exige):
 
```bash
python cliente.py --endereco SEU-DOMINIO.ngrok-free.dev:443 --seguro
```
 
Troque `SEU-DOMINIO.ngrok-free.dev` pelo domínio que o ngrok gerar. Não é necessário alterar o código do projeto.


## Log do balanceador

Para cada requisição recebida, o balanceador acrescenta uma linha em `balanceador.log` (criado ao lado de `balanceador.py`; outro caminho com `--log`):

```
IP/porta cliente; tipo requisicao; horario; servidor atribuido
127.0.0.1:43032; IniciarPartida; 2026-11-07 15:49:53; 127.0.0.1:50052
```

- **tipo requisicao**: o nome do rpc (`ListarRanking`, `IniciarPartida`, `ObterEstado`, `Responder`, `UsarAjuda`).
- **IP/porta cliente**: com o ngrok, quem chega ao balanceador é o agente do ngrok (na própria máquina). Quando o ngrok envia o cabeçalho `x-forwarded-for`, o IP do jogador aparece antes, no formato `IP (via 127.0.0.1:porta)`.
- **servidor atribuido**: o servidor que de fato respondeu. Se um servidor estiver fora do ar, o balanceador tenta o próximo.

## Balanceamento

Round-Robin: as chamadas são entregues aos servidores 1, 2, 3, 1, 2, 3 e assim por diante. O balanceador repassa as mensagens como bytes, sem interpretá-las.

## Banco de dados

O SQLite é utilizado (arquivo em banco/quiz.db). Os 3 servidores abrem o mesmo arquivo. As escritas usam `BEGIN IMMEDIATE`, que reserva a escrita logo no início da transação, para dois servidores não sortearem duas perguntas para a mesma posição.

| Tabela | Conteúdo |
|---|---|
| `pergunta` | banco de questões: nível, enunciado, 4 alternativas e a correta |
| `jogador` | nickname (único, sem diferenciar maiúsculas) |
| `jogo` | estado atual da partida: jogador, status, posição, pontuação, ajudas usadas |
| `acao` | histórico de cada jogo: pergunta exibida, resposta, meio a meio, pulo e passe livre |

## Arquivos

```
cliente.py             interface de terminal
balanceador.py         balanceador Round-Robin com log em arquivo
servidor.py            servidor gRPC (ListarRanking, IniciarPartida, ObterEstado)
testar_servidor.py     chama os rpcs no balanceador ou em um servidor
requirements.txt       bibliotecas
proto/quiz.proto       contrato gRPC
quiz_pb2*.py, .pyi     código gerado a partir do quiz.proto
banco/schema.sql       tabelas
banco/criar_banco.py   cria o banco/quiz.db
```

## Gerar o código gRPC de novo (apenas se necessário)
```bash
python -m grpc_tools.protoc -I proto --python_out=. --pyi_out=. --grpc_python_out=. proto/quiz.proto
```
