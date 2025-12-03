from flask import Blueprint, jsonify, request
from infra.db.database import get_db_session
from infra.repositories.meta_repository_sqlite import MetaRepositorySqlite
from infra.repositories.meta_uso_repository_sqlite import MetaUsoRepositorySqlite
from infra.repositories.transacao_repository_sqlite import TransacaoRepositorySqlite
from use_cases.meta_use_cases import (
    CriarMeta,
    EditarMeta,
    PausarMeta,
    RetomarMeta,
    CancelarMeta,
    ConcluirMeta,
    RegistrarUsoMeta,
    LiberarSaldoMeta,
)

meta_bp = Blueprint("meta_bp", __name__)


def _serialize_meta(meta):
    return {
        "id": meta.id,
        "nome": meta.nome,
        "valor_alvo": meta.valor_alvo,
        "valor_atual": meta.valor_atual,
        "data_limite": meta.data_limite.isoformat() if meta.data_limite else None,
        "id_perfil": meta.id_perfil,
        "status": meta.status.value,
        "concluida_em": meta.concluida_em.isoformat() if meta.concluida_em else None,
        "finalizada_em": meta.finalizada_em.isoformat()
        if meta.finalizada_em
        else None,
        "progresso_percentual": meta.progresso_percentual(),
        "esta_concluida": meta.esta_concluida(),
        "esta_finalizada": meta.esta_finalizada(),
    }


@meta_bp.route("/meta/criar_meta", methods=["POST"])
def criar_meta_route():
    id_usuario = "usuario_mock_id"
    data = request.json or {}

    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = CriarMeta(meta_repo)

        resultado = use_case.execute(
            id_usuario=id_usuario,
            nome=data.get("nome"),
            valor_alvo=data.get("valor"),
            data_limite=data.get("data_limite"),
            id_perfil=data.get("id_perfil"),
        )

        db_session.commit()
        meta = resultado["meta"]
        sugestoes = resultado["sugestoes"]
        resposta = {**_serialize_meta(meta), "sugestoes": sugestoes}
        return jsonify(resposta), 201

    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação na criação da meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno na criação da meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/editar", methods=["PUT"])
def editar_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    data = request.json or {}

    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = EditarMeta(meta_repo)

        meta = use_case.execute(
            id_meta=id_meta,
            id_usuario=id_usuario,
            nome=data.get("nome"),
            valor_alvo=data.get("valor_alvo"),
            data_limite=data.get("data_limite"),
        )

        db_session.commit()
        resposta = {
            **_serialize_meta(meta),
            "progresso_percentual": meta.progresso_percentual(),
            "mensagem": "Meta editada com sucesso!",
        }
        return jsonify(resposta), 200

    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação na edição da meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno na edição da meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/pausar", methods=["POST"])
def pausar_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = PausarMeta(meta_repo)

        meta = use_case.execute(id_meta=id_meta, id_usuario=id_usuario)

        db_session.commit()
        resposta = {
            "id": meta.id,
            "status": meta.status.value,
            "mensagem": "Meta pausada com sucesso!",
        }
        return jsonify(resposta), 200

    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação ao pausar meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno ao pausar meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/retomar", methods=["POST"])
def retomar_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = RetomarMeta(meta_repo)

        meta = use_case.execute(id_meta=id_meta, id_usuario=id_usuario)

        db_session.commit()
        resposta = {
            "id": meta.id,
            "status": meta.status.value,
            "mensagem": "Meta retomada com sucesso!",
        }
        return jsonify(resposta), 200

    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação ao retomar meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno ao retomar meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/cancelar", methods=["POST"])
def cancelar_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    data = request.json or {}

    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = CancelarMeta(meta_repo)

        resultado = use_case.execute(
            id_meta=id_meta,
            id_usuario=id_usuario,
            acao_fundos=data.get("acao_fundos", "manter"),
            id_meta_destino=data.get("id_meta_destino"),
        )

        db_session.commit()
        resposta = {
            "meta": _serialize_meta(resultado["meta"]),
            "acao_fundos": resultado["acao_fundos"],
            "id_meta_destino": resultado["id_meta_destino"],
            "mensagem": "Meta cancelada com sucesso!",
        }
        return jsonify(resposta), 200

    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação ao cancelar meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno ao cancelar meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/concluir", methods=["POST"])
