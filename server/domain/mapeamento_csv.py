from dataclasses import dataclass, field
import uuid


@dataclass
class MapeamentoCSV:
    id_usuario: str
    nome: str
    coluna_data: str
    coluna_valor: str
    coluna_descricao: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

