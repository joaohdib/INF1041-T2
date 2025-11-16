import json
from flask import Blueprint, request, jsonify
from datetime import date, datetime
from use_cases.transacao_use_cases import (
    LancarTransacao, 
    ListarTransacoesPendentes,
    CategorizarTransacoesEmLote,
    ObterEstatisticasDashboard,
    AnexarReciboTransacao,
    FiltrarTransacoes,
    AtualizarTransacao,
    DeletarTransacao
)
from use_cases.importacao_use_cases import (
    ImportarExtratoBancario,
    SalvarMapeamentoCSV,
    ListarMapeamentosCSV,
)
from infra.repositories.transacao_repository_sqlite import TransacaoRepositorySqlite
from infra.repositories.anexo_repository_sqlite import AnexoRepositorySqlite
from infra.repositories.mapeamento_csv_repository_sqlite import (
    MapeamentoCSVRepositorySqlite,
)
from infra.storage.anexo_storage_local import AnexoStorageLocal
from infra.db.database import get_db_session 
from domain.transacao import Transacao, StatusTransacao
from domain.anexo import Anexo

transacao_bp = Blueprint('transacao_bp', __name__)

# Função auxiliar de serialização
def serialize_transacao(t: Transacao) -> dict:
    """ Converte um objeto Transacao em um dicionário para JSON. """
    return {
        "id": t.id,
        "data": t.data.isoformat(),
        "descricao": t.descricao,
        "valor": t.valor,
        "tipo": t.tipo.value,
        "status": t.status.value,
        "id_categoria": t.id_categoria,
        "id_perfil": t.id_perfil
    }

def serialize_anexo(a: Anexo) -> dict:
    """ Converte um objeto Anexo em um dicionário para JSON. """
    return {
        "id": a.id,
        "id_transacao": a.id_transacao,
        "nome_arquivo": a.nome_arquivo,
        "caminho_storage": a.caminho_storage, # O frontend usará isso para o link
        "tipo_mime": a.tipo_mime,
        "data_upload": a.data_upload.isoformat()
    }

@transacao_bp.route('/lancar_transacao', methods=['POST'])
def lancar_transacao_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    
    try:
        # 1. Lê dados do formulario
        data_form = request.form
        
        # 2. Prepara o payload para o Caso de Uso
        payload = {
            "id_usuario": id_usuario,
            "valor": float(data_form.get('valor')),
            "tipo": data_form.get('tipo'),
            "data": datetime.fromisoformat(data_form.get('data')) if data_form.get('data') else datetime.now(),
            "descricao": data_form.get('descricao') or None,
            "id_categoria": data_form.get('id_categoria') or None,
            "id_perfil": data_form.get('id_perfil') or None,
        }

        # 3. Chama o Caso de Uso para criar a transação
        transacao_repo = TransacaoRepositorySqlite(db_session)
        use_case_lancar = LancarTransacao(transacao_repo)
        transacao_criada = use_case_lancar.execute(**payload)
        
        # 4. Verifica se um anexo foi enviado (request.files)
        if 'anexo' in request.files:
            file = request.files['anexo']
            if file and file.filename != '':
                # Se sim, injeta dependências e chama o caso de uso de anexo
                anexo_repo = AnexoRepositorySqlite(db_session)
                storage = AnexoStorageLocal()
                use_case_anexar = AnexarReciboTransacao(storage, anexo_repo, transacao_repo)
                
                use_case_anexar.execute(
                    id_usuario=id_usuario,
                    id_transacao=transacao_criada.id,
                    file_stream=file,
                    file_name=file.filename,
                    content_type=file.mimetype,
                    content_length=file.content_length
                )
        
        # 5. Commit de tudo
        db_session.commit()
        return jsonify(serialize_transacao(transacao_criada)), 201
    
    except ValueError as e:
        db_session.rollback(); return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback(); return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/<id_transacao>/anexo', methods=['POST'])
