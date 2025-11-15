from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Meta:
    id_usuario: str
    nome: str
    valor_alvo: float
    data_limite: datetime
    id_perfil: str | None = None
    valor_atual: float = 0.0
    concluida_em: datetime | None = None
    finalizada_em: datetime | None = None
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

    def concluir_manual(self):
        """Marca a meta como concluída manualmente."""
        if self.concluida_em is None:
            self.concluida_em = datetime.now()
            print(f"DEBUG: Meta {self.id} concluída em {self.concluida_em}")

    def finalizar(self):
        """Marca a meta como finalizada após registro de uso."""
        if self.finalizada_em is None:
            self.finalizada_em = datetime.now()
            print(f"DEBUG: Meta {self.id} finalizada em {self.finalizada_em}")

    def registrar_aporte(self, valor: float):
        if valor <= 0:
            raise ValueError("Valor do aporte deve ser positivo.")
        self.valor_atual += valor
        self._atualizar_status()

    def atualizar_valor_atual(self, novo_valor: float) -> None:
        if novo_valor < 0:
            raise ValueError("Valor atual da meta não pode ser negativo.")
        self.valor_atual = novo_valor
        self._atualizar_status()

    def esta_concluida(self) -> bool:
        return self.concluida_em is not None

    def esta_finalizada(self) -> bool:
        return self.finalizada_em is not None

    def _atualizar_status(self) -> None:
        if self.valor_atual >= self.valor_alvo:
            if self.concluida_em is None:
                self.concluida_em = datetime.now()
                print(f"DEBUG: Meta {self.id} concluída automaticamente")
        else:
            self.concluida_em = None

    def progresso_percentual(self) -> float:
        return round((self.valor_atual / self.valor_alvo) * 100, 2)