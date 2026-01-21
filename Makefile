.PHONY: setup ingest run demo clean

# Just set python path to current directory
export PYTHONPATH := $(shell pwd)

setup:
	python3 -m pip install -r requirements.txt
	@echo "Starting Qdrant locally (No Docker required)..."
	@if pgrep qdrant > /dev/null; then \
		echo "Qdrant is already running."; \
	else \
		nohup ./qdrant_bin/qdrant > qdrant.log 2>&1 & \
		echo "Qdrant started in background."; \
	fi
	@echo "Waiting for Qdrant to initialize..."
	sleep 5

stop:
	@echo "Stopping local Qdrant..."
	pkill qdrant || echo "Qdrant not running"

ingest:
	python3 -m scripts.gen_dummy_data
	python3 -m scripts.ingest

run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test-demo:
	python3 -m scripts.demo_cli

clean:
	rm -rf project/data/sample_images/*
	rm -f project/data/*.jsonl
	rm -rf __pycache__
