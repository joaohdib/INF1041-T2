import pytest
from unittest.mock import MagicMock
from datetime import datetime, date
from typing import List

from use_cases.transacao_use_cases import (
    LancarTransacao, 
    ListarTransacoesPendentes,
    CategorizarTransacoesEmLote,
    ObterEstatisticasDashboard,
    FiltrarTransacoes,
    AtualizarTransacao, 
    DeletarTransacao    
)
from use_cases.repository_interfaces import ITransacaoRepository
from domain.transacao import Transacao, StatusTransacao, TipoTransacao

@pytest.fixture
def mock_repo():
    """
    Cria um mock_repo limpo (MagicMock) para cada teste que o solicitar.
    """
    return MagicMock(spec=ITransacaoRepository)

# --- Testes (Lançamento Rápido e Completo) ---

def test_lancar_transacao_rapida_sucesso_cai_na_inbox(mock_repo):
    
    # 1. Arrange 
    use_case = LancarTransacao(transacao_repo=mock_repo)
    input_data = {
        "id_usuario": "user123", "valor": 25.00,
        "tipo": "DESPESA", "descricao": "Almoço"
        # Sem categoria/perfil
    }
    # 2. Act 
    transacao_criada = use_case.execute(**input_data)
    # 3. Assert 
    assert transacao_criada.status == StatusTransacao.PENDENTE 
    mock_repo.add.assert_called_once_with(transacao_criada)

def test_lancar_transacao_completa_sucesso_pula_inbox(mock_repo):
    
    # 1. Arrange 
    use_case = LancarTransacao(transacao_repo=mock_repo)
    input_data = {
        "id_usuario": "user123", "valor": 200.00, "tipo": "DESPESA",
        "descricao": "Consulta Médica",
        "id_categoria": "cat_saude", # Lançamento completo
        "id_perfil": "perfil_pessoal" # Lançamento completo
    }
    # 2. Act 
    transacao_criada = use_case.execute(**input_data)
    # 3. Assert 
    assert transacao_criada.status == StatusTransacao.PROCESSADO
    assert transacao_criada.id_categoria == "cat_saude"
    mock_repo.add.assert_called_once_with(transacao_criada)

def test_lancar_transacao_falha_valor_zero(mock_repo):
    
    # 1. Arrange 
    use_case = LancarTransacao(transacao_repo=mock_repo)
    # 2. Act & 3. Assert
    with pytest.raises(ValueError, match="O valor deve ser maior que zero."):
        use_case.execute(id_usuario="user123", valor=0.0, tipo="RECEITA")
    mock_repo.add.assert_not_called()

# --- Teste (Listar Inbox) ---

def test_listar_transacoes_pendentes_sucesso(mock_repo):
    
    # 1. Arrange
    id_usuario_teste = "user_inbox"
    transacoes_mock = [
        Transacao(valor=100.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_usuario_teste),
        Transacao(valor=50.0, tipo=TipoTransacao.RECEITA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_usuario_teste)
    ]
    mock_repo.get_pendentes_by_usuario.return_value = transacoes_mock
    use_case = ListarTransacoesPendentes(transacao_repo=mock_repo)
    # 2. Act
    resultado = use_case.execute(id_usuario=id_usuario_teste)
    # 3. Assert
    mock_repo.get_pendentes_by_usuario.assert_called_once_with(id_usuario_teste)
    assert len(resultado) == 2

# --- Testes (Filtros) ---

def test_filtrar_transacoes_sucesso_delega_ao_repo(mock_repo):
    # 1. Arrange
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    
    filtros = {
        "id_usuario": "user_filter", 
        "data_de": date(2025, 1, 1),
        "data_ate": date(2025, 1, 31), 
        "valor_min": 50.0, 
        "valor_max": 100.0,
        "descricao": "Restaurante", 
        "status": StatusTransacao.PENDENTE,
        "id_categoria": None,
        "id_perfil": None,
        "sem_categoria": False,
        "sem_perfil": False
    }
    # 2. Act
    use_case.execute(**filtros)
    
    # 3. Assert
    mock_repo.get_by_filters.assert_called_once_with(**filtros)