def concluir_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        use_case = ConcluirMeta(meta_repo)
        meta = use_case.execute(id_meta=id_meta, id_usuario=id_usuario)
        db_session.commit()
        resposta = {
            "id": meta.id,
            "concluida_em": meta.concluida_em.isoformat()
            if meta.concluida_em
            else None,
            "mensagem": "Meta concluída com sucesso!",
        }
        return jsonify(resposta), 200
    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação ao concluir meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno ao concluir meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/registrar-uso", methods=["POST"])
def registrar_uso_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    data = request.json or {}
    id_transacao = data.get("id_transacao")

    if not id_transacao:
        return jsonify({"erro": "id_transacao é obrigatório"}), 400

    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        transacao_repo = TransacaoRepositorySqlite(db_session)
        meta_uso_repo = MetaUsoRepositorySqlite(db_session)
        use_case = RegistrarUsoMeta(meta_repo, meta_uso_repo, transacao_repo)
        resultado = use_case.execute(
            id_meta=id_meta,
            id_transacao=id_transacao,
            id_usuario=id_usuario,
        )
        db_session.commit()
        resposta = {
            "meta": _serialize_meta(resultado["meta"]),
            "valor_utilizado": resultado["valor_utilizado"],
        }
        return jsonify(resposta), 200
    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação ao registrar uso da meta: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno ao registrar uso da meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/liberar-saldo", methods=["POST"])
def liberar_saldo_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        transacao_repo = TransacaoRepositorySqlite(db_session)
        meta_uso_repo = MetaUsoRepositorySqlite(db_session)
        use_case = LiberarSaldoMeta(meta_repo, meta_uso_repo)
        resultado = use_case.execute(id_meta=id_meta, id_usuario=id_usuario)
        db_session.commit()
        resposta = {
            "meta": _serialize_meta(resultado["meta"]),
            "valor_total_meta": resultado["valor_total_meta"],
            "valor_utilizado": resultado["valor_utilizado"],
            "saldo_restante": resultado["saldo_restante"],
            "mensagem": "Saldo liberado com sucesso!",
        }
        return jsonify(resposta), 200
    except ValueError as e:
        db_session.rollback()
        print(f"Erro de validação ao liberar saldo: {e}")
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db_session.rollback()
        print(f"Erro interno ao liberar saldo: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()


@meta_bp.route("/meta/<id_meta>/detalhes", methods=["GET"])
def detalhes_meta_route(id_meta):
    id_usuario = "usuario_mock_id"
    db_session = get_db_session()

    try:
        meta_repo = MetaRepositorySqlite(db_session)
        transacao_repo = TransacaoRepositorySqlite(db_session)
        meta_uso_repo = MetaUsoRepositorySqlite(db_session)

        meta = meta_repo.get_by_id(id_meta)
        if not meta or meta.id_usuario != id_usuario:
            return jsonify({"erro": "Meta não encontrada"}), 404

        total_utilizado = meta_uso_repo.sum_uso_por_meta(id_meta)
        saldo_restante = meta.valor_atual - total_utilizado

        return jsonify(
            {
                "id": meta.id,
                "nome": meta.nome,
                "valor_alvo": meta.valor_alvo,
                "valor_economizado": meta.valor_atual,
                "valor_utilizado": total_utilizado,
                "saldo_restante": saldo_restante,
                "status": meta.status.value,
                "concluida": meta.esta_concluida(),
                "finalizada": meta.esta_finalizada(),
                "concluida_em": meta.concluida_em.isoformat()
                if meta.concluida_em
                else None,
                "finalizada_em": meta.finalizada_em.isoformat()
                if meta.finalizada_em
                else None,
            }
        ), 200
    except Exception as e:
        print(f"Erro interno ao obter detalhes da meta: {e}")
        return jsonify({"erro": f"Erro interno: {e}"}), 500
    finally:
        db_session.close()
