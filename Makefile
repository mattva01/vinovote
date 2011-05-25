#!/usr/bin/make

BOOTSTRAP_PYTHON=python2.6

.PHONY: build
build: installed

.PHONY: bootstrap
bootstrap installed: 
	$(BOOTSTRAP_PYTHON) bootstrap.py .
	touch installed

.PHONY: update
update:
	git pull


.PHONY: run
run: build
	bin/python manage.py syncdb
	bin/python manage.py runserver 0.0.0.0:8000
	


.PHONY: clean
clean:
	rm -rf bin
	rm -rf include
	rm -rf lib
	rm lib64
	rm vinodatabase
	rm installed
	find . -name '*.py[co]' -delete
# Helpers

.PHONY: ubuntu-environment
ubuntu-environment:
	sudo apt-get install git build-essential

