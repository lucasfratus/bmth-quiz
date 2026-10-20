from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNDEFINED: _ClassVar[Status]
    EM_ANDAMENTO: _ClassVar[Status]
    DERROTA: _ClassVar[Status]
    VITORIA: _ClassVar[Status]

class TipoAjuda(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AJUDA_UNDEFINED: _ClassVar[TipoAjuda]
    MEIO_A_MEIO: _ClassVar[TipoAjuda]
    PULO: _ClassVar[TipoAjuda]
    PASSE_LIVRE: _ClassVar[TipoAjuda]
STATUS_UNDEFINED: Status
EM_ANDAMENTO: Status
DERROTA: Status
VITORIA: Status
AJUDA_UNDEFINED: TipoAjuda
MEIO_A_MEIO: TipoAjuda
PULO: TipoAjuda
PASSE_LIVRE: TipoAjuda

class ListarRankingRequest(_message.Message):
    __slots__ = ("limite",)
    LIMITE_FIELD_NUMBER: _ClassVar[int]
    limite: int
    def __init__(self, limite: _Optional[int] = ...) -> None: ...

class EntradaRanking(_message.Message):
    __slots__ = ("nickname", "pontuacao", "data")
    NICKNAME_FIELD_NUMBER: _ClassVar[int]
    PONTUACAO_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    nickname: str
    pontuacao: int
    data: str
    def __init__(self, nickname: _Optional[str] = ..., pontuacao: _Optional[int] = ..., data: _Optional[str] = ...) -> None: ...

class ListarRankingResponse(_message.Message):
    __slots__ = ("entradas",)
    ENTRADAS_FIELD_NUMBER: _ClassVar[int]
    entradas: _containers.RepeatedCompositeFieldContainer[EntradaRanking]
    def __init__(self, entradas: _Optional[_Iterable[_Union[EntradaRanking, _Mapping]]] = ...) -> None: ...

class IniciarPartidaRequest(_message.Message):
    __slots__ = ("nickname",)
    NICKNAME_FIELD_NUMBER: _ClassVar[int]
    nickname: str
    def __init__(self, nickname: _Optional[str] = ...) -> None: ...

class PartidaRequest(_message.Message):
    __slots__ = ("id_partida",)
    ID_PARTIDA_FIELD_NUMBER: _ClassVar[int]
    id_partida: int
    def __init__(self, id_partida: _Optional[int] = ...) -> None: ...

class Alternativa(_message.Message):
    __slots__ = ("letra", "texto")
    LETRA_FIELD_NUMBER: _ClassVar[int]
    TEXTO_FIELD_NUMBER: _ClassVar[int]
    letra: str
    texto: str
    def __init__(self, letra: _Optional[str] = ..., texto: _Optional[str] = ...) -> None: ...

class Ajuda(_message.Message):
    __slots__ = ("tipo", "nome", "descricao", "esta_disponivel", "motivo")
    TIPO_FIELD_NUMBER: _ClassVar[int]
    NOME_FIELD_NUMBER: _ClassVar[int]
    DESCRICAO_FIELD_NUMBER: _ClassVar[int]
    ESTA_DISPONIVEL_FIELD_NUMBER: _ClassVar[int]
    MOTIVO_FIELD_NUMBER: _ClassVar[int]
    tipo: TipoAjuda
    nome: str
    descricao: str
    esta_disponivel: bool
    motivo: str
    def __init__(self, tipo: _Optional[_Union[TipoAjuda, str]] = ..., nome: _Optional[str] = ..., descricao: _Optional[str] = ..., esta_disponivel: _Optional[bool] = ..., motivo: _Optional[str] = ...) -> None: ...

class EstadoPartida(_message.Message):
    __slots__ = ("id_partida", "nickname", "status", "nivel", "ordem", "total", "enunciado", "alternativas", "eliminadas", "pontuacao", "pontos_base", "bonus_maximo", "janela_bonus_s", "segundos_decorridos", "ajudas", "niveis_da_partida")
    ID_PARTIDA_FIELD_NUMBER: _ClassVar[int]
    NICKNAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NIVEL_FIELD_NUMBER: _ClassVar[int]
    ORDEM_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    ENUNCIADO_FIELD_NUMBER: _ClassVar[int]
    ALTERNATIVAS_FIELD_NUMBER: _ClassVar[int]
    ELIMINADAS_FIELD_NUMBER: _ClassVar[int]
    PONTUACAO_FIELD_NUMBER: _ClassVar[int]
    PONTOS_BASE_FIELD_NUMBER: _ClassVar[int]
    BONUS_MAXIMO_FIELD_NUMBER: _ClassVar[int]
    JANELA_BONUS_S_FIELD_NUMBER: _ClassVar[int]
    SEGUNDOS_DECORRIDOS_FIELD_NUMBER: _ClassVar[int]
    AJUDAS_FIELD_NUMBER: _ClassVar[int]
    NIVEIS_DA_PARTIDA_FIELD_NUMBER: _ClassVar[int]
    id_partida: int
    nickname: str
    status: Status
    nivel: str
    ordem: int
    total: int
    enunciado: str
    alternativas: _containers.RepeatedCompositeFieldContainer[Alternativa]
    eliminadas: _containers.RepeatedScalarFieldContainer[str]
    pontuacao: int
    pontos_base: int
    bonus_maximo: int
    janela_bonus_s: int
    segundos_decorridos: float
    ajudas: _containers.RepeatedCompositeFieldContainer[Ajuda]
    niveis_da_partida: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id_partida: _Optional[int] = ..., nickname: _Optional[str] = ..., status: _Optional[_Union[Status, str]] = ..., nivel: _Optional[str] = ..., ordem: _Optional[int] = ..., total: _Optional[int] = ..., enunciado: _Optional[str] = ..., alternativas: _Optional[_Iterable[_Union[Alternativa, _Mapping]]] = ..., eliminadas: _Optional[_Iterable[str]] = ..., pontuacao: _Optional[int] = ..., pontos_base: _Optional[int] = ..., bonus_maximo: _Optional[int] = ..., janela_bonus_s: _Optional[int] = ..., segundos_decorridos: _Optional[float] = ..., ajudas: _Optional[_Iterable[_Union[Ajuda, _Mapping]]] = ..., niveis_da_partida: _Optional[_Iterable[str]] = ...) -> None: ...

