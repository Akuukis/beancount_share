init:
	pip3 install -r requirements.txt

lint:
	black  beancount_share/

test:
	pytest --maxfail=1 --verbose -vv

clean:
	rm -rf build/* dist/*

build: clean
	python3 setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

.PHONY: init test
