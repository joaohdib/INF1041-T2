import pytest
from unittest.mock import MagicMock
from use_cases.transacao_use_cases import LancarTransacao
from use_cases.repository_interfaces import ITransacaoRepository
from domain.transacao import Transacao, StatusTransacao, TipoTransacao

def test_lancar_transacao_rapida_sucesso():
    # 1. Arrange 
    # Criamos um "Mock" do repositório.
    mock_repo = MagicMock(spec=ITransacaoRepository)
    
    use_case = LancarTransacao(transacao_repo=mock_repo)
    
    # Dados de entrada 
    input_data = {
        "id_usuario": "user123",
        "valor": 25.00,
        "tipo": "DESPESA",
        "descricao": "Almoço"
    }

    # 2. Act 
    transacao_criada = use_case.execute(**input_data)

    # 3. Assert 
    
    # Verificamos se a transação foi criada corretamente
    assert isinstance(transacao_criada, Transacao)
    assert transacao_criada.valor == 25.00
    assert transacao_criada.tipo == TipoTransacao.DESPESA
    assert transacao_criada.descricao == "Almoço"
    # Verificamos se ela está PENDENTE 
    assert transacao_criada.status == StatusTransacao.PENDENTE 

    # Verificamos se o método "add" do repositório foi chamado
    # exatamente uma vez, com o objeto correto.
    mock_repo.add.assert_called_once_with(transacao_criada)

def test_lancar_transacao_rapida_falha_valor_zero():
    # 1. Arrange 
    mock_repo = MagicMock(spec=ITransacaoRepository)
    use_case = LancarTransacaoRapida(transacao_repo=mock_repo)
    
    # 2. Act & 3. Assert
    with pytest.raises(ValueError, match="O valor deve ser maior que zero."):
        use_case.execute(
            id_usuario="user123",
            valor=0.0,
            tipo="RECEITA"
        )
    
    # Garantimos que o repositório não foi chamado
    mock_repo.add.assert_not_called()