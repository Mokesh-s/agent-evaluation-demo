setup:
	uv venv
	uv pip install -r requirements.txt

run:
	python -m app.cli

eval:
	python -m evals.run_eval

eval-bug:
	DEMO_BUG=true python -m evals.run_eval

test:
	pytest -q
