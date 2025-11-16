import pytest
from unittest.mock import MagicMock

from domain.mapeamento_csv import MapeamentoCSV
from use_cases.importacao_use_cases import ImportarExtratoBancario, SalvarMapeamentoCSV
from use_cases.repository_interfaces import ITransacaoRepository, IMapeamentoCSVRepository


@pytest.fixture
def mock_repo():
    return MagicMock(spec=ITransacaoRepository)


@pytest.fixture
def mock_mapeamento_repo():
    return MagicMock(spec=IMapeamentoCSVRepository)


def test_importar_csv_com_mapeamento_sucesso(mock_repo):
    conteudo = "Data;Valor;Descricao\n01/02/2024;123,45;Almoço".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    resultado = use_case.execute(
        id_usuario="u1",
        file_bytes=conteudo,
        file_name="extrato.csv",
        column_mapping={
            "data": "Data",
            "valor": "Valor",
            "descricao": "Descricao",
        },
    )

    assert resultado["total_importadas"] == 1
    mock_repo.add.assert_called_once()


def test_importar_ofx_sucesso(mock_repo):
    ofx = """
<OFX>
  <BANKTRANLIST>
    <STMTTRN>
      <DTPOSTED>20240101
      <TRNAMT>-50.00
      <MEMO>Mercado</MEMO>
    </STMTTRN>
  </BANKTRANLIST>
</OFX>
""".encode("latin-1")

    use_case = ImportarExtratoBancario(mock_repo)
    resultado = use_case.execute(
        id_usuario="u1",
        file_bytes=ofx,
        file_name="extrato.ofx",
    )

    assert resultado["total_importadas"] == 1
    mock_repo.add.assert_called_once()


def test_importar_formato_invalido(mock_repo):
    use_case = ImportarExtratoBancario(mock_repo)
    with pytest.raises(ValueError, match="Formato de arquivo inválido"):
        use_case.execute(
            id_usuario="u1",
            file_bytes=b"qualquer",
            file_name="extrato.pdf",
        )
    mock_repo.add.assert_not_called()


def test_importar_csv_sem_colunas_obrigatorias(mock_repo):
    conteudo = "col1,col2\n1,2".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    with pytest.raises(ValueError, match="CSV sem as colunas esperadas"):
        use_case.execute(
            id_usuario="u1",
            file_bytes=conteudo,
            file_name="extrato.csv",
        )


def test_importar_csv_sem_transacoes(mock_repo):
    conteudo = "data,valor,descricao\n".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    with pytest.raises(ValueError, match="Nenhuma transação válida"):
        use_case.execute(
            id_usuario="u1",
            file_bytes=conteudo,
            file_name="extrato.csv",
        )


def test_importar_csv_com_mapeamento_salvo(mock_repo, mock_mapeamento_repo):
    conteudo = "header1,header2,header3\n01/01/2024,100,Aluguel".encode()
    mock_mapeamento_repo.get_by_id.return_value = MapeamentoCSV(
        id_usuario='u1',
        nome='Banco X',
        coluna_data='header1',
        coluna_valor='header2',
        coluna_descricao='header3',
        id='map1'
    )

    use_case = ImportarExtratoBancario(mock_repo, mock_mapeamento_repo)
    resultado = use_case.execute(
        id_usuario='u1',
        file_bytes=conteudo,
        file_name='extrato.csv',
        mapping_id='map1'
    )

    assert resultado['total_importadas'] == 1
    mock_mapeamento_repo.get_by_id.assert_called_once_with('map1')
    mock_repo.add.assert_called_once()


def test_importar_csv_mapeamento_colunas_repetidas(mock_repo):
    conteudo = "Data,Valor,Descricao\n01/02/2024,10,Teste".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    with pytest.raises(ValueError, match="Cada campo"):
        use_case.execute(
            id_usuario='u1',
            file_bytes=conteudo,
            file_name='extrato.csv',
            column_mapping={
                'data': 'Data',
                'valor': 'Data',
                'descricao': 'Descricao'
            }
        )


