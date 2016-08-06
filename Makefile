venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt && touch reqs

agile_analytics.egg-info/PKG-INFO: reqs
	./venv/bin/python setup.py develop

test: agile_analytics.egg-info/PKG-INFO
	./venv/bin/py.test -svv --flake8
	./venv/bin/py.test -svv --cov=agile_analytics tests/

systest: test tryout.py
	# Poor man's system test, not committed because it requies a real jira
	./venv/bin/python tryout.py

clean_pycs:
	find . | grep -E "(__pycache__|\.pyc)" | xargs rm -rf

clean: clean_pycs
	rm -rf sdist-venv
	rm -rf .coverage
	rm -rf .cache
	rm -rf reqs
	rm -rf venv
	rm -rf agile_analytics.egg-info
	rm -rf dist

docs: reqs
	cd docs && make html

version: agile_analytics.egg-info/PKG-INFO
	./venv/bin/python -c "import agile_analytics; open('version.txt', 'w').write(agile_analytics.version)"
	git add agile_analytics/version.py
	git add version.txt
	git commit -m "Version bump."

test_sdist: test version clean
	python setup.py sdist
	virtualenv ./sdist-venv
	./sdist-venv/bin/pip install ./dist/*.tar.gz
	./sdist-venv/bin/python -c "import agile_analytics; assert agile_analytics"

.PHONY: test clean clean_pycs docs version systest
