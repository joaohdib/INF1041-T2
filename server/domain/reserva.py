from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Reserva:
    """Entidade de domínio que representa um aporte reservado para uma meta."""

    id_usuario: str
    id_meta: str
    valor: float
    id_transacao: str | None = None
    observacao: str | None = None
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise ValueError("Valor da reserva deve ser positivo.")

    def atualizar_valor(self, novo_valor: float) -> None:
        """Atualiza o valor reservado e marca o timestamp de atualização."""
        if novo_valor <= 0:
            raise ValueError("Valor da reserva deve ser positivo.")
        self.valor = novo_valor
        self.atualizado_em = datetime.utcnow()