def test_importar_csv_sem_cabecalho(mock_repo):
    conteudo = "12/06/2025,mercado,1000\n13/06/2025,padaria,-50".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    resultado = use_case.execute(
        id_usuario='u1',
        file_bytes=conteudo,
        file_name='extrato.csv',
        column_mapping={
            'data': '__col_0',
            'descricao': '__col_1',
            'valor': '__col_2',
        },
        sem_cabecalho=True,
    )

    assert resultado['total_importadas'] == 2
    assert mock_repo.add.call_count == 2


def test_importar_csv_sem_cabecalho_sem_mapeamento(mock_repo):
    conteudo = "12/06/2025,mercado,1000\n".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    with pytest.raises(ValueError, match="Mapeie manualmente as colunas"):
        use_case.execute(
            id_usuario='u1',
            file_bytes=conteudo,
            file_name='extrato.csv',
            sem_cabecalho=True,
        )


def test_importar_csv_com_mapeamento_salvo_sem_cabecalho(mock_repo, mock_mapeamento_repo):
    conteudo = "12/06/2025,mercado,1000\n13/06/2025,padaria,50".encode()
    mock_mapeamento_repo.get_by_id.return_value = MapeamentoCSV(
        id_usuario='u1',
        nome='Banco Sem Cabeçalho',
        coluna_data='__col_0',
        coluna_valor='__col_2',
        coluna_descricao='__col_1',
        id='map2'
    )

    use_case = ImportarExtratoBancario(mock_repo, mock_mapeamento_repo)
    resultado = use_case.execute(
        id_usuario='u1',
        file_bytes=conteudo,
        file_name='extrato.csv',
        mapping_id='map2'
    )

    assert resultado['total_importadas'] == 2
    mock_mapeamento_repo.get_by_id.assert_called_once_with('map2')


def test_salvar_mapeamento_csv_sucesso(mock_mapeamento_repo):
    mock_mapeamento_repo.exists_nome.return_value = False
    mock_mapeamento_repo.add.side_effect = lambda m: m
    use_case = SalvarMapeamentoCSV(mock_mapeamento_repo)
    resultado = use_case.execute(
        id_usuario='u1',
        nome='Banco XPTO',
        coluna_data='Data',
        coluna_valor='Valor',
        coluna_descricao='Descricao'
    )

    assert resultado.nome == 'Banco XPTO'
    mock_mapeamento_repo.add.assert_called_once()


def test_salvar_mapeamento_coluna_duplicada(mock_mapeamento_repo):
    use_case = SalvarMapeamentoCSV(mock_mapeamento_repo)
    with pytest.raises(ValueError, match="Cada coluna essencial deve ser única"):
        use_case.execute(
            id_usuario='u1',
            nome='Banco',
            coluna_data='Data',
            coluna_valor='Data',
            coluna_descricao='Descricao'
        )


def test_salvar_mapeamento_nome_repetido(mock_mapeamento_repo):
    mock_mapeamento_repo.exists_nome.return_value = True
    use_case = SalvarMapeamentoCSV(mock_mapeamento_repo)
    with pytest.raises(ValueError, match="Já existe um mapeamento"):
        use_case.execute(
            id_usuario='u1',
            nome='Banco',
            coluna_data='Data',
            coluna_valor='Valor',
            coluna_descricao='Descricao'
        )


def test_importar_csv_valor_negativo_determina_despesa(mock_repo):
    conteudo = "Data,Valor,Descricao\n01/02/2024,-250.50,Cartão\n".encode()
    use_case = ImportarExtratoBancario(mock_repo)

    use_case.execute(
        id_usuario='u1',
        file_bytes=conteudo,
        file_name='extrato.csv',
        column_mapping={
            'data': 'Data',
            'valor': 'Valor',
            'descricao': 'Descricao'
        }
    )

    args, _ = mock_repo.add.call_args
    transacao = args[0]
    assert transacao.tipo.name == 'DESPESA'
    assert transacao.valor == 250.50