# Teste para os novos filtros (sem categoria/perfil)
def test_filtrar_transacoes_com_filtros_avancados(mock_repo):
    # 1. Arrange
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    filtros = {
        "id_usuario": "user_filter",
        "status": StatusTransacao.PENDENTE,
        "id_categoria": "cat_lazer", # Filtra por categoria específica
        "sem_perfil": True             # Filtra onde perfil é NULO
    }
    # 2. Act
    use_case.execute(**filtros)
    # 3. Assert
    mock_repo.get_by_filters.assert_called_once_with(
        id_usuario="user_filter",
        data_de=None, data_ate=None, valor_min=None, valor_max=None,
        descricao=None, status=StatusTransacao.PENDENTE,
        id_categoria="cat_lazer", id_perfil=None,
        sem_categoria=False, sem_perfil=True
    )

def test_filtrar_transacoes_falha_data_invalida(mock_repo):
    
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    with pytest.raises(ValueError, match="A data 'Até' deve ser maior"):
        use_case.execute(id_usuario="u1", data_de=date(2025, 2, 1), data_ate=date(2025, 1, 31))
    mock_repo.get_by_filters.assert_not_called()

def test_filtrar_transacoes_falha_valor_invalido(mock_repo):
    
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    with pytest.raises(ValueError, match="O valor 'Máximo' deve ser maior"):
        use_case.execute(id_usuario="u1", valor_min=100.0, valor_max=50.0)
    mock_repo.get_by_filters.assert_not_called()

# --- Teste (Categorizar em Lote) ---

def test_categorizar_transacoes_em_lote_sucesso(mock_repo):
    # 1. Arrange
    id_usuario_teste = "user_lote"
    ids_para_atualizar = ["t1", "t2"]
    t1_pendente = Transacao(id="t1", valor=10.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_usuario_teste)
    t2_pendente = Transacao(id="t2", valor=20.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_usuario_teste)
    mock_repo.get_by_ids.return_value = [t1_pendente, t2_pendente]
    use_case = CategorizarTransacoesEmLote(transacao_repo=mock_repo)
    # 2. Act
    count = use_case.execute(
        id_usuario=id_usuario_teste, ids_transacoes=ids_para_atualizar,
        id_categoria="cat_transporte", id_perfil="perfil_pessoal"
    )
    # 3. Assert
    assert count == 2
    mock_repo.get_by_ids.assert_called_once_with(ids_para_atualizar)
    assert t1_pendente.status == StatusTransacao.PROCESSADO
    mock_repo.update_batch.assert_called_once_with([t1_pendente, t2_pendente])

def test_categorizar_transacoes_em_lote_falha_seguranca(mock_repo):
    id_usuario_teste = "user_lote"
    id_outro_usuario = "user_hacker"
    t1_outro_usuario = Transacao(id="t_outro", valor=10.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_outro_usuario)
    mock_repo.get_by_ids.return_value = [t1_outro_usuario]
    use_case = CategorizarTransacoesEmLote(transacao_repo=mock_repo)
    count = use_case.execute(
        id_usuario=id_usuario_teste, ids_transacoes=["t_outro"],
        id_categoria="cat_teste", id_perfil="perfil_teste"
    )
    assert count == 0
    mock_repo.update_batch.assert_not_called()

# Testes para Edição de Transação (Botão Editar) 

@pytest.fixture
def transacao_existente_pendente():
    """ Fixture de uma transação pendente para testes de edição/deleção. """
    return Transacao(
        id="trans_edit_1",
        id_usuario="user_edit",
        valor=100.0,
        tipo=TipoTransacao.DESPESA,
        data=datetime.now(),
        status=StatusTransacao.PENDENTE,
        descricao="Descrição Antiga"
    )

