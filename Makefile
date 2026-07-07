.PHONY: test lint clean web demo

test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

clean:
	rm -rf .harness/trace/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/

web:
	streamlit run src/agent_harness/web/theater.py

demo:
	python -m demo.demo_guardrail
	python -m demo.demo_feedback
	python -m demo.demo_scope