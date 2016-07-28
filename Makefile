venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

agile_analytics.egg-info: reqs
	./venv/bin/python setup.py develop

test: agile_analytics.egg-info
	./venv/bin/py.test -svvx --flake8 --cov=agile_analytics tests/

systest: test tryout.py
	# Poor man's system test, not committed because it requies a real jira
	./venv/bin/python tryout.py

clean_pycs:
	find . -name "*.pyc" -exec rm -rf {} \;
	find . -name "__pycache__" -exec rm -rf {} \;

clean: clean_pycs
	rm -rf venv
	rm -rf agile_analytics.egg-info

docs: reqs
	cd docs && make html


.PHONY: test clean clean_pycs docs climate
