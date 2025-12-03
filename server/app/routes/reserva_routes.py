from flask import Blueprint, jsonify, request
from domain.meta import Meta
from domain.reserva import Reserva
from infra.db.database import get_db_session
from infra.repositories.meta_repository_sqlite import MetaRepositorySqlite
from infra.repositories.reserva_repository_sqlite import ReservaRepositorySqlite
from use_cases.reserva_use_cases import (
    AtualizarReserva,
    CriarReserva,
    ExcluirReserva,
    ListarMetasDisponiveisParaReserva,
)

reserva_bp = Blueprint("reserva_bp", __name__)


def _build_repositories(db_session):
    meta_repo = MetaRepositorySqlite(db_session)
    reserva_repo = ReservaRepositorySqlite(db_session)
    return meta_repo, reserva_repo


def _serialize_reserva(reserva: Reserva) -> dict:
    return {
        "id": reserva.id,
        "id_usuario": reserva.id_usuario,
        "id_meta": reserva.id_meta,
        "valor": reserva.valor,
        "id_transacao": reserva.id_transacao,
        "observacao": reserva.observacao,
        "criado_em": reserva.criado_em.isoformat() if reserva.criado_em else None,
        "atualizado_em": reserva.atualizado_em.isoformat()
        if reserva.atualizado_em
        else None,
    }


def _serialize_meta_progress(meta: Meta) -> dict:
    payload = {
        "id": meta.id,
        "nome": meta.nome,
        "valor_alvo": meta.valor_alvo,
        "valor_atual": meta.valor_atual,
        "progresso_percentual": meta.progresso_percentual(),
        "esta_concluida": meta.esta_concluida(),
        "concluida_em": meta.concluida_em.isoformat()
        if meta.concluida_em
        else None,
    }
    if payload["esta_concluida"]:
        payload["mensagem"] = "Meta concluída! Parabéns pelo objetivo atingido."
    return payload


@reserva_bp.route("/", methods=["POST"])
def criar_reserva_route():
    id_usuario = "usuario_mock_id"
    payload = request.json or {}
    db_session = get_db_session()

    try:
        meta_repo, reserva_repo = _build_repositories(db_session)
        use_case = CriarReserva(reserva_repo, meta_repo)
        resultado = use_case.execute(
            id_usuario=id_usuario,
            id_meta=payload.get("id_meta"),
            valor=payload.get("valor"),
            id_transacao=payload.get("id_transacao"),
            observacao=payload.get("observacao"),
        )
        db_session.commit()
        reserva_obj = resultado["reserva"]
        meta_obj = resultado["meta"]
        meta_payload = _serialize_meta_progress(meta_obj)
        resposta = {
            "reserva": _serialize_reserva(reserva_obj),
            "meta": meta_payload,
        }
        if "mensagem" in meta_payload:
            resposta["mensagem"] = meta_payload["mensagem"]
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
        resultado = use_case.execute(
            id_usuario=id_usuario,
            id_reserva=reserva_id,
            novo_valor=payload.get("valor"),
            observacao=payload.get("observacao"),
        )
        db_session.commit()
        reserva_obj = resultado["reserva"]
        meta_obj = resultado["meta"]
        resposta = {
            "reserva": _serialize_reserva(reserva_obj),
            "meta": _serialize_meta_progress(meta_obj),
        }
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
        resultado = use_case.execute(id_usuario=id_usuario, id_reserva=reserva_id)
        db_session.commit()
        meta_obj = resultado["meta"]
        resposta = {
            "meta": _serialize_meta_progress(meta_obj),
            "mensagem": "Reserva removida e progresso da meta atualizado.",
        }
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
        metas = use_case.execute(id_usuario=id_usuario)
        metas_payload = [
            {
                "id": meta.id,
                "nome": meta.nome,
                "valor_alvo": meta.valor_alvo,
                "valor_atual": meta.valor_atual,
                "progresso_percentual": meta.progresso_percentual(),
                "data_limite": meta.data_limite.isoformat(),
            }
            for meta in metas
        ]
        resposta = {"metas": metas_payload}
        if not metas_payload:
            resposta["mensagem"] = (
                "Nenhuma meta disponível. Que tal criar uma nova meta agora?"
            )
        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
