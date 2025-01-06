install:
	python3 -m venv .venv
	. .venv/bin/activate; pip3 install -r requirements.txt --upgrade
	printf '\nrun:\n    source .venv/bin/activate\n\n'

lint:
	black  beancount_share/

test:
	pytest --maxfail=1 -v --cov=beancount_share

clean:
	rm -rf build/* dist/*

build: clean
	python3 setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

.PHONY: init test
