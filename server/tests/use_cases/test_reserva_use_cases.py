import pytest
from datetime import datetime, timedelta

from domain.meta import Meta
from domain.reserva import Reserva
from use_cases.reserva_use_cases import (
    CriarReserva,
    AtualizarReserva,
    ExcluirReserva,
    ListarMetasDisponiveisParaReserva,
)
from use_cases.repository_interfaces import IMetaRepository, IReservaRepository


class FakeMetaRepository(IMetaRepository):
    def __init__(self):
        self.metas: dict[str, Meta] = {}

    def add(self, meta: Meta) -> None:
        self.metas[meta.id] = meta

    def get_by_usuario(self, id_usuario: str):
        return [meta for meta in self.metas.values() if meta.id_usuario == id_usuario]

    def update(self, meta: Meta) -> None:
        self.metas[meta.id] = meta

    def get_by_id(self, id_meta: str):
        return self.metas.get(id_meta)


class FakeReservaRepository(IReservaRepository):
    def __init__(self):
        self.reservas: dict[str, Reserva] = {}

    def add(self, reserva: Reserva) -> None:
        self.reservas[reserva.id] = reserva

    def update(self, reserva: Reserva) -> None:
        self.reservas[reserva.id] = reserva

    def delete(self, reserva_id: str) -> None:
        self.reservas.pop(reserva_id, None)

    def get_by_id(self, reserva_id: str):
        return self.reservas.get(reserva_id)

    def get_by_meta(self, id_meta: str):
        return [reserva for reserva in self.reservas.values() if reserva.id_meta == id_meta]

    def get_total_by_meta(self, id_meta: str) -> float:
        return sum(reserva.valor for reserva in self.get_by_meta(id_meta))


def criar_meta(id_usuario: str, valor_alvo: float, valor_inicial: float = 0.0) -> Meta:
    meta = Meta(
        id_usuario=id_usuario,
        nome="Viagem",
        valor_alvo=valor_alvo,
        valor_atual=valor_inicial,
        data_limite=datetime.now() + timedelta(days=90),
    )
    return meta


def test_criar_reserva_atualiza_progresso():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 1000.0, valor_inicial=100.0)
    meta_repo.add(meta)

    reserva_existente = Reserva(id_usuario="user1", id_meta=meta.id, valor=100.0)
    reserva_repo.add(reserva_existente)

    use_case = CriarReserva(reserva_repo, meta_repo)
    resposta = use_case.execute(id_usuario="user1", id_meta=meta.id, valor=50.0)

    assert resposta["meta"]["valor_atual"] == pytest.approx(150.0)
    assert meta_repo.get_by_id(meta.id).valor_atual == pytest.approx(150.0)


def test_criar_reserva_conclui_meta():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 1000.0, valor_inicial=980.0)
    meta_repo.add(meta)
    reserva_repo.add(Reserva(id_usuario="user1", id_meta=meta.id, valor=980.0))

    use_case = CriarReserva(reserva_repo, meta_repo)
    resposta = use_case.execute(id_usuario="user1", id_meta=meta.id, valor=50.0)

    assert resposta["meta"]["esta_concluida"] is True
    assert "mensagem" in resposta
    assert meta_repo.get_by_id(meta.id).esta_concluida()


def test_atualizar_reserva_recalcula_progresso():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 500.0, valor_inicial=150.0)
    meta_repo.add(meta)

    reserva = Reserva(id_usuario="user1", id_meta=meta.id, valor=50.0)
    reserva_repo.add(reserva)
    reserva_repo.add(Reserva(id_usuario="user1", id_meta=meta.id, valor=100.0))

    use_case = AtualizarReserva(reserva_repo, meta_repo)
    resposta = use_case.execute(id_usuario="user1", id_reserva=reserva.id, novo_valor=20.0)

    assert resposta["meta"]["valor_atual"] == pytest.approx(120.0)
    assert meta_repo.get_by_id(meta.id).valor_atual == pytest.approx(120.0)


def test_excluir_reserva_recalcula_progresso():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 500.0, valor_inicial=150.0)
    meta_repo.add(meta)

    reserva = Reserva(id_usuario="user1", id_meta=meta.id, valor=50.0)
    reserva_repo.add(reserva)
    reserva_repo.add(Reserva(id_usuario="user1", id_meta=meta.id, valor=100.0))

    use_case = ExcluirReserva(reserva_repo, meta_repo)
    resposta = use_case.execute(id_usuario="user1", id_reserva=reserva.id)

    assert resposta["meta"]["valor_atual"] == pytest.approx(100.0)
    assert meta_repo.get_by_id(meta.id).valor_atual == pytest.approx(100.0)


def test_nao_criar_reserva_para_meta_concluida():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 500.0, valor_inicial=500.0)
    meta_repo.add(meta)
    reserva_repo.add(Reserva(id_usuario="user1", id_meta=meta.id, valor=500.0))

    use_case = CriarReserva(reserva_repo, meta_repo)

    with pytest.raises(ValueError):
        use_case.execute(id_usuario="user1", id_meta=meta.id, valor=10.0)


def test_listar_metas_disponiveis_sem_resultado():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 500.0, valor_inicial=500.0)
    meta_repo.add(meta)

    caso_uso = ListarMetasDisponiveisParaReserva(meta_repo)
    resposta = caso_uso.execute(id_usuario="user1")

    assert resposta["metas"] == []
    assert "mensagem" in resposta


def test_atualizar_reserva_verifica_permissao():
    meta_repo = FakeMetaRepository()
    reserva_repo = FakeReservaRepository()

    meta = criar_meta("user1", 500.0, valor_inicial=50.0)
    meta_repo.add(meta)

    reserva = Reserva(id_usuario="user1", id_meta=meta.id, valor=50.0)
    reserva_repo.add(reserva)

    use_case = AtualizarReserva(reserva_repo, meta_repo)

    with pytest.raises(PermissionError):
        use_case.execute(id_usuario="user2", id_reserva=reserva.id, novo_valor=20.0)