class ResponderRequest(_message.Message):
    __slots__ = ("id_partida", "letra")
    ID_PARTIDA_FIELD_NUMBER: _ClassVar[int]
    LETRA_FIELD_NUMBER: _ClassVar[int]
    id_partida: int
    letra: str
    def __init__(self, id_partida: _Optional[int] = ..., letra: _Optional[str] = ...) -> None: ...

class ResultadoResposta(_message.Message):
    __slots__ = ("correta", "letra_alt_escolhida", "texto_alt_escolhida", "letra_alt_correta", "texto_alt_correta", "pontos_ganhos", "bonus", "pontuacao", "status", "nivel", "ordem", "total", "enunciado", "posicao_ranking")
    CORRETA_FIELD_NUMBER: _ClassVar[int]
    LETRA_ALT_ESCOLHIDA_FIELD_NUMBER: _ClassVar[int]
    TEXTO_ALT_ESCOLHIDA_FIELD_NUMBER: _ClassVar[int]
    LETRA_ALT_CORRETA_FIELD_NUMBER: _ClassVar[int]
    TEXTO_ALT_CORRETA_FIELD_NUMBER: _ClassVar[int]
    PONTOS_GANHOS_FIELD_NUMBER: _ClassVar[int]
    BONUS_FIELD_NUMBER: _ClassVar[int]
    PONTUACAO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NIVEL_FIELD_NUMBER: _ClassVar[int]
    ORDEM_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    ENUNCIADO_FIELD_NUMBER: _ClassVar[int]
    POSICAO_RANKING_FIELD_NUMBER: _ClassVar[int]
    correta: bool
    letra_alt_escolhida: str
    texto_alt_escolhida: str
    letra_alt_correta: str
    texto_alt_correta: str
    pontos_ganhos: int
    bonus: int
    pontuacao: int
    status: Status
    nivel: str
    ordem: int
    total: int
    enunciado: str
    posicao_ranking: int
    def __init__(self, correta: _Optional[bool] = ..., letra_alt_escolhida: _Optional[str] = ..., texto_alt_escolhida: _Optional[str] = ..., letra_alt_correta: _Optional[str] = ..., texto_alt_correta: _Optional[str] = ..., pontos_ganhos: _Optional[int] = ..., bonus: _Optional[int] = ..., pontuacao: _Optional[int] = ..., status: _Optional[_Union[Status, str]] = ..., nivel: _Optional[str] = ..., ordem: _Optional[int] = ..., total: _Optional[int] = ..., enunciado: _Optional[str] = ..., posicao_ranking: _Optional[int] = ...) -> None: ...

class UsarAjudaRequest(_message.Message):
    __slots__ = ("id_partida", "ajuda")
    ID_PARTIDA_FIELD_NUMBER: _ClassVar[int]
    AJUDA_FIELD_NUMBER: _ClassVar[int]
    id_partida: int
    ajuda: TipoAjuda
    def __init__(self, id_partida: _Optional[int] = ..., ajuda: _Optional[_Union[TipoAjuda, str]] = ...) -> None: ...

class ResultadoAjuda(_message.Message):
    __slots__ = ("tipo", "ordem", "total", "nivel", "eliminadas", "enunciado_pulado", "letra_alt_correta", "texto_alt_correta", "pontos_ganhos", "pontuacao")
    TIPO_FIELD_NUMBER: _ClassVar[int]
    ORDEM_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    NIVEL_FIELD_NUMBER: _ClassVar[int]
    ELIMINADAS_FIELD_NUMBER: _ClassVar[int]
    ENUNCIADO_PULADO_FIELD_NUMBER: _ClassVar[int]
    LETRA_ALT_CORRETA_FIELD_NUMBER: _ClassVar[int]
    TEXTO_ALT_CORRETA_FIELD_NUMBER: _ClassVar[int]
    PONTOS_GANHOS_FIELD_NUMBER: _ClassVar[int]
    PONTUACAO_FIELD_NUMBER: _ClassVar[int]
    tipo: TipoAjuda
    ordem: int
    total: int
    nivel: str
    eliminadas: _containers.RepeatedScalarFieldContainer[str]
    enunciado_pulado: str
    letra_alt_correta: str
    texto_alt_correta: str
    pontos_ganhos: int
    pontuacao: int
    def __init__(self, tipo: _Optional[_Union[TipoAjuda, str]] = ..., ordem: _Optional[int] = ..., total: _Optional[int] = ..., nivel: _Optional[str] = ..., eliminadas: _Optional[_Iterable[str]] = ..., enunciado_pulado: _Optional[str] = ..., letra_alt_correta: _Optional[str] = ..., texto_alt_correta: _Optional[str] = ..., pontos_ganhos: _Optional[int] = ..., pontuacao: _Optional[int] = ...) -> None: ...
