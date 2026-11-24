# CloudDesk Makefile
# Windows: use .venv/Scripts/python.exe; PYTHONPATH must include backend (use ; separator)
# Set PYTHONIOENCODING=utf-8 for CLI output with symbols

.PHONY: setup seed ingest backend demo demo-% test lint mcp mcp-server docker-up docker-down terraform-validate smoke

# ============================================================================
# Variables
# ============================================================================
PYTHON := .venv/Scripts/python.exe
UV := .venv/Scripts/uv.exe
PYTHONPATH := backend;.
BACKEND_DIR := backend
FRONTEND_DIR := frontend
SAMPLE_DATA_DIR := sample_data

# Windows-compatible export
export PYTHONPATH
export PYTHONIOENCODING := utf-8

# ============================================================================
# Setup
# ============================================================================
setup: .venv .env
	@echo "Setup complete. Run 'make backend' to start the API."

.venv: pyproject.toml uv.lock
	@echo "Creating virtual environment and installing dependencies..."
	uv venv
	uv sync --all-extras
	@touch .venv

.env: .env.example
	@if not exist .env (copy .env.example .env && echo "Created .env from .env.example. Edit it with your settings.")

.env.example:
	@echo "Creating .env.example..."
	@echo DEMO_MODE=true > .env.example
	@echo ENVIRONMENT=development >> .env.example
	@echo CORS_ORIGINS=http://localhost:3000 >> .env.example
	@echo JWT_SECRET=dev-secret-change-in-production >> .env.example
	@echo SUPABASE_JWT_SECRET= >> .env.example
	@echo DATABASE_URL=sqlite+aiosqlite:///./data/support.db >> .env.example
	@echo CHECKPOINT_DB_PATH=./data/checkpoints.db >> .env.example
	@echo REDIS_URL= >> .env.example
	@echo USE_FAKE_REDIS=true >> .env.example
	@echo LLM_PROVIDER=fake >> .env.example
	@echo LLM_API_KEY= >> .env.example
	@echo LLM_MODEL=gpt-4o-mini >> .env.example
	@echo EMBEDDING_PROVIDER=fake >> .env.example
	@echo EMBEDDING_MODEL=text-embedding-3-small >> .env.example
	@echo EMBEDDING_DIMENSIONS=384 >> .env.example
	@echo VECTOR_STORE=memory >> .env.example
	@echo QDRANT_URL= >> .env.example
	@echo QDRANT_API_KEY= >> .env.example
	@echo QDRANT_COLLECTION=clouddesk_knowledge >> .env.example
	@echo APPROVAL_REQUIRED_FOR_REFUNDS=true >> .env.example
	@echo MAX_REFUND_WITHOUT_APPROVAL=0 >> .env.example
	@echo TOOL_TIMEOUT_SECONDS=30 >> .env.example
	@echo RATE_LIMIT_PER_MINUTE=120 >> .env.example
	@echo SAMPLE_DATA_DIR=sample_data >> .env.example
	@echo LANGCHAIN_TRACING_V2=false >> .env.example
	@echo LANGCHAIN_API_KEY= >> .env.example
	@echo LANGCHAIN_PROJECT=clouddesk-support >> .env.example

# ============================================================================
# Data
# ============================================================================
seed:
	@echo "Loading sample data into database..."
	$(PYTHON) scripts/seed.py

ingest:
	@echo "Chunking and indexing knowledge base..."
	$(PYTHON) scripts/ingest.py

# ============================================================================
# Development
# ============================================================================
backend:
	@echo "Starting FastAPI on :8000..."
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

demo:
	@echo "Running demo for CD-1002 (refund approval)..."
	$(PYTHON) scripts/demo.py

demo-%:
	@echo "Running demo for $*..."
	$(PYTHON) scripts/demo.py --ticket $*

# ============================================================================
# Testing
# ============================================================================
test:
	@echo "Running backend tests (offline)..."
	cd $(BACKEND_DIR) && $(PYTHON) -m pytest -q --tb=short