def test_atualizar_transacao_sucesso(mock_repo, transacao_existente_pendente):
    # 1. Arrange
    mock_repo.get_by_id.return_value = transacao_existente_pendente
    use_case = AtualizarTransacao(transacao_repo=mock_repo)
    
    dados_atualizados = {
        "descricao": "Descrição Atualizada",
        "id_categoria": "cat_alimentacao",
        "id_perfil": "perfil_pessoal"
    }

    # 2. Act
    resultado = use_case.execute(
        id_usuario="user_edit",
        id_transacao="trans_edit_1",
        dados_atualizados=dados_atualizados
    )

    # 3. Assert
    mock_repo.get_by_id.assert_called_once_with("trans_edit_1")
    assert resultado.descricao == "Descrição Atualizada"
    
    assert resultado.valor == 100.0 
    
    # Verifica se a categorização mudou o status
    assert resultado.status == StatusTransacao.PROCESSADO
    assert resultado.id_categoria == "cat_alimentacao"
    
    mock_repo.update.assert_called_once_with(transacao_existente_pendente)

def test_atualizar_transacao_falha_seguranca(mock_repo, transacao_existente_pendente):
    # 1. Arrange
    mock_repo.get_by_id.return_value = transacao_existente_pendente # Pertence a 'user_edit'
    use_case = AtualizarTransacao(transacao_repo=mock_repo)
    dados = {"valor": 50.0}

    # 2. Act & Assert
    with pytest.raises(PermissionError, match="Usuário não autorizado"):
        use_case.execute(
            id_usuario="user_hacker", # <-- Outro usuário
            id_transacao="trans_edit_1",
            dados_atualizados=dados
        )
    
    # Garante que não salvou
    mock_repo.update.assert_not_called()

# Testes para Deleção de Transação (Botão Deletar) 

def test_deletar_transacao_sucesso(mock_repo, transacao_existente_pendente):
    # 1. Arrange
    mock_repo.get_by_id.return_value = transacao_existente_pendente
    use_case = DeletarTransacao(transacao_repo=mock_repo)

    # 2. Act
    use_case.execute(id_usuario="user_edit", id_transacao="trans_edit_1")

    # 3. Assert
    mock_repo.get_by_id.assert_called_once_with("trans_edit_1")
    mock_repo.delete.assert_called_once_with("trans_edit_1")

def test_deletar_transacao_falha_seguranca(mock_repo, transacao_existente_pendente):
    # 1. Arrange
    mock_repo.get_by_id.return_value = transacao_existente_pendente # Pertence a 'user_edit'
    use_case = DeletarTransacao(transacao_repo=mock_repo)

    # 2. Act & Assert
    with pytest.raises(PermissionError, match="Usuário não autorizado"):
        use_case.execute(
            id_usuario="user_hacker", # <-- Outro usuário
            id_transacao="trans_edit_1"
        )
    
    mock_repo.delete.assert_not_called()

def test_deletar_transacao_nao_encontrada(mock_repo):
    # 1. Arrange
    mock_repo.get_by_id.return_value = None # Transação não existe
    use_case = DeletarTransacao(transacao_repo=mock_repo)

    # 2. Act
    # Não deve levantar erro, apenas não fazer nada
    use_case.execute(id_usuario="user_edit", id_transacao="trans_fake")

    # 3. Assert
    mock_repo.get_by_id.assert_called_once_with("trans_fake")
    mock_repo.delete.assert_not_called() # Não deve chamar delete

# --- Teste do Dashboard ---

def test_obter_estatisticas_dashboard_sucesso(mock_repo):
    # 1. Arrange
    id_usuario_teste = "user_dash"
    stats_mock = {"saldo_atual": 12047.92, "receitas_mes": 8500.0, "despesas_mes": 3420.15}
    mock_repo.get_dashboard_stats.return_value = stats_mock
    use_case = ObterEstatisticasDashboard(transacao_repo=mock_repo)
    # 2. Act
    resultado = use_case.execute(id_usuario=id_usuario_teste)
    # 3. Assert
    mock_repo.get_dashboard_stats.assert_called_once_with(id_usuario_teste)
    assert resultado["saldo_atual"] == 12047.92