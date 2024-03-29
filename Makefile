
develop:
	pip install -e .[dev]

clean_so:
	find fluidlab -name "*.so" -delete

black:
	black -l 82 .

tests:
	pytest fluidlab

tests_coverage:
	mkdir -p .coverage
	coverage run -p -m pytest fluidlab

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage: tests_coverage report_coverage
