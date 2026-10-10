# Typical flow: make fetch up try PROFILE=qwen3.6-27b
# Run `make` to list targets. Put GATEWAY_API_KEY / VLLM_API_KEY in .env (git-ignored).

PROFILE ?=
SHARDS ?= 4
RUN_DIR ?=
ARGS ?=
GATEWAY = 127.0.0.1:9000

# down/logs/ps need no PROFILE: compose only needs env vars to interpolate, so use any profile.
COMPOSE_PROFILE = $(or $(PROFILE),$(patsubst profiles/%.env,%,$(firstword $(wildcard profiles/*.env))))
COMPOSE = docker compose --env-file profiles/$(COMPOSE_PROFILE).env $(if $(wildcard .env),--env-file .env)
AUTH = $(if $(GATEWAY_API_KEY),-H "Authorization: Bearer $$GATEWAY_API_KEY")

.PHONY: help profiles need-profile fetch up down logs ps status try test parity live lint bench latency index report

help:
	@echo "Targets (PROFILE=<name> is needed where marked):"
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'
	@echo; echo "Profiles:"; $(MAKE) -s profiles

profiles: ## List profile names and models
	@for f in profiles/*.env; do \
		printf '  %-22s %s\n' "$$(basename $$f .env)" "$$(grep '^HF_MODEL=' $$f | cut -d= -f2)"; \
	done

need-profile:
	@[ -n "$(PROFILE)" ] && [ -f "profiles/$(PROFILE).env" ] || { \
		echo "PROFILE=$(PROFILE) is required; one of:" >&2; $(MAKE) -s profiles >&2; exit 2; }

fetch: need-profile ## Download the model weights (PROFILE)
	uv run python scripts/fetch_model.py --profile $(PROFILE)

up: need-profile ## Start or switch the stack, wait until healthy (PROFILE)
	$(COMPOSE) up -d --build --wait --wait-timeout 2400
	@curl -s --max-time 5 $(GATEWAY)/health; echo

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Follow vllm and gateway logs
	$(COMPOSE) logs -f vllm gateway

ps: ## Show container state
	$(COMPOSE) ps

status: ## Print gateway health, exit 1 if down
	@curl -sf --max-time 5 $(GATEWAY)/health && echo || { echo "gateway: down"; exit 1; }

try: ## Send a systemone request and a streaming chat
	curl -s $(GATEWAY)/v1/systemone -H 'content-type: application/json' $(AUTH) -d '{ \
	  "model": "jev-latest", \
	  "state": "My card was charged twice for one order, please refund.", \
	  "questions": { \
	    "team": {"type": "choice", "instructions": "Which team should handle this?", \
	             "criteria": {"billing": null, "technical": null, "sales": null}}, \
	    "urgent": {"type": "noul", "instructions": "Needs a reply today"}}}'
	@echo
	curl -sN $(GATEWAY)/v1/chat/completions -H 'content-type: application/json' $(AUTH) \
	  -d '{"model": "jev-latest", "messages": [{"role": "user", "content": "Say hi"}], "stream": true}'

test: ## Unit tests
	uv run pytest -q

parity: ## Parity tests
	uv run pytest tests/parity -q

live: ## Live tests (stack up and idle)
	uv run pytest -m live tests/live -v

lint: ## Ruff check
	uv run ruff check .

bench: need-profile ## Benchmark; ARGS=--quick for a short run (PROFILE)
	uv run python scripts/bench.py --profile $(PROFILE) $(ARGS)

latency: need-profile ## Latency benchmark (PROFILE)
	uv run python scripts/latency.py --profile $(PROFILE)

index: need-profile ## Decision Index run; SHARDS=4, RUN_DIR=<dir> resumes (PROFILE)
	uv run python scripts/evaluate.py index --profile $(PROFILE) --shards $(SHARDS) --strict $(if $(RUN_DIR),--run-dir $(RUN_DIR))

report: ## Regenerate the Phase 2 README tables
	uv run python scripts/phase2_report.py --readme
