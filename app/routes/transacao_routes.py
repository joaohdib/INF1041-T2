from flask import Blueprint, request, jsonify
from use_cases.transacao_use_cases import LancarTransacao
from infra.repositories.transacao_repository_sqlite import TransacaoRepositorySqlite
from infra.db.database import get_db_connection # Função que retorna a conexão

transacao_bp = Blueprint('transacao_bp', __name__)

@transacao_bp.route('/lancar_transacao', methods=['POST'])
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