test-unit:
	$(PYTHON) -m pytest tests/unit -q --tb=short

test-api:
	$(PYTHON) -m pytest tests/api -q --tb=short

test-rag:
	$(PYTHON) -m pytest tests/rag -q --tb=short

test-agents:
	$(PYTHON) -m pytest tests/agents -q --tb=short

test-workflow:
	$(PYTHON) -m pytest tests/workflow -q --tb=short

test-evaluation:
	$(PYTHON) -m pytest tests/evaluation -q --tb=short

test-deployment:
	$(PYTHON) -m pytest tests/deployment -q --tb=short

test-frontend:
	cd $(FRONTEND_DIR) && npm run test -- --run

lint:
	@echo "Running ruff..."
	ruff check .
	@echo "Running frontend lint..."
	cd $(FRONTEND_DIR) && npm run lint

typecheck:
	cd $(FRONTEND_DIR) && npx tsc --noEmit

# ============================================================================
# MCP Server
# ============================================================================
mcp:
	@echo "Starting MCP server (read-only tools)..."
	$(PYTHON) -m integrations.mcp.server

mcp-client:
	@echo "Running MCP client example..."
	$(PYTHON) -m integrations.mcp.client_example

# ============================================================================
# Docker
# ============================================================================
docker-up:
	docker compose config -q && docker compose up --build

docker-down:
	docker compose down -v

docker-logs:
	docker compose logs -f

# ============================================================================
# Terraform
# ============================================================================
terraform-validate:
	@echo "Validating Terraform for all clouds..."
	cd deployment/aws && terraform init -backend=false && terraform validate
	cd deployment/azure && terraform init -backend=false && terraform validate
	cd deployment/gcp && terraform init -backend=false && terraform validate

terraform-plan-%:
	cd deployment/$* && terraform plan -var-file=environments/dev/terraform.tfvars

terraform-apply-%:
	cd deployment/$* && terraform apply -var-file=environments/dev/terraform.tfvars

# ============================================================================
# Smoke Test
# ============================================================================
smoke:
	@echo "Running smoke test against BASE_URL=$$BASE_URL..."
	@if not defined BASE_URL (set BASE_URL=http://localhost:8000)
	$(PYTHON) scripts/smoke_test.py --base-url $$BASE_URL

# ============================================================================
# Utilities
# ============================================================================
clean:
	@echo "Cleaning..."
	@if exist .venv rmdir /s /q .venv
	@if exist data rmdir /s /q data
	@if exist __pycache__ rmdir /s /q __pycache__
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rmdir /s /q "%%d"
	@for /d /r . %%d in (.mypy_cache) do @if exist "%%d" rmdir /s /q "%%d"

reset: clean setup seed ingest
	@echo "Full reset complete."

# ============================================================================
# Help
# ============================================================================
help:
	@echo "CloudDesk Makefile targets:"
	@echo "  setup              - Create venv, install deps, create .env"
	@echo "  seed               - Load sample data into DB"
	@echo "  ingest             - Chunk and index knowledge base"
	@echo "  backend            - Start FastAPI on :8000"
	@echo "  demo               - Run CD-1002 demo (refund approval)"
	@echo "  demo-CD-1005       - Run CD-1005 demo (escalation)"
	@echo "  test               - Run all backend tests (offline)"
	@echo "  test-*             - Run specific test suite"
	@echo "  lint               - Run ruff + frontend lint"
	@echo "  typecheck          - Run TypeScript type check"
	@echo "  mcp                - Start MCP server"
	@echo "  docker-up          - Build and start all containers"
	@echo "  docker-down        - Stop and remove containers"
	@echo "  terraform-validate - Validate all Terraform configs"
	@echo "  smoke              - Run smoke test (set BASE_URL)"
	@echo "  clean              - Remove venv, data, caches"
	@echo "  reset              - Clean + setup + seed + ingest"