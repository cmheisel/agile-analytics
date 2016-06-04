venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

jira_agile_extractor.egg-info: reqs
	./venv/bin/python setup.py develop

test: jira_agile_extractor.egg-info
	./venv/bin/py.test --flakes --pep8

clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \;

clean: clean_pycs
	rm -rf venv
	rm -rf jira_agile_extractor.egg-info


.PHONY: test clean clean_pycs
