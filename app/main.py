import sys
import os
from flask import Flask, jsonify

# Garante que os módulos das pastas irmãs sejam encontrados
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # --- Importações após ajuste do Path ---
    from app.routes.transacao_routes import transacao_bp
    from app.routes.meta_routes import meta_bp
    from app.routes.reserva_routes import reserva_bp
    from infra.db.database import init_db, Session
except ImportError as e:
    print("Erro de importação. Verifique a estrutura de pastas e os __init__.py")
    print(f"Detalhe: {e}")
    sys.exit(1)

# --- Inicialização do Banco de Dados ---
try:
    # Esta chamada agora cria as tabelas via SQLAlchemy Models
    init_db()
except Exception as e:
    print(f"ERRO: Não foi possível inicializar o banco de dados.")
    print(e)
    sys.exit(1)


# --- Criação da Aplicação Flask ---
app = Flask(__name__)

# Registro dos Blueprints (rotas)
app.register_blueprint(transacao_bp, url_prefix='/api/transacoes')
app.register_blueprint(meta_bp, url_prefix='/api/metas')
app.register_blueprint(reserva_bp, url_prefix='/api/reservas')

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
    