.PHONY: requirement clean todo

modules=modules
noseopt=

requirement:
	- pip install -r requirements/necessary.rec


pylint:
	pylint $(modules) --max-public-methods=50 --include-ids=y --ignored-classes=Item.Meta --method-rgx='[a-z_][a-z0-9_]{2,40}$$'

todo:
	find . -type f -not -name '*~*' -not -name 'Makefile*' -print0 | xargs -0 -e egrep -n 'todo|TODO|FIXME'

clean:
	-rm *~*
	-rm *.pyc
	-find . -name '*.pyc' -exec rm -f {} \;
	-find . -name '*.orig' -exec rm -f {} \;

#TIP: you can choose which modules to test: for example "make test modules=modules/blog"
test: clean
	#PYTHONPATH=$(PYTHONPATH):. DJANGO_SETTINGS_MODULE=minus.settings nosetests $(noseopt) $(modules)
	python manage.py test --twill-error-dir=/tmp/tddspry --verbosity=2 --nologcapture modules

run:
	PYTHONPATH=$(PYTHONPATH):. DJANGO_SETTINGS_MODULE=minus.settings python manage.py runserver
	
#old host
#remote = ssh -p 58216 minus.lviv@95.169.186.180

host = minus@78.46.38.205
port = 22222
remote = ssh -p $(port) $(host)

deploy: clean
	hg archive -t tgz -X "static/testfiles" minus.tar.gz
	scp -P $(port) minus.tar.gz $(host):~/
	$(remote) "tar xvf ~/minus.tar.gz -C ~/www/ && rm ~/minus.tar.gz"
	$(remote) "cp -r ~/www/minus/static/* ~/www/minus.lvivua/static/"
	$(remote) "touch ~/www/minus_django.wsgi"
	rm minus.tar.gz
	
# TODO: Refactor

devhost = minusdev@78.46.38.205
devremote = ssh -p $(port) $(devhost)
deploydev: clean
	hg archive -t tgz -X "static/testfiles" minus.tar.gz
	scp -P $(port) minus.tar.gz $(devhost):~/
	$(devremote) "tar xvf ~/minus.tar.gz -C ~/www/ && rm ~/minus.tar.gz"
	$(devremote) "cp -r ~/www/minus/static/* ~/www/dev.minus.lviv.ua/static/"
	$(devremote) "touch ~/www/minusdev_django.wsgi"
	rm minus.tar.gz
