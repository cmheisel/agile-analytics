venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

jira_agile_extractor.egg-info: reqs
	./venv/bin/python setup.py develop

test: jira_agile_extractor.egg-info
	./venv/bin/py.test -svv --flake8
	# Poor man's system test, not committed because it requies a real jira
	[ -f tryout.py ] && ./venv/bin/python tryout.py

clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \;

clean: clean_pycs
	rm -rf venv
	rm -rf jira_agile_extractor.egg-info

docs: reqs
	cd docs && make html

.PHONY: test clean clean_pycs docs
