import sys
import os
from flask import Flask, jsonify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # --- Importações após ajuste do Path ---
    from app.routes.transacao_routes import transacao_bp
    from infra.db.database import init_db
except ImportError as e:
    print("Erro de importação. Verifique a estrutura de pastas e os __init__.py")
    print(f"Detalhe: {e}")
    sys.exit(1)

try:
    print("Inicializando o banco de dados...")
    init_db()
    print("Banco de dados pronto.")
except Exception as e:
    print(f"ERRO: Não foi possível inicializar o banco de dados.")
    print(e)
    # Se o banco falhar, a aplicação não deve iniciar.
    sys.exit(1)


# --- Criação da Aplicação Flask ---
app = Flask(__name__)

app.register_blueprint(transacao_bp, url_prefix='/api/transacoes')

# --- Rota Raiz (Health Check) ---
@app.route('/')
@app.route('/api')
def index():
    """ Rota de verificação para saber se o servidor está online. """
    return jsonify({
        "status": "Servidor da API Financeira está online!",
        "documentacao_rotas": "/api/transacoes/..."
    })

# --- Ponto de Entrada ---
if __name__ == "__main__":
    """
    Executa o servidor Flask.
    'debug=True' ativa o auto-reload quando você salva o código.
    'host="0.0.0.0"' torna o servidor acessível na sua rede local 
    (útil para testar de outro dispositivo), não apenas no localhost.
    """
    print("Iniciando servidor Flask em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
    