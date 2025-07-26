.PHONY: tests

export EVALUATION_SYSTEM_CONFIG_FILE := $(PWD)/docker/local-eval-system.conf
export EVALUATION_SYSTEM_DRS_CONFIG_FILE := $(PWD)/docker/drs_config.toml
export OIDC_DISCOVERY_URL ?= http://localhost:8080/realms/freva/.well-known/openid-configuration
export DJANGO_SUPERUSER_PASSWORD := secret
export DEV_MODE := 1
export CHAT_BOT := 1
export COLUMNS=250
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
	git clone https://github.com/freva-org/freva-nextgen.git $$TEMP_DIR &&\
	python -m pip install $$TEMP_DIR/freva-rest $$TEMP_DIR/freva-data-portal-worker &&\
	rm -rf $$TEMP_DIR

setup-node:
	npm install

setup-stacbrowser:
	@echo "Setting up STAC Browser..."
	rm -rf static_root/stac-browser
	mkdir -p static_root/stac-browser
	@if [ ! -d "stac-browser" ]; then \
		git clone https://github.com/radiantearth/stac-browser.git stac-browser; \
	fi
	cd stac-browser && \
	npm install && \
	npm run build -- --historyMode="hash" --allowExternalAccess=false && \
	cp -r dist/* ../static_root/stac-browser/

	@APP_JS=$$(ls static_root/stac-browser/js/app.*.js 2>/dev/null | head -1); \
	if [ -n "$$APP_JS" ]; then \
		echo "Found app.js: $$APP_JS"; \
		sed -i 's/catalogUrl:null/catalogUrl:window.STAC_CATALOG_URL/g' "$$APP_JS" 2>/dev/null || sed -i '' 's/catalogUrl:null/catalogUrl:window.STAC_CATALOG_URL/g' "$$APP_JS"; \
		sed -i 's/showThumbnailsAsAssets:!1/showThumbnailsAsAssets:1/g' "$$APP_JS" 2>/dev/null || sed -i '' 's/showThumbnailsAsAssets:!1/showThumbnailsAsAssets:1/g' "$$APP_JS"; \
		echo "Modified: $$APP_JS"; \
	else \
		echo "Error: app.js not found in static_root/stac-browser/js/"; \
		ls -la static_root/stac-browser/js/ || echo "Directory does not exist"; \
		exit 1; \
	fi

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
	python docker/config/dev-utils.py oidc $(OIDC_DISCOVERY_URL)
	python -m freva_rest.cli -p 7777 --services zarr-stream stacapi --oidc-discovery-url $(OIDC_DISCOVERY_URL) --redis-ssl-keyfile $(REDIS_SSL_KEYFILE) --redis-ssl-certfile $(REDIS_SSL_CERTFILE) --oidc-client-id freva --debug --dev >> rest.log 2>&1 &
	@echo "To watch the freva-rest logs, run 'tail -f rest.log'"

runfrontend:
	@echo "Starting npm development server..."
	npm run dev > npm.log 2>&1 &
	@echo "npm development server is running..."
	@echo "To watch the npm logs, run 'tail -f npm.log'"

stopserver:
	ps aux | grep '[m]anage.py runserver' | awk '{print $$2}' | xargs -r kill
	echo "Stopped Django development server..." > runserver.log

stoprest:
	ps aux | grep '[f]reva_rest.cli' | awk '{print $$2}' | xargs -r kill
	ps aux | grep '[d]ata_portal_worker' | awk '{print $$2}' | xargs -r kill
	ps aux | grep '[m]anage.py runserver' | awk '{print $$2}' | xargs -r kill
	rm -fr .data-portal-cluster-config.json
	echo "Stopped freva-rest development server..." > rest.log

stopfrontend:
	pkill -f "npm run dev"
	echo "Stopped npm development server..." > npm.log

stop: stopserver stopfrontend stoprest
	@echo "All services have been stopped."

setup: setup-rest setup-stacbrowser setup-node setup-django dummy-data

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
	curl -H 'Cache-Control: no-cache' -Ls -o bump.py https://raw.githubusercontent.com/freva-org/freva-deployment/main/release.py
	python3 bump.py tag web -v
	rm bump.py
