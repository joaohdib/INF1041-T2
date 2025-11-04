from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class TipoTransacao(Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"

class StatusTransacao(Enum):
    PENDENTE = "PENDENTE"
    PROCESSADO = "PROCESSADO"

@dataclass
class Transacao:
    valor: float
    tipo: TipoTransacao
    data: datetime
    status: StatusTransacao
    id_usuario: str # Assumindo que temos um usuário
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    descricao: str | None = None
    id_categoria: str | None = None
    id_perfil: str | None = None
    id_projeto: str | None = None
    
    def __post_init__(self):
        if self.valor <= 0:
            raise ValueError("O valor da transação deve ser positivo.")
            
    def categorizar(self, id_categoria: str, id_perfil: str):
        """ Aplica categoria e perfil e marca como processada. """
        self.id_categoria = id_categoria
        self.id_perfil = id_perfil
        self.status = StatusTransacao.PROCESSADO