def anexar_recibo_route(id_transacao: str):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    
    try:
        # 1. Validação do arquivo na requisição (form-data)
        if 'anexo' not in request.files:
            return jsonify({"erro": "Nenhum arquivo 'anexo' enviado no form-data."}), 400
        
        file = request.files['anexo']
        
        if not file or file.filename == '':
            return jsonify({"erro": "Nome de arquivo inválido ou não selecionado."}), 400

        # 2. Injeção de Dependência (DI)
        anexo_repo = AnexoRepositorySqlite(db_session)
        transacao_repo = TransacaoRepositorySqlite(db_session)
        storage = AnexoStorageLocal()
        
        # 3. Chama o Caso de Uso
        use_case = AnexarReciboTransacao(storage, anexo_repo, transacao_repo)
        anexo_criado = use_case.execute(
            id_usuario=id_usuario,
            id_transacao=id_transacao,
            file_stream=file,             # Passa o objeto FileStorage
            file_name=file.filename,     # Nome original
            content_type=file.mimetype,  # Tipo MIME
            content_length=file.content_length # Tamanho
        )
        
        # 4. Commit da transação
        db_session.commit()
        
        return jsonify({
            "id_anexo": anexo_criado.id, 
            "id_transacao": anexo_criado.id_transacao,
            "nome_arquivo": anexo_criado.nome_arquivo,
            "caminho": anexo_criado.caminho_storage
        }), 201

    except ValueError as e: # Erro de validação (tamanho, tipo, etc)
        db_session.rollback()
        return jsonify({"erro": str(e)}), 400
    except PermissionError as e: # Erro de segurança
        db_session.rollback()
        return jsonify({"erro": str(e)}), 403 # Forbidden
    except Exception as e: # Erro interno (ex: falha ao salvar no disco)
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/<id_transacao>/anexos', methods=['GET'])
def get_anexos_route(id_transacao: str):
    id_usuario = "usuario_mock_id" # (Validação de usuário ocorreria no caso de uso)
    db_session = get_db_session()
    try:
        anexo_repo = AnexoRepositorySqlite(db_session)
        
        # (Faltando validação de segurança, mas funcional)
        anexos = anexo_repo.get_by_transacao_id(id_transacao)
        
        return jsonify([serialize_anexo(a) for a in anexos]), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/<id_transacao>', methods=['PUT'])
