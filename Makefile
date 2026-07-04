.PHONY: install dev build test lint docker-build docker-up clean

# 清除 TRAE 环境可能设置的 Python 干扰变量
UV_RUN = env -u PYTHONHOME -u PYTHONPATH uv run

install:
	cd frontend && pnpm install
	cd backend && uv sync --extra dev

dev:
	@trap 'kill 0' EXIT; \
	(cd backend && $(UV_RUN) uvicorn resume_agent.main:app --reload --port 8000) & \
	(cd frontend && ./node_modules/.bin/vite)

build:
	cd frontend && ./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build

test:
	cd backend && $(UV_RUN) pytest
	cd frontend && ./node_modules/.bin/tsc --noEmit

lint:
	cd backend && $(UV_RUN) ruff check .
	cd frontend && ./node_modules/.bin/tsc --noEmit

docker-build:
	docker compose build

docker-up:
	docker compose up

clean:
	rm -rf frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
