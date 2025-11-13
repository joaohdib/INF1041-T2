import pytest
from unittest.mock import MagicMock, Mock
from datetime import datetime

from use_cases.transacao_use_cases import AnexarReciboTransacao
from use_cases.repository_interfaces import (
    ITransacaoRepository, 
    IAnexoRepository
)
from infra.storage.storage_interface import IAnexoStorage
from domain.transacao import Transacao, TipoTransacao, StatusTransacao
from domain.anexo import Anexo

# --- Configuração (Arrange) Global para os Testes ---

@pytest.fixture
def mock_storage():
    """ Mock para a interface de storage. """
    return MagicMock(spec=IAnexoStorage)

@pytest.fixture
def mock_anexo_repo():
    """ Mock para o repositório de anexos. """
    return MagicMock(spec=IAnexoRepository)

@pytest.fixture
def mock_transacao_repo():
    """ Mock para o repositório de transações. """
    return MagicMock(spec=ITransacaoRepository)

@pytest.fixture
def use_case(mock_storage, mock_anexo_repo, mock_transacao_repo):
    """ Instancia o Caso de Uso com todas as dependências mockadas. """
    return AnexarReciboTransacao(mock_storage, mock_anexo_repo, mock_transacao_repo)

# --- Testes ---

def test_anexar_recibo_sucesso(use_case, mock_storage, mock_anexo_repo, mock_transacao_repo):
    # 1. Arrange (Cenário de Sucesso)
    id_usuario = "user_1"
    id_transacao = "trans_1"
    
    # Mock do stream do arquivo (como o Flask FileStorage)
    mock_file = Mock(content_length=1024, filename="recibo.pdf", mimetype="application/pdf")
    
    # Mock da transação que existe no banco
    transacao_existente = Transacao(
        id=id_transacao, id_usuario=id_usuario, valor=10.0, 
        tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE
    )
    mock_transacao_repo.get_by_id.return_value = transacao_existente
    
    # Mock do caminho que o storage retornará
    mock_storage.save.return_value = "uploads/fake-uuid.pdf"

    # 2. Act
    anexo_criado = use_case.execute(
        id_usuario=id_usuario,
        id_transacao=id_transacao,
        file_stream=mock_file,
        file_name="recibo.pdf",
        content_type="application/pdf",
        content_length=1024
    )

    # 3. Assert
    # Verifica se a transação foi checada
    mock_transacao_repo.get_by_id.assert_called_once_with(id_transacao)
    
    # Verifica se o arquivo foi salvo no storage
    mock_storage.save.assert_called_once_with(mock_file, "recibo.pdf", "application/pdf")
    
    # Verifica se o anexo foi salvo no repositório
    mock_anexo_repo.add.assert_called_once()
    args = mock_anexo_repo.add.call_args[0]
    anexo_salvo = args[0]
    
    assert isinstance(anexo_salvo, Anexo)
    assert anexo_salvo.caminho_storage == "uploads/fake-uuid.pdf"
    assert anexo_salvo.id_transacao == id_transacao
    assert anexo_salvo.tamanho_bytes == 1024

def test_anexar_recibo_falha_tamanho_excedido(use_case, mock_storage, mock_anexo_repo):
    # 1. Arrange (Cenário de Falha: Tamanho)
    tamanho_grande = AnexarReciboTransacao.MAX_SIZE_BYTES + 1
    
    # 2. Act & Assert
    with pytest.raises(ValueError, match="tamanho máximo"):
        use_case.execute(
            id_usuario="user_1", id_transacao="trans_1",
            file_stream=Mock(), file_name="arquivo.jpg",
            content_type="image/jpeg", content_length=tamanho_grande
        )
    
    # Garante que nada foi salvo
    mock_storage.save.assert_not_called()
    mock_anexo_repo.add.assert_not_called()

def test_anexar_recibo_falha_formato_nao_suportado(use_case, mock_storage, mock_anexo_repo):
    # 1. Arrange (Cenário de Falha: Formato)
    
    # 2. Act & Assert
    with pytest.raises(ValueError, match="Formato de arquivo não suportado"):
        use_case.execute(
            id_usuario="user_1", id_transacao="trans_1",
            file_stream=Mock(), file_name="virus.exe",
            content_type="application/octet-stream", content_length=1024
        )
        
    # Garante que nada foi salvo
    mock_storage.save.assert_not_called()
    mock_anexo_repo.add.assert_not_called()

def test_anexar_recibo_falha_transacao_nao_encontrada(use_case, mock_transacao_repo, mock_storage):
    # 1. Arrange
    mock_transacao_repo.get_by_id.return_value = None # Transação não existe
    
    # 2. Act & Assert
    with pytest.raises(ValueError, match="Transação não encontrada"):
        use_case.execute(
            id_usuario="user_1", id_transacao="trans_fake",
            file_stream=Mock(), file_name="recibo.pdf",
            content_type="application/pdf", content_length=1024
        )
    
    mock_storage.save.assert_not_called()

def test_anexar_recibo_falha_seguranca_outro_usuario(use_case, mock_transacao_repo, mock_storage):
    # 1. Arrange
    id_usuario = "user_1"
    id_usuario_hacker = "hacker_2"
    id_transacao = "trans_user_1"
    
    # Transação existe, mas pertence a outro usuário
    transacao_existente = Transacao(
        id=id_transacao, id_usuario=id_usuario, valor=10.0, 
        tipo=TipoTransacao.DESPESA, data=datetime.now(), status=StatusTransacao.PENDENTE
    )
    mock_transacao_repo.get_by_id.return_value = transacao_existente

    # 2. Act & Assert
    with pytest.raises(PermissionError, match="Usuário não autorizado"):
        use_case.execute(
            id_usuario=id_usuario_hacker, # <-- O hacker tentando anexar
            id_transacao=id_transacao,
            file_stream=Mock(), file_name="recibo.pdf",
            content_type="application/pdf", content_length=1024
        )
        
    mock_storage.save.assert_not_called()