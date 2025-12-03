import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StatusMeta(Enum):
    ATIVA = "ATIVA"
    PAUSADA = "PAUSADA"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


@dataclass
class Meta:
    """Entidade de Domínio para Metas Financeiras."""

    id_usuario: str
    nome: str
    valor_alvo: float
    data_limite: datetime
    id_perfil: str | None = None
    valor_atual: float = 0.0
    concluida_em: datetime | None = None
    finalizada_em: datetime | None = None
    status: StatusMeta = StatusMeta.ATIVA
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if not self.nome or self.nome.strip() == "":
            raise ValueError("Nome da meta é obrigatório.")
        if self.valor_alvo <= 0:
            raise ValueError("Valor alvo deve ser maior que zero.")
        if self.data_limite.date() <= datetime.now().date():
            raise ValueError("Data limite deve ser futura.")
        if self.valor_atual < 0:
            raise ValueError("Valor atual não pode ser negativo.")
        self._atualizar_status()

    def editar(self, nome: str, valor_alvo: float, data_limite: datetime) -> None:
        """Edita os dados básicos da meta."""
        if self.status == StatusMeta.CONCLUIDA:
            raise ValueError("Não é possível editar uma meta concluída.")

        self.nome = nome
        self.valor_alvo = valor_alvo
        self.data_limite = data_limite
        self._atualizar_status()

    def pausar(self) -> None:
        """Pausa a meta."""
        if self.status == StatusMeta.CONCLUIDA:
            raise ValueError("Não é possível pausar uma meta concluída.")
        self.status = StatusMeta.PAUSADA

    def retomar(self) -> None:
        """Retoma uma meta pausada."""
        if self.status != StatusMeta.PAUSADA:
            raise ValueError("Só é possível retomar metas pausadas.")
        self.status = StatusMeta.ATIVA

    def cancelar(self) -> None:
        """Cancela a meta."""
        if self.status == StatusMeta.CONCLUIDA:
            raise ValueError("Não é possível cancelar uma meta concluída.")
        self.status = StatusMeta.CANCELADA

    def concluir_manual(self):
        """Marca a meta como concluída manualmente."""
        if self.concluida_em is None:
            self.concluida_em = datetime.now()
            self.status = StatusMeta.CONCLUIDA

    def finalizar(self):
        """Marca a meta como finalizada após registro de uso."""
        if self.finalizada_em is None:
            self.finalizada_em = datetime.now()

    def registrar_aporte(self, valor: float):
        """Incrementa o valor atual da meta com validação."""
        if self.status != StatusMeta.ATIVA:
            raise ValueError(
                "Só é possível registrar aportes em metas ativas.")
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

    def esta_finalizada(self) -> bool:
        return self.finalizada_em is not None

    def _atualizar_status(self) -> None:
        # Se a meta já foi concluída (manual ou automática), não desfaz conclusão
        if self.status == StatusMeta.CONCLUIDA and self.concluida_em:
            return

        if self.valor_atual >= self.valor_alvo:
            if self.concluida_em is None:
                self.concluida_em = datetime.now()
                self.status = StatusMeta.CONCLUIDA
        else:
            if self.status == StatusMeta.CONCLUIDA:
                self.status = StatusMeta.ATIVA

    def progresso_percentual(self) -> float:
        return round((self.valor_atual / self.valor_alvo) * 100, 2)
