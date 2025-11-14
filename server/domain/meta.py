from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Meta:
    """Entidade de Domínio para Metas Financeiras.

    Representa um objetivo financeiro (ex: "Férias na Europa") que possui:
    - valor alvo total (valor_alvo)
    - valor acumulado até o momento (valor_atual)
    - data limite para atingir o objetivo (data_limite)
    - vínculo opcional a um Perfil Financeiro (id_perfil)
    """
    id_usuario: str
    nome: str
    valor_alvo: float
    data_limite: datetime
    id_perfil: str | None = None
    valor_atual: float = 0.0
    concluida_em: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if not self.nome or self.nome.strip() == "":
            raise ValueError("Nome da meta é obrigatório.")
        if self.valor_alvo <= 0:
            raise ValueError("Valor alvo deve ser maior que zero.")
        if self.data_limite <= datetime.now():
            raise ValueError("Data limite deve ser futura.")
        if self.valor_atual < 0:
            raise ValueError("Valor atual não pode ser negativo.")
        self._atualizar_status()

    def registrar_aporte(self, valor: float):
        """Incrementa o valor atual da meta com validação."""
        if valor <= 0:
            raise ValueError("Valor do aporte deve ser positivo.")
        self.valor_atual += valor
        self._atualizar_status()

    def atualizar_valor_atual(self, novo_valor: float) -> None:
        """Atualiza o total reservado para a meta recalculando o status."""
        if novo_valor < 0:
            raise ValueError("Valor atual da meta não pode ser negativo.")
        self.valor_atual = novo_valor
        self._atualizar_status()

    def esta_concluida(self) -> bool:
        return self.concluida_em is not None

    def _atualizar_status(self) -> None:
        if self.valor_atual >= self.valor_alvo:
            if self.concluida_em is None:
                self.concluida_em = datetime.now()
        else:
            self.concluida_em = None

    def progresso_percentual(self) -> float:
        return round((self.valor_atual / self.valor_alvo) * 100, 2)