def atualizar_transacao_route(id_transacao: str):
    id_usuario = "usuario_mock_id"
    dados_atualizados = request.json
    db_session = get_db_session()
    
    try:
        transacao_repo = TransacaoRepositorySqlite(db_session)
        use_case = AtualizarTransacao(transacao_repo)
        
        transacao_atualizada = use_case.execute(
            id_usuario=id_usuario,
            id_transacao=id_transacao,
            dados_atualizados=dados_atualizados
        )
        
        db_session.commit()
        return jsonify(serialize_transacao(transacao_atualizada)), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"erro": str(e)}), 400
    except PermissionError as e:
        db_session.rollback()
        return jsonify({"erro": str(e)}), 403
    except Exception as e:
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/<id_transacao>', methods=['DELETE'])
def deletar_transacao_route(id_transacao: str):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    
    try:
        transacao_repo = TransacaoRepositorySqlite(db_session)
        use_case = DeletarTransacao(transacao_repo)
        
        use_case.execute(
            id_usuario=id_usuario,
            id_transacao=id_transacao
        )
        
        db_session.commit()
        return jsonify({"mensagem": "Transação deletada com sucesso."}), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"erro": str(e)}), 404 # Not Found
    except PermissionError as e:
        db_session.rollback()
        return jsonify({"erro": str(e)}), 403
    except Exception as e:
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/importar_extrato', methods=['POST'])
def importar_extrato_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        if 'arquivo' not in request.files:
            return jsonify({'erro': "Nenhum arquivo enviado."}), 400

        arquivo = request.files['arquivo']
        if not arquivo.filename:
            return jsonify({'erro': "Arquivo inválido."}), 400

        try:
            mapping_payload = request.form.get('mapeamento_colunas')
            mapping = json.loads(mapping_payload) if mapping_payload else None
        except json.JSONDecodeError:
            return jsonify({'erro': "Mapeamento de colunas inválido."}), 400

        mapping_id = request.form.get('id_mapeamento') or None
        salvar_nome = request.form.get('salvar_mapeamento_nome') or None
        sem_cabecalho = True

        conteudo = arquivo.read()

        transacao_repo = TransacaoRepositorySqlite(db_session)
        mapeamento_repo = MapeamentoCSVRepositorySqlite(db_session)

        saved_mapping_id = None
        if salvar_nome:
            if not mapping:
                return jsonify({'erro': "Para salvar o mapeamento informe as colunas."}), 400
            salvar_uc = SalvarMapeamentoCSV(mapeamento_repo)
            salvo = salvar_uc.execute(
                id_usuario=id_usuario,
                nome=salvar_nome,
                coluna_data=mapping.get('data'),
                coluna_valor=mapping.get('valor'),
                coluna_descricao=mapping.get('descricao')
            )
            saved_mapping_id = salvo.id
            mapping_id = saved_mapping_id

        use_case = ImportarExtratoBancario(transacao_repo, mapeamento_repo)
        resultado = use_case.execute(
            id_usuario=id_usuario,
            file_bytes=conteudo,
            file_name=arquivo.filename,
            column_mapping=mapping,
            mapping_id=mapping_id,
            sem_cabecalho=sem_cabecalho
        )

        if saved_mapping_id:
            resultado['mapeamento_salvo_id'] = saved_mapping_id

        db_session.commit()
        return jsonify(resultado), 201

    except ValueError as e:
        db_session.rollback()
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        db_session.rollback()
        return jsonify({'erro': f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@transacao_bp.route('/importacao/mapeamentos', methods=['GET'])
def listar_mapeamentos_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    try:
        repo = MapeamentoCSVRepositorySqlite(db_session)
        use_case = ListarMapeamentosCSV(repo)
        mapeamentos = use_case.execute(id_usuario)
        payload = [
            {
                "id": m.id,
                "nome": m.nome,
                "coluna_data": m.coluna_data,
                "coluna_valor": m.coluna_valor,
                "coluna_descricao": m.coluna_descricao,
            }
            for m in mapeamentos
        ]
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({'erro': f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/inbox', methods=['GET'])
def get_inbox_route():
    # --- Inbox padrão agora usa Filtros ---
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    try:
        transacao_repo = TransacaoRepositorySqlite(db_session)
        use_case = FiltrarTransacoes(transacao_repo) 
        transacoes = use_case.execute(id_usuario=id_usuario) 
        
        transacoes_json = [serialize_transacao(t) for t in transacoes]
        return jsonify(transacoes_json), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
    
@transacao_bp.route('/inbox/filtrar', methods=['GET'])
def filtrar_inbox_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    
    try:
        args = request.args
        
        # Converte tipos
        data_de = date.fromisoformat(args.get('data_de')) if args.get('data_de') else None
        data_ate = date.fromisoformat(args.get('data_ate')) if args.get('data_ate') else None
        valor_min = float(args.get('valor_min')) if args.get('valor_min') is not None else None
        valor_max = float(args.get('valor_max')) if args.get('valor_max') is not None else None
        status_str = args.get('status')
        status = StatusTransacao(status_str.upper()) if status_str else None
        
        # Converte booleans (ex: /filtrar?sem_categoria=true)
        sem_categoria = args.get('sem_categoria', 'false').lower() == 'true'
        sem_perfil = args.get('sem_perfil', 'false').lower() == 'true'

        params = {
            "id_usuario": id_usuario,
            "data_de": data_de,
            "data_ate": data_ate,
            "valor_min": valor_min,
            "valor_max": valor_max,
            "descricao": args.get('descricao'),
            "status": status,
            "id_categoria": args.get('id_categoria'),
            "id_perfil": args.get('id_perfil'),
            "sem_categoria": sem_categoria,
            "sem_perfil": sem_perfil
        }

        transacao_repo = TransacaoRepositorySqlite(db_session)
        use_case = FiltrarTransacoes(transacao_repo)
        
        transacoes = use_case.execute(**params)
        
        transacoes_json = [serialize_transacao(t) for t in transacoes]
        return jsonify(transacoes_json), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@transacao_bp.route('/inbox/categorizar', methods=['POST'])
def categorizar_em_lote_route():
    id_usuario = "usuario_mock_id"
    data = request.json
    
    db_session = get_db_session()
    
    try:
        ids_transacoes = data.get('ids_transacoes')
        id_categoria = data.get('id_categoria')
        id_perfil = data.get('id_perfil')
        
        transacao_repo = TransacaoRepositorySqlite(db_session)
        
        use_case = CategorizarTransacoesEmLote(transacao_repo)
        count = use_case.execute(
            id_usuario=id_usuario,
            ids_transacoes=ids_transacoes,
            id_categoria=id_categoria,
            id_perfil=id_perfil
        )
        
        db_session.commit() # Salva as mudanças do lote
        
        return jsonify({"mensagem": f"{count} transações atualizadas com sucesso."}), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
    
@transacao_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    
    try:
        transacao_repo = TransacaoRepositorySqlite(db_session)
        
        use_case = ObterEstatisticasDashboard(transacao_repo)
        estatisticas = use_case.execute(id_usuario=id_usuario)
        
        return jsonify(estatisticas), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
