INF1041 Personal Finance Platform
=================================

Full-stack personal finance planner built for the INF1041 course. The project helps users import transactions, categorize expenses, set savings targets, and keep digital receipts. It follows Clean Architecture boundaries and SOLID principles to keep the codebase testable, modular, and easy to evolve.

Table of Contents
-----------------

1. About the Project
2. Architecture & Principles
3. Features
4. Tech Stack
5. Getting Started
6. Running Tests
7. API Overview
8. Project Structure
9. Contributing

1. About the Project
--------------------

- **Goal**: deliver a didactic-yet-realistic finance assistant with dashboards, goals ("metas"), reservation envelopes, and an inbox for receipts.
- **Frontend**: static HTML/CSS/JS bundled in `client/`, consuming the backend through REST and displaying dashboards without external frameworks.
- **Backend**: Flask + SQLAlchemy service exposing CRUD endpoints for transactions, goals, reserves, and data insights.
- **Data layer**: SQLite database initialized with seed data so the UI works on first run.

2. Architecture & Principles
----------------------------

- **Clean Architecture**
	- `domain/`: enterprise entities and business rules (e.g., `transacao.py`, `meta.py`).
	- `use_cases/`: application services orchestrating workflows such as imports, dashboard aggregations, or inbox handling.
	- `infra/`: implementation details like repositories, storage adapters, and database configuration.
	- `app/`: delivery layer (Flask blueprints) translating HTTP requests into use-case calls.
- **SOLID Highlights**
	- *Single Responsibility*: each repository handles exactly one aggregate (`transacao_repository_sqlite.py`, `meta_repository_sqlite.py`, etc.).
	- *Open/Closed*: use-case services depend on interfaces from `repository_interfaces.py`, making it easy to add new persistence strategies without modifying business logic.
	- *Liskov & Interface Segregation*: small, purpose-built interfaces (e.g., storage vs repository) prevent leaking infrastructure details into the domain.
	- *Dependency Inversion*: delivery and infra depend on abstractions defined in `use_cases/`, ensuring the core domain stays framework-agnostic.

3. Features
-----------

- Dashboard with income/expense indicators and category charts.
- Transaction CRUD with attachments stored under `uploads/`.
- Goal (meta) tracking and progress monitoring.
- Envelope-style reserves (`reservas`) to earmark funds.
- CSV import workflow with configurable column mapping.
- Inbox to review uploaded receipts and supporting documents.

4. Tech Stack
-------------

- **Backend**: Python 3.11+, Flask, SQLAlchemy, Flask-Cors, Pytest.
- **Database**: SQLite (file-based, auto-initialized by `init_db`).
- **Frontend**: HTML5, CSS3, vanilla JavaScript modules (`client/js/*`).
- **Tooling**: pytest for unit tests, seed scripts in `app/main.py` for fixtures.

5. Getting Started
------------------

### Prerequisites

- Python 3.11 or later.
- A modern browser (Chrome, Firefox, Edge) for the client.

### Backend Setup

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r server/requirements.txt

# 3. Run the Flask server (default: http://localhost:5000)
python server/app/main.py
```

The first launch creates the SQLite database, seeds mock data (profiles, categories), and exposes REST endpoints under `/api`.

### Frontend Setup

- Open `client/index.html` directly in the browser **or** serve the `client/` folder with Live Server / any static server to avoid CORS restrictions.
- Update API URLs inside `client/js/api.js` if you run the backend on a non-default host/port.

6. Running Tests
----------------

Unit tests live in `server/tests/use_cases/`.

```powershell
.\.venv\Scripts\activate
pytest server/tests
```

Add new tests near the corresponding use-case to keep the business core well-covered.

7. API Overview
---------------

| Area        | Base Path              | Highlights |
|-------------|------------------------|------------|
| Transactions| `/api/transacoes`      | CRUD, CSV import, attachment upload |
| Goals       | `/api/metas`           | Create/update goals, track progress |
| Reserves    | `/api/reservas`        | Manage savings envelopes |
| Data        | `/api/data`            | Aggregated metrics for dashboards |
| Uploads     | `/uploads/<filename>`  | Serve stored receipt images |

Detailed route docs can be explored with any REST client (Insomnia, Postman) against the running server.

8. Project Structure
--------------------

```
INF1041-T2/
├── client/              # Static frontend (dashboard, metas, inbox)
├── server/
│   ├── app/             # Flask app + blueprints
│   ├── domain/          # Entities and value objects
│   ├── infra/           # DB config, repositories, storage
│   ├── use_cases/       # Application services & interfaces
│   └── tests/           # Pytest suites for use cases
└── uploads/             # Receipt attachments (gitignored)
```

