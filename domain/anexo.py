from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class Anexo:
    """
    Entidade de Domínio para Anexos.
    Representa os metadados de um recibo.
    """
    id_transacao: str
    nome_arquivo: str      # Nome original do arquivo (ex: "recibo.jpg")
    caminho_storage: str   # Caminho interno (ex: "uploads/uuid.jpg")
    tipo_mime: str         # ex: "image/jpeg"
    tamanho_bytes: int
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_upload: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """ Validações de regras de negócio da entidade. """
        if not self.id_transacao:
            raise ValueError("Anexo deve estar associado a uma transação.")
        if not self.nome_arquivo or self.nome_arquivo.strip() == "":
            raise ValueError("Nome do arquivo é obrigatório.")
        if self.tamanho_bytes <= 0:
            raise ValueError("Tamanho do arquivo deve ser positivo.")