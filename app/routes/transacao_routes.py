from flask import Blueprint, request, jsonify
from use_cases.transacao_use_cases import (
    LancarTransacao, 
    ListarTransacoesPendentes,
    CategorizarTransacoesEmLote,
    ObterEstatisticasDashboard
)
from infra.repositories.transacao_repository_sqlite import TransacaoRepositorySqlite
from infra.db.database import get_db_connection # Função que retorna a conexão
from domain.transacao import Transacao

transacao_bp = Blueprint('transacao_bp', __name__)

@transacao_bp.route('/transacao/lancar_transacao', methods=['POST'])
def lancar_transacao_route():
    # 1. Extrai dados da Requisição
    data = request.json
    id_usuario = "usuario_mock_id" # Em um cenário real, viria do token de autenticação
    
    try:
        # 2. Injeção de Dependência
        db_conn = get_db_connection()
        transacao_repo = TransacaoRepositorySqlite(db_conn)
        
        # 3. Chama o Caso de Uso
        use_case = LancarTransacao(transacao_repo)
        transacao = use_case.execute(
            id_usuario=id_usuario,
            valor=float(data.get('valor')),
            tipo=data.get('tipo'),
            descricao=data.get('descricao')
        )
        
        # 4. Retorna a Resposta
        return jsonify({"id": transacao.id, "status": transacao.status.value}), 201
    
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    
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

@transacao_bp.route('/inbox', methods=['GET'])
def get_inbox_route():
    id_usuario = "usuario_mock_id" # Viria do token
    
    try:
        db_conn = get_db_connection()
        transacao_repo = TransacaoRepositorySqlite(db_conn)
        
        use_case = ListarTransacoesPendentes(transacao_repo)
        transacoes_pendentes = use_case.execute(id_usuario=id_usuario)
        
        # Serializa a lista de transações
        transacoes_json = [serialize_transacao(t) for t in transacoes_pendentes]
        
        return jsonify(transacoes_json), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    
@transacao_bp.route('/inbox/categorizar', methods=['POST'])
def categorizar_em_lote_route():
    id_usuario = "usuario_mock_id" # Viria do token
    data = request.json
    
    try:
        # Extrai os dados da requisição
        ids_transacoes = data.get('ids_transacoes') # Espera uma lista de IDs
        id_categoria = data.get('id_categoria')
        id_perfil = data.get('id_perfil')
        
        db_conn = get_db_connection()
        transacao_repo = TransacaoRepositorySqlite(db_conn)
        
        use_case = CategorizarTransacoesEmLote(transacao_repo)
        count = use_case.execute(
            id_usuario=id_usuario,
            ids_transacoes=ids_transacoes,
            id_categoria=id_categoria,
            id_perfil=id_perfil
        )
        
        return jsonify({"mensagem": f"{count} transações atualizadas com sucesso."}), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    
@transacao_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats_route():
    id_usuario = "usuario_mock_id" # Viria do token
    
    try:
        db_conn = get_db_connection()
        transacao_repo = TransacaoRepositorySqlite(db_conn)
        
        use_case = ObterEstatisticasDashboard(transacao_repo)
        estatisticas = use_case.execute(id_usuario=id_usuario)
        
        return jsonify(estatisticas), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
