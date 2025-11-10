from flask import Blueprint, request, jsonify
from infra.db.database import get_db_connection
from infra.repositories.meta_repository_sqlite import MetaRepositorySqlite
from use_cases.meta_use_cases import CriarMeta

meta_bp = Blueprint('meta_bp', __name__)


@meta_bp.route('/meta/criar_meta', methods=['POST'])
def criar_meta_route():
    id_usuario = "usuario_mock_id"  # Em produção: viria do token
    data = request.json or {}

    try:
        db_conn = get_db_connection()
        meta_repo = MetaRepositorySqlite(db_conn)
        use_case = CriarMeta(meta_repo)

        resultado = use_case.execute(
            id_usuario=id_usuario,
            nome=data.get('nome'),
            valor_alvo=data.get('valor'),
            data_limite=data.get('data_limite'),
            id_perfil=data.get('id_perfil')
        )

        return jsonify(resultado), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
