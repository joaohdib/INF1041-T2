import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS  

# Garante que os módulos das pastas irmãs sejam encontrados
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.routes.transacao_routes import transacao_bp
    from app.routes.meta_routes import meta_bp
    from app.routes.reserva_routes import reserva_bp
    from app.routes.data_routes import data_bp
    from infra.db.database import init_db, Session
    
    from infra.db.models import Perfil, Categoria

except ImportError as e:
    print("Erro de importação. Verifique a estrutura de pastas e os __init__.py")
    print(f"Detalhe: {e}")
    sys.exit(1)


def seed_initial_data():
    """ Garante que os dados mínimos (mocks) existam no DB. """
    print("Verificando dados iniciais (seeding)...")
    db_session = Session()
    
    try:
        user_id = "usuario_mock_id"
        
        # --- 1. Perfis (Corrigido) ---
        # Garante que Perfis são 'Pessoal' e 'PJ'
        perfis_seed = {
            "perfil_pessoal": Perfil(id="perfil_pessoal", id_usuario=user_id, nome="Pessoal"),
            "perfil_pj": Perfil(id="perfil_pj", id_usuario=user_id, nome="PJ")
        }
        
        for p_id, p_obj in perfis_seed.items():
            if not db_session.query(Perfil).filter_by(id=p_id).first():
                db_session.add(p_obj)
                print(f"Criando perfil: {p_obj.nome}")

        # --- 2. Categorias (Expandido) ---
        categorias_seed = {
            "cat_alimentacao": Categoria(id="cat_alimentacao", id_usuario=user_id, nome="Alimentação"),
            "cat_transporte": Categoria(id="cat_transporte", id_usuario=user_id, nome="Transporte"),
            "cat_saude": Categoria(id="cat_saude", id_usuario=user_id, nome="Saúde"),
            "cat_moradia": Categoria(id="cat_moradia", id_usuario=user_id, nome="Moradia (Aluguel/Contas)"),
            "cat_lazer": Categoria(id="cat_lazer", id_usuario=user_id, nome="Lazer (Cinema, Bares)"),
            "cat_educacao": Categoria(id="cat_educacao", id_usuario=user_id, nome="Educação (Cursos, Livros)"),
            "cat_vestuario": Categoria(id="cat_vestuario", id_usuario=user_id, nome="Vestuário"),
            "cat_servicos_app": Categoria(id="cat_servicos_app", id_usuario=user_id, nome="Serviços (Streaming, Apps)"),
            "cat_impostos": Categoria(id="cat_impostos", id_usuario=user_id, nome="Impostos e Taxas"),
            "cat_invest": Categoria(id="cat_invest", id_usuario=user_id, nome="Investimentos (Aportes)"),
            "cat_viagem": Categoria(id="cat_viagem", id_usuario=user_id, nome="Viagem"),
            "cat_outros_d": Categoria(id="cat_outros_d", id_usuario=user_id, nome="Outras Despesas"),
            
            # Receitas (3)
            "cat_salario": Categoria(id="cat_salario", id_usuario=user_id, nome="Salário"),
            "cat_renda_sup": Categoria(id="cat_renda_sup", id_usuario=user_id, nome="Renda Suplementar (Freela)"),
            "cat_outros_r": Categoria(id="cat_outros_r", id_usuario=user_id, nome="Outras Receitas")
        }

        for c_id, c_obj in categorias_seed.items():
            if not db_session.query(Categoria).filter_by(id=c_id).first():
                db_session.add(c_obj)
                print(f"Criando categoria: {c_obj.nome}")

        db_session.commit()
        print("Seeding concluído.")
    
    except Exception as e:
        db_session.rollback()
        print(f"Erro durante o seeding: {e}")
    finally:
        db_session.close()


# --- Inicialização do Banco de Dados ---
try:
    # Esta chamada agora cria as tabelas via SQLAlchemy Models
    init_db()
    
    seed_initial_data()
    
except Exception as e:
    print(f"ERRO: Não foi possível inicializar o banco de dados.")
    print(e)
    sys.exit(1)


# --- Criação da Aplicação Flask ---
app = Flask(__name__)

CORS(app)

# Registro dos Blueprints (rotas)
app.register_blueprint(transacao_bp, url_prefix='/api/transacoes')
app.register_blueprint(meta_bp, url_prefix='/api/metas')
app.register_blueprint(reserva_bp, url_prefix='/api/reservas')
app.register_blueprint(data_bp, url_prefix='/api/data')

# --- Gerenciamento de Sessão (Teardown) ---
@app.teardown_appcontext
def shutdown_session(exception=None):
    """ Remove a sessão do SQLAlchemy ao final de cada request. """
    Session.remove()

# --- Rota Raiz (Health Check) ---
@app.route('/')
@app.route('/api')
def index():
    """ Rota de verificação para saber se o servidor está online. """
    return jsonify({
        "status": "Servidor da API Financeira (SQLAlchemy) está online!",
        "documentacao_rotas": "/api/transacoes/... /api/metas/... e /api/reservas/..."
    })

# --- Ponto de Entrada ---
if __name__ == "__main__":
    print("Iniciando servidor Flask em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)