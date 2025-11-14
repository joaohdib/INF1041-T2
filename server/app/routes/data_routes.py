from flask import Blueprint, jsonify
from infra.db.database import get_db_session, Session
from infra.db.models import Categoria, Perfil 
data_bp = Blueprint('data_bp', __name__)

@data_bp.route('/categorias', methods=['GET'])
def get_categorias_route():
    """ Retorna a lista de categorias cadastradas. """
    id_usuario = "usuario_mock_id" # Usar o mesmo mock
    db_session = get_db_session()
    try:
        # Busca direto dos models (simples)
        categorias = db_session.query(Categoria).filter_by(id_usuario=id_usuario).all()

        # Converte para JSON
        categorias_json = [
            {"id": c.id, "nome": c.nome} for c in categorias
        ]
        return jsonify(categorias_json), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()

@data_bp.route('/perfis', methods=['GET'])
def get_perfis_route():
    """ Retorna a lista de perfis cadastrados. """
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    try:
        perfis = db_session.query(Perfil).filter_by(id_usuario=id_usuario).all()
        perfis_json = [
            {"id": p.id, "nome": p.nome} for p in perfis
        ]
        return jsonify(perfis_json), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()