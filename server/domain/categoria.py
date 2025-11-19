from dataclasses import dataclass

from domain.transacao import TipoTransacao


@dataclass
class Categoria:
    id: str
    nome: str
    id_usuario: str
    tipo: TipoTransacao
