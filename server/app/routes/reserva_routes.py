from flask import Blueprint, request, jsonify

from infra.db.database import get_db_session
from infra.repositories.meta_repository_sqlite import MetaRepositorySqlite
from infra.repositories.reserva_repository_sqlite import ReservaRepositorySqlite
from use_cases.reserva_use_cases import (
    CriarReserva,
    AtualizarReserva,
    ExcluirReserva,
    ListarMetasDisponiveisParaReserva,
)

reserva_bp = Blueprint("reserva_bp", __name__)


def _build_repositories(db_session):
    meta_repo = MetaRepositorySqlite(db_session)
    reserva_repo = ReservaRepositorySqlite(db_session)
    return meta_repo, reserva_repo


@reserva_bp.route("/", methods=["POST"])
def criar_reserva_route():
    id_usuario = "usuario_mock_id"
    payload = request.json or {}
    db_session = get_db_session()

    try:
        meta_repo, reserva_repo = _build_repositories(db_session)
        use_case = CriarReserva(reserva_repo, meta_repo)
        resposta = use_case.execute(
            id_usuario=id_usuario,
            id_meta=payload.get("id_meta"),
            valor=payload.get("valor"),
            id_transacao=payload.get("id_transacao"),
            observacao=payload.get("observacao"),
        )
        db_session.commit()
        return jsonify(resposta), 201
    except (ValueError, PermissionError) as e:
        db_session.rollback()
        status_code = 403 if isinstance(e, PermissionError) else 400
        return jsonify({"erro": str(e)}), status_code
    except Exception as e:
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@reserva_bp.route("/<reserva_id>", methods=["PUT"])
def atualizar_reserva_route(reserva_id: str):
    id_usuario = "usuario_mock_id"
    payload = request.json or {}
    db_session = get_db_session()

    try:
        meta_repo, reserva_repo = _build_repositories(db_session)
        use_case = AtualizarReserva(reserva_repo, meta_repo)
        resposta = use_case.execute(
            id_usuario=id_usuario,
            id_reserva=reserva_id,
            novo_valor=payload.get("valor"),
            observacao=payload.get("observacao"),
        )
        db_session.commit()
        return jsonify(resposta), 200
    except (ValueError, PermissionError) as e:
        db_session.rollback()
        status_code = 403 if isinstance(e, PermissionError) else 400
        return jsonify({"erro": str(e)}), status_code
    except Exception as e:
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@reserva_bp.route("/<reserva_id>", methods=["DELETE"])
def excluir_reserva_route(reserva_id: str):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo, reserva_repo = _build_repositories(db_session)
        use_case = ExcluirReserva(reserva_repo, meta_repo)
        resposta = use_case.execute(id_usuario=id_usuario, id_reserva=reserva_id)
        db_session.commit()
        return jsonify(resposta), 200
    except (ValueError, PermissionError) as e:
        db_session.rollback()
        status_code = 403 if isinstance(e, PermissionError) else 400
        return jsonify({"erro": str(e)}), status_code
    except Exception as e:
        db_session.rollback()
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@reserva_bp.route("/metas-disponiveis", methods=["GET"])
def listar_metas_disponiveis_route():
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = ListarMetasDisponiveisParaReserva(meta_repo)
        resposta = use_case.execute(id_usuario=id_usuario)
        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
