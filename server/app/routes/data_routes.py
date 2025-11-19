from domain.transacao import TipoTransacao
from flask import Blueprint, jsonify, request
from infra.db.database import get_db_session
from infra.db.models import Categoria, Perfil

data_bp = Blueprint("data_bp", __name__)


@data_bp.route("/categorias", methods=["GET"])
def get_categorias_route():
    """Retorna a lista de categorias cadastradas."""
    id_usuario = "usuario_mock_id"
    tipo_filtro = request.args.get("tipo")  # Lê o parametro da URL (ex: ?tipo=DESPESA)

    db_session = get_db_session()
    try:
        query = db_session.query(Categoria).filter_by(id_usuario=id_usuario)

        if tipo_filtro:
            # Filtra se o parametro foi passado
            try:
                query = query.filter_by(tipo=TipoTransacao(tipo_filtro))
            except ValueError:
                pass  # Ignora se o tipo for inválido

        categorias = query.all()

        # Converte para JSON
        categorias_json = [
            {"id": c.id, "nome": c.nome, "tipo": c.tipo.value} for c in categorias
        ]
        return jsonify(categorias_json), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@data_bp.route("/perfis", methods=["GET"])
def get_perfis_route():
    """Retorna a lista de perfis cadastrados."""
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    try:
        perfis = db_session.query(Perfil).filter_by(id_usuario=id_usuario).all()
        perfis_json = [{"id": p.id, "nome": p.nome} for p in perfis]
        return jsonify(perfis_json), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
