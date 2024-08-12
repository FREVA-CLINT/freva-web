.PHONY: tests

export EVALUATION_SYSTEM_CONFIG_FILE := $(PWD)/docker/local-eval-system.conf
export EVALUATION_SYSTEM_DRS_CONFIG_FILE := $(PWD)/docker/drs_config.toml
export DJANGO_SUPERUSER_PASSWORD := secret
export DEV_MODE := 1
export ENV_FILE ?= .env
export RE
include $(ENV_FILE)
export

.PHONY: all run runserver runfrontend stopserver stopfrontend stop setup


all: setup runserver runfrontend
	@echo "All services are running in the background."

dummy-data:
	docker/dummy_plugin_runs.sh

setup-django:
	python manage.py makemigrations base
	python manage.py migrate --fake-initial
	python manage.py migrate --fake contenttypes
	python manage.py createsuperuser --noinput --username admin --email foo@bar.com.au || echo

setup-rest:
	TEMP_DIR=$$(mktemp -d) && \
	git clone https://github.com/FREVA-CLINT/freva-nextgen.git $$TEMP_DIR &&\
	$$(which python) -m pip install $$TEMP_DIR/freva-rest $$TEMP_DIR/freva-data-portal-worker &&\
	rm -rf $$TEMP_DIR

setup-node:
	npm install

runserver:
	@echo "Starting Django development server..."
	python manage.py runserver > runserver.log 2>&1 &
	@echo "Django development server is running..."
	@echo "To watch the Django server logs, run 'tail -f runserver.log'"

runrest:
	@echo "Starting up freva-rest api"
	@echo $(ENV_FILE)
	@echo $(REDIS_SSL_CERTFILE)
	python docker/config/dev-utils.py redis-config .data-portal-cluster-config.json \
		--user $(REDIS_USER) \
		--passwd $(REDIS_PASSWD) \
		--cert-file $(REDIS_SSL_CERTFILE) \
		--key-file $(REDIS_SSL_KEYFILE)
	$$(which python) -m data_portal_worker -c .data-portal-cluster-config.json > rest.log 2>&1 &
	python docker/config/dev-utils.py oidc http://localhost:8080/realms/freva/.well-known/openid-configuration
	$$(which python) -m freva_rest.cli -p 7777 --tls-key $(REDIS_SSL_KEYFILE) --tls-cert $(REDIS_SSL_CERTFILE) --debug --dev >> rest.log 2>&1 &
	@echo "To watch the freva-rest logs, run 'tail -f rest.log'"

runfrontend:
	@echo "Starting npm development server..."
	npm run dev > npm.log 2>&1 &
	@echo "npm development server is running..."
	@echo "To watch the npm logs, run 'tail -f npm.log'"

stopserver:
	ps aux | grep '[f]reva_rest.cli' | awk '{print $$2}' | xargs -r kill
	ps aux | grep '[d]ata_portal_worker' | awk '{print $$2}' | xargs -r kill
	ps aux | grep '[m]anage.py runserver' | awk '{print $$2}' | xargs -r kill
	rm -fr .data-portal-cluster-config.json
	echo "Stopped Django development server..." > runserver.log
	echo "Stopped freva-rest development server..." > rest.log


stopfrontend:
	pkill -f "npm run dev"
	echo "Stopped npm development server..." > npm.log

stop: stopserver stopfrontend
	@echo "All services have been stopped."

setup: setup-rest setup-node setup-django dummy-data

run: runrest runfrontend runserver

lint: setup-node
	npm run lint-format
	npm run lint
	isort -c --profile black -t py312 .

tests: setup-node
	npm run build-production
	npm run build
	rm -rf node_modules
	pytest -vv $(PWD) tests/

release:
	pip install git-python requests packaging tomli
	curl -H 'Cache-Control: no-cache' -Ls -o bump.py https://raw.githubusercontent.com/FREVA-CLINT/freva-deployment/main/release.py
	python3 bump.py tag web -v
	rm bump.py
