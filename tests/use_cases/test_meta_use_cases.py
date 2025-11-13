from datetime import datetime, timedelta
from use_cases.meta_use_cases import CriarMeta, MetaCalculator
from use_cases.repository_interfaces import IMetaRepository
from domain.meta import Meta


class FakeMetaRepository(IMetaRepository):
    def __init__(self):
        self.metas = []

    def add(self, meta: Meta) -> None:
        self.metas.append(meta)

    def get_by_usuario(self, id_usuario: str):
        return [m for m in self.metas if m.id_usuario == id_usuario]

    def update(self, meta: Meta) -> None:
        for idx, item in enumerate(self.metas):
            if item.id == meta.id:
                self.metas[idx] = meta
                return

    def get_by_id(self, id_meta: str) -> Meta | None:
        for meta in self.metas:
            if meta.id == id_meta:
                return meta
        return None


def test_criar_meta_sucesso_calculo_mensal():
    repo = FakeMetaRepository()
    use_case = CriarMeta(repo)
    prazo = datetime.now() + timedelta(days=90)  # ~3 meses
    resultado = use_case.execute(
        id_usuario="u1",
        nome="Férias na Europa",
        valor_alvo=1200,
        data_limite=prazo
    )
    # Mensal deve ficar aproximadamente 400 (1200/3) com arredondamento
    mensal = resultado["sugestoes"]["mensal"]
    assert 390 <= mensal <= 410
    assert resultado["nome"] == "Férias na Europa"


def test_criar_meta_falha_prazo_obrigatorio():
    repo = FakeMetaRepository()
    use_case = CriarMeta(repo)
    try:
        use_case.execute(id_usuario="u1", nome="Meta X", valor_alvo=1000, data_limite=None)
        assert False, "Deveria lançar erro de prazo obrigatório"
    except ValueError as e:
        assert "Data Final" in str(e)


def test_criar_meta_falha_valor_invalido():
    repo = FakeMetaRepository()
    use_case = CriarMeta(repo)
    for valor in [None, "abc", 0, -10]:
        try:
            use_case.execute(id_usuario="u1", nome="Meta X", valor_alvo=valor, data_limite=datetime.now()+timedelta(days=10))
            assert False, f"Deveria falhar para valor {valor}"
        except ValueError:
            pass


def test_criar_meta_falha_prazo_passado():
    repo = FakeMetaRepository()
    use_case = CriarMeta(repo)
    try:
        use_case.execute(id_usuario="u1", nome="Meta X", valor_alvo=500, data_limite=datetime.now()-timedelta(days=1))
        assert False, "Deveria falhar para data passada"
    except ValueError as e:
        assert "futura" in str(e)
