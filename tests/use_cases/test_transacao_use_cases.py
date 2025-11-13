import pytest
from unittest.mock import MagicMock
from datetime import datetime, date
from typing import List

from use_cases.transacao_use_cases import (
    LancarTransacao, 
    ListarTransacoesPendentes,
    CategorizarTransacoesEmLote,
    ObterEstatisticasDashboard,
    FiltrarTransacoes
)
from use_cases.repository_interfaces import ITransacaoRepository
from domain.transacao import Transacao, StatusTransacao, TipoTransacao

def test_lancar_transacao_rapida_sucesso_cai_na_inbox():
    # 1. Arrange 
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = LancarTransacao(transacao_repo=mock_repo)
    
    input_data = {
        "id_usuario": "user123",
        "valor": 25.00,
        "tipo": "DESPESA",
        "descricao": "Almoço"
        # Sem categoria/perfil
    }

    # 2. Act 
    transacao_criada = use_case.execute(**input_data)

    # 3. Assert 
    assert isinstance(transacao_criada, Transacao)
    # Verificamos se ela está PENDENTE 
    assert transacao_criada.status == StatusTransacao.PENDENTE 
    mock_repo.add.assert_called_once_with(transacao_criada)

    # Verificamos se o método "add" do repositório foi chamado exatamente uma vez, com o objeto correto.
    mock_repo.add.assert_called_once_with(transacao_criada)

def test_lancar_transacao_completa_sucesso_pula_inbox():
    # 1. Arrange 
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = LancarTransacao(transacao_repo=mock_repo)
    
    input_data = {
        "id_usuario": "user123",
        "valor": 200.00,
        "tipo": "DESPESA",
        "descricao": "Consulta Médica",
        "id_categoria": "cat_saude", # Lançamento completo
        "id_perfil": "perfil_pessoal" # Lançamento completo
    }

    # 2. Act 
    transacao_criada = use_case.execute(**input_data)

    # 3. Assert 
    # Verificamos se ela está PROCESSADA
    assert transacao_criada.status == StatusTransacao.PROCESSADO
    assert transacao_criada.id_categoria == "cat_saude"

def test_lancar_transacao_rapida_falha_valor_zero():
    # 1. Arrange 
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = LancarTransacao(transacao_repo=mock_repo)
    
    # 2. Act & 3. Assert
    with pytest.raises(ValueError, match="O valor deve ser maior que zero."):
        use_case.execute(
            id_usuario="user123",
            valor=0.0,
            tipo="RECEITA"
        )
    
    # Garantimos que o repositório não foi chamado
    mock_repo.add.assert_not_called()

def test_listar_transacoes_pendentes_sucesso():
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    id_usuario_teste = "user_inbox"
    
    # Mock de transações PENDENTES que o repositório deve retornar
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
    assert resultado[0].status == StatusTransacao.PENDENTE

def test_filtrar_transacoes_sucesso_delega_ao_repo():
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    
    filtros = {
        "id_usuario": "user_filter",
        "data_de": date(2025, 1, 1),
        "data_ate": date(2025, 1, 31),
        "valor_min": 50.0,
        "valor_max": 100.0,
        "descricao": "Restaurante",
        "status": StatusTransacao.PENDENTE
    }

    # 2. Act
    use_case.execute(**filtros)

    # 3. Assert
    # Verifica se o caso de uso chamou o repositório com os mesmos parâmetros
    mock_repo.get_by_filters.assert_called_once_with(**filtros)

def test_filtrar_transacoes_falha_data_invalida():
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    
    data_de = date(2025, 2, 1)
    data_ate = date(2025, 1, 31) # Data 'Até' ANTES da 'De'

    # 2. Act & 3. Assert
    with pytest.raises(ValueError, match="A data 'Até' deve ser maior"):
        use_case.execute(id_usuario="u1", data_de=data_de, data_ate=data_ate)
    
    mock_repo.get_by_filters.assert_not_called()

def test_filtrar_transacoes_falha_valor_invalido():
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = FiltrarTransacoes(transacao_repo=mock_repo)
    
    # 2. Act & 3. Assert
    with pytest.raises(ValueError, match="O valor 'Máximo' deve ser maior"):
        use_case.execute(id_usuario="u1", valor_min=100.0, valor_max=50.0)
    
    mock_repo.get_by_filters.assert_not_called()

def test_categorizar_transacoes_em_lote_sucesso():
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    id_usuario_teste = "user_lote"
    ids_para_atualizar = ["t1", "t2"]
    
    # Transações PENDENTES que o repositório vai retornar
    t1_pendente = Transacao(id="t1", valor=10.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_usuario_teste)
    t2_pendente = Transacao(id="t2", valor=20.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_usuario_teste)
    
    mock_repo.get_by_ids.return_value = [t1_pendente, t2_pendente]
    
    use_case = CategorizarTransacoesEmLote(transacao_repo=mock_repo)
    
    # 2. Act
    count = use_case.execute(
        id_usuario=id_usuario_teste,
        ids_transacoes=ids_para_atualizar,
        id_categoria="cat_transporte",
        id_perfil="perfil_pessoal"
    )

    # 3. Assert
    assert count == 2 # Verificamos se 2 transações foram processadas
    mock_repo.get_by_ids.assert_called_once_with(ids_para_atualizar)
    
    # Verificamos se a lógica de domínio foi chamada (status mudou)
    assert t1_pendente.status == StatusTransacao.PROCESSADO
    assert t1_pendente.id_categoria == "cat_transporte"
    assert t2_pendente.status == StatusTransacao.PROCESSADO
    
    mock_repo.update_batch.assert_called_once_with([t1_pendente, t2_pendente])

def test_categorizar_transacoes_em_lote_falha_seguranca():
    # Teste de segurança: usuário tenta categorizar transação de outro
    
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    id_usuario_teste = "user_lote"
    id_outro_usuario = "user_hacker"
    
    t1_outro_usuario = Transacao(id="t_outro", valor=10.0, tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE, id_usuario=id_outro_usuario)
    
    mock_repo.get_by_ids.return_value = [t1_outro_usuario]
    use_case = CategorizarTransacoesEmLote(transacao_repo=mock_repo)

    # 2. Act
    count = use_case.execute(
        id_usuario=id_usuario_teste,
        ids_transacoes=["t_outro"],
        id_categoria="cat_teste",
        id_perfil="perfil_teste"
    )
    
    # 3. Assert
    assert count == 0 # Nenhuma transação foi atualizada
    mock_repo.update_batch.assert_not_called() # Método de salvar não foi chamado

def test_obter_estatisticas_dashboard_sucesso():
    # 1. Arrange
    mock_repo = MagicMock(spec=ITransacaoRepository)
    id_usuario_teste = "user_dash"
    
    stats_mock = {"saldo_atual": 12047.92, "receitas_mes": 8500.0, "despesas_mes": 3420.15}
    mock_repo.get_dashboard_stats.return_value = stats_mock
    
    use_case = ObterEstatisticasDashboard(transacao_repo=mock_repo)

    # 2. Act
    resultado = use_case.execute(id_usuario=id_usuario_teste)

    # 3. Assert
    mock_repo.get_dashboard_stats.assert_called_once_with(id_usuario_teste)
    assert resultado["saldo_atual"] == 12047.92
    assert resultado["receitas_mes"] == 8500.0