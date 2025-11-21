from domain.transacao import TipoTransacao
from flask import Blueprint, jsonify, request
from infra.db.database import get_db_session
from infra.db.models import Categoria, Perfil, Meta as MetaModel

data_bp = Blueprint("data_bp", __name__)


@data_bp.route("/categorias", methods=["GET"])
def get_categorias_route():
    """Retorna a lista de categorias cadastradas."""
    id_usuario = "usuario_mock_id"
    tipo_filtro = request.args.get("tipo")

    db_session = get_db_session()
    try:
        query = db_session.query(Categoria).filter_by(id_usuario=id_usuario)

        if tipo_filtro:
            try:
                query = query.filter_by(tipo=TipoTransacao(tipo_filtro))
            except ValueError:
                pass

        categorias = query.all()

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


@data_bp.route("/metas", methods=["GET"])
def get_metas_route():
    """Retorna a lista de metas do usuário."""
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()
    
    try:
        metas = db_session.query(MetaModel).filter_by(id_usuario=id_usuario).all()
        
        metas_json = []
        for meta in metas:
            metas_json.append({
                "id": meta.id,
                "nome": meta.nome,
                "valor_alvo": meta.valor_alvo,
                "valor_atual": meta.valor_atual,
                "data_limite": meta.data_limite.isoformat() if meta.data_limite else None,
                "id_perfil": meta.id_perfil,
                "status": meta.status,
                "concluida_em": meta.concluida_em.isoformat() if meta.concluida_em else None,
                "finalizada_em": meta.finalizada_em.isoformat() if meta.finalizada_em else None,
            })
        
        return jsonify(metas_json), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()