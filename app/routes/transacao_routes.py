from flask import Blueprint, request, jsonify
from use_cases.transacao_use_cases import (
    LancarTransacao, 
    ListarTransacoesPendentes,
    CategorizarTransacoesEmLote,
    ObterEstatisticasDashboard,
    AnexarReciboTransacao
)
from infra.repositories.transacao_repository_sqlite import TransacaoRepositorySqlite
from infra.repositories.anexo_repository_sqlite import AnexoRepositorySqlite
from infra.storage.anexo_storage_local import AnexoStorageLocal
from infra.db.database import get_db_session 
from domain.transacao import Transacao

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

@transacao_bp.route('/lancar_transacao', methods=['POST'])
def lancar_transacao_route():
    data = request.json
    id_usuario = "usuario_mock_id" # Em um cenário real, viria do token
    
    # 1. Pega a sessão
    db_session = get_db_session()
    
    try:
        # 2. Injeção de Dependência (com a sessão)
        transacao_repo = TransacaoRepositorySqlite(db_session)
        
        # 3. Chama o Caso de Uso
        use_case = LancarTransacao(transacao_repo)
        transacao = use_case.execute(
            id_usuario=id_usuario,
            valor=float(data.get('valor')),
            tipo=data.get('tipo'),
            descricao=data.get('descricao')
        )
        
        # 4. Commit da transação!
        db_session.commit()
        
        return jsonify({"id": transacao.id, "status": transacao.status.value}), 201
    
    except ValueError as e:
        db_session.rollback() # Desfaz em caso de erro de negócio
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback() # Desfaz em caso de erro interno
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close() # Fecha a sessão, devolvendo-a ao pool

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

@transacao_bp.route('/inbox', methods=['GET'])
def get_inbox_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    try:
        transacao_repo = TransacaoRepositorySqlite(db_session)
        
        use_case = ListarTransacoesPendentes(transacao_repo)
        transacoes_pendentes = use_case.execute(id_usuario=id_usuario)
        
        transacoes_json = [serialize_transacao(t) for t in transacoes_pendentes]
        
        # GET não precisa de commit
        return jsonify(transacoes_json), 200
        
    except Exception as e:
        # GET não deve ter rollback, mas é bom fechar a sessão
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
