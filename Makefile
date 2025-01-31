.PHONY: tests

export EVALUATION_SYSTEM_CONFIG_FILE := $(PWD)/docker/local-eval-system.conf
export EVALUATION_SYSTEM_DRS_CONFIG_FILE := $(PWD)/docker/drs_config.toml
export DJANGO_SUPERUSER_PASSWORD := secret
export DEV_MODE := 1
export DOCKER_ENV_FILE ?= .env
include $(DOCKER_ENV_FILE)
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
	git clone -b stac-catalog https://github.com/FREVA-CLINT/freva-nextgen.git $$TEMP_DIR &&\
	python -m pip install $$TEMP_DIR/freva-rest $$TEMP_DIR/freva-data-portal-worker &&\
	rm -rf $$TEMP_DIR

setup-stac: # this is a setup only for STAC-API and STAC-Browser, and not static STAC
	python -m pip install stac-fastapi.opensearch
	@echo "STAC FastAPI dependencies installed successfully"
	git clone https://github.com/radiantearth/stac-browser.git stac-browser &&\
	cd stac-browser &&\
	npm install

setup-node:
	npm install

runserver:
	@echo "Starting Django development server..."
	python manage.py runserver > runserver.log 2>&1 &
	@echo "Django development server is running..."
	@echo "To watch the Django server logs, run 'tail -f runserver.log'"

runrest:
	@echo "Starting up freva-rest api"
	python docker/config/dev-utils.py redis-config .data-portal-cluster-config.json \
		--user $(REDIS_USER) \
		--passwd $(REDIS_PASSWD) \
		--cert-file $(REDIS_SSL_CERTFILE) \
		--key-file $(REDIS_SSL_KEYFILE)
	python -m data_portal_worker -c .data-portal-cluster-config.json > rest.log 2>&1 &
	python docker/config/dev-utils.py oidc http://localhost:8080/realms/freva/.well-known/openid-configuration
	python -m freva_rest.cli -p 7777 --redis-ssl-keyfile $(REDIS_SSL_KEYFILE) --redis-ssl-certfile $(REDIS_SSL_CERTFILE) --debug --dev >> rest.log 2>&1 &
	@echo "To watch the freva-rest logs, run 'tail -f rest.log'"

runfrontend:
	@echo "Starting npm development server..."
	npm run dev > npm.log 2>&1 &
	@echo "npm development server is running..."
	@echo "To watch the npm logs, run 'tail -f npm.log'"

wait-for-opensearch:
	@echo "wait until openseach wakes up"
	@until curl -s "localhost:9202/_cluster/health" > /dev/null; do \
		echo "we wait 2 secs for OpenSearch to wake up"; \
		sleep 2; \
	done
	@echo "OpenSearch is ready to go, now we have to enable auto index creation"
	@curl -XPUT "localhost:9202/_cluster/settings" -H 'Content-Type: application/json' -d'{ \
		"persistent": { \
			"cluster.blocks.create_index": null, \
			"action.auto_create_index": true \
		} \
	}'

runstac: wait-for-opensearch
	ES_HOST=localhost \
	ES_PORT=9202 \
	ES_USE_SSL=false \
	ES_VERIFY_CERTS=false \
	BACKEND=opensearch \
	ENVIRONMENT=local \
	APP_HOST=0.0.0.0 \
	APP_PORT=8083 \
	STAC_USERNAME=stac \
	STAC_PASSWORD=secret \
	STAC_FASTAPI_TITLE="Freva STAC Service" \
	STAC_FASTAPI_DESCRIPTION="Freva STAC Service provides a SpatioTemporal Asset Catalog API" \
	STAC_FASTAPI_ROUTE_DEPENDENCIES='[{"routes":[{"path":"/collections/{collection_id}/items/{item_id}","method":["PUT","DELETE"]},{"path":"/collections/{collection_id}/items","method":["POST"]},{"path":"/collections","method":["POST"]},{"path":"/collections/{collection_id}","method":["PUT","DELETE"]},{"path":"/collections/{collection_id}/bulk_items","method":["POST"]},{"path":"/aggregations","method":["POST"]},{"path":"/collections/{collection_id}/aggregations","method":["POST"]},{"path":"/aggregate","method":["POST"]},{"path":"/aggregate","method":["POST"]},{"path":"/collections/{collection_id}/aggregate","method":["POST"]}],"dependencies":[{"method":"stac_fastapi.core.basic_auth.BasicAuth","kwargs":{"credentials":[{"username":"stac","password":"secret"}]}}]}]' \
	python -m stac_fastapi.opensearch.app >> stac.log 2>&1 &
	@echo "STAC service is running..."
	@echo "To watch the STAC logs, run 'tail -f stac.log'"
	cd stac-browser && npm start -- --open --catalogUrl=http://localhost:8083 --port 8085 > stac-browser.log 2>&1 &
	@echo "STAC Browser is running..."
	@echo "To watch the STAC Browser logs, run 'tail -f stac-browser.log'"

stopserver:
	ps aux | grep '[f]reva_rest.cli' | awk '{print $$2}' | xargs -r kill
	ps aux | grep '[d]ata_portal_worker' | awk '{print $$2}' | xargs -r kill
	ps aux | grep '[m]anage.py runserver' | awk '{print $$2}' | xargs -r kill
	@if pgrep -f '[s]tac_fastapi.opensearch.app' > /dev/null; then \
		ps aux | grep '[s]tac_fastapi.opensearch.app' | awk '{print $$2}' | head -n 1 | xargs kill; \
		sleep 1; \
	fi
	pkill -f "stac-browser" || true
	rm -fr .data-portal-cluster-config.json
	echo "Stopped Django development server..." > runserver.log
	echo "Stopped freva-rest development server..." > rest.log
	echo "Stopped STAC service..." > stac.log
	echo "Stopped STAC Browser..." >> stac-browser.log

stopfrontend:
	pkill -f "npm run dev"
	echo "Stopped npm development server..." > npm.log

stop: stopserver stopfrontend
	@echo "All services have been stopped."

setup: setup-rest setup-node setup-django dummy-data setup-stac

run: runrest runfrontend runserver runstac

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
