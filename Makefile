venv:
	virtualenv ./venv

reqs: venv
	./venv/bin/pip install -r requirements.txt

test: reqs
	./venv/bin/python setup.py develop
	./venv/bin/py.test --flakes --pep8

clean:
	rm -rf venv

.PHONY: reqs, test, clean
