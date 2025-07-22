VIRTUAL_ENV ?= venv
VIRTUAL_ENV_BIN = $(VIRTUAL_ENV)/bin
ifeq ($(OS), Windows_NT)
	VIRTUAL_ENV_BIN = $(VIRTUAL_ENV)/Scripts
endif
NODE_BIN = node_modules/.bin
SOURCE_DIRS = adhocracy-plus apps tests
ARGUMENTS=$(filter-out $(firstword $(MAKECMDGOALS)), $(MAKECMDGOALS))

ifeq ($(OS), Windows_NT)
	
else
	# for mac os gsed is needed (brew install gnu-sed and brew install gsed)
	SED = sed
	ifneq (, $(shell command -v gsed;))
		SED = gsed
	endif
endif

.PHONY: all
all: help

.PHONY: help
help:
	@echo adhocracy+ development tools
	@echo
	@echo It will either use an exisiting virtualenv if it was entered
	@echo before or create a new one in the venv subdirectory.
	@echo
	@echo usage:
	@echo
	@echo "  make install					-- install dev setup"
	@echo "  make clean						-- delete node modules and venv"
	@echo "  make fixtures					-- load example data"
	@echo "  make server					-- start a dev server"
	@echo "  make watch						-- start a dev server and rebuild js and css files on changes"
	@echo "  make background				-- start background processes"
	@echo "  make test						-- run all test cases"
	@echo "  make pytest					-- run all test cases with pytest"
	@echo "  make pytest-lastfailed			-- run test that failed last"
	@echo "  make pytest-clean				-- test on new database"
	@echo "  make jstest					-- run js tests with coverage"
	@echo "  make jstest-nocov				-- run js tests without coverage"
	@echo "  make jstest-debug				-- run changed tests only, no coverage"
	@echo "  make jstest-updateSnapshots	-- update jest snapshots"
	@echo "  make coverage					-- write coverage report to dir htmlcov"
	@echo "  make lint						-- lint all project files"
	@echo "  make lint-quick				-- lint all files staged in git"
	@echo "  make lint-js-fix				-- fix linting for all js files staged in git"
	@echo "  make lint-html-fix				-- fix linting for all html files passed as argument"
	@echo "  make lint-html-files			-- lint for all html files with django profile rules"
	@echo "  make lint-python-files			-- lint all python files passed as argument"
	@echo "  make po						-- create new po files from the source"
	@echo "  make mo						-- create new mo files from the translated po files"
	@echo "  make release					-- build everything required for a release"
	@echo "  make postgres-start			-- start the local postgres cluster"
	@echo "  make postgres-stop				-- stops the local postgres cluster"
	@echo "  make postgres-create			-- create the local postgres cluster (only works on ubuntu 20.04)"
	@echo "  make local-a4					-- patch to use local a4 (needs to have path ../adhocracy4)"
	@echo "  make celery-worker-start		-- starts the celery worker in the foreground"
	@echo "  make celery-worker-status		-- lists all registered tasks and active worker nodes"
	@echo "  make celery-worker-dummy-task	-- calls the dummy task and prints result from redis"
	@echo "  make docs                   	-- run the mkdocs server for the documentation"
	@echo

.PHONY: install
install:
	npm install --no-save
	npm run build
ifeq ($(OS), Windows_NT)
	make copy-windows-specific-magic-files
	make install-windows-specific-tools
	make setup-windows-specific-local-config
	@powershell -Command "if (!(Test-Path $(VIRTUAL_ENV_BIN)/python.exe)) { python -m venv $(VIRTUAL_ENV) }"
else
	if [ ! -f $(VIRTUAL_ENV_BIN)/python3 ]; then python3 -m venv $(VIRTUAL_ENV); fi
endif
	$(VIRTUAL_ENV_BIN)/python -m pip install --upgrade pip
	$(VIRTUAL_ENV_BIN)/python -m pip install --upgrade -r requirements/dev.txt
	$(VIRTUAL_ENV_BIN)/python manage.py migrate

.PHONY: copy-windows-specific-magic-files
copy-windows-specific-magic-files:
ifeq ($(OS), Windows_NT)
	@powershell -Command "if (!([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { \
		Start-Process wt.exe -ArgumentList 'powershell -NoProfile -ExecutionPolicy Bypass -File \"$(CURDIR)\windows_specific\copy-files-to-system32.ps1\"' -Verb RunAs -Wait; \
		exit; \
	} else { \
		Start-Process wt.exe -ArgumentList 'powershell -NoProfile -ExecutionPolicy Bypass -File \"$(CURDIR)\windows_specific\copy-files-to-system32.ps1\"' -Wait; \
	}"
endif

.PHONY: install-windows-specific-tools
install-windows-specific-tools:
ifeq ($(OS), Windows_NT)
	@powershell -Command " \
		powershell -NoProfile -ExecutionPolicy Bypass -File \"$(CURDIR)\windows_specific\install-tools.ps1\" -Verb RunAs; \
	"
endif

.PHONY: setup-windows-specific-local-config
setup-windows-specific-local-config:
ifeq ($(OS), Windows_NT)
	@powershell -Command " \
		powershell -NoProfile -ExecutionPolicy Bypass -File \"$(CURDIR)\windows_specific\setup-local-config.ps1\" -Verb RunAs; \
	"
endif

.PHONY: clean
clean:
ifeq ($(OS), Windows_NT)
	@powershell -Command "if (Test-Path package-lock.json) { Remove-Item package-lock.json }"
	@powershell -Command "if (Test-Path node_modules) { Remove-Item node_modules -Recurse -Force }"
	@powershell -Command "if (Test-Path venv) { Remove-Item venv -Recurse -Force }"
else
	if [ -f package-lock.json ]; then rm package-lock.json; fi
	if [ -d node_modules ]; then rm -rf node_modules; fi
	if [ -d venv ]; then rm -rf venv; fi
endif

.PHONY: fixtures
fixtures:
	$(VIRTUAL_ENV_BIN)/python manage.py loaddata adhocracy-plus/fixtures/site-dev.json
	$(VIRTUAL_ENV_BIN)/python manage.py loaddata adhocracy-plus/fixtures/users-dev.json
	$(VIRTUAL_ENV_BIN)/python manage.py loaddata adhocracy-plus/fixtures/orga-dev.json

.PHONY: server
server:
	$(VIRTUAL_ENV_BIN)/python manage.py runserver 8004

.PHONY: watch
watch:
ifeq ($(OS), Windows_NT)
	trap 'kill %1' KILL; \
	npm run watch & \
	$(VIRTUAL_ENV)\Scripts\python manage.py runserver 8004
else
	trap 'kill %1' KILL; \
	npm run watch & \
	$(VIRTUAL_ENV)/bin/python manage.py runserver 8004
endif

.PHONY: background
background:
	$(VIRTUAL_ENV_BIN)/python manage.py process_tasks

.PHONY: test
test:
	$(VIRTUAL_ENV_BIN)/py.test --reuse-db
	npm run testNoCov

.PHONY: pytest
pytest:
	$(VIRTUAL_ENV_BIN)/py.test --reuse-db

.PHONY: pytest-lastfailed
pytest-lastfailed:
	$(VIRTUAL_ENV_BIN)/py.test --reuse-db --last-failed

.PHONY: pytest-clean
pytest-clean:
	if [ -f test_db.sqlite3 ]; then rm test_db.sqlite3; fi
	$(VIRTUAL_ENV_BIN)/py.test

.PHONY: jstest
jstest:
	npm run test

.PHONY: jstest-nocov
jstest-nocov:
	npm run testNoCov

.PHONY: jstest-debug
jstest-debug:
	npm run testDebug

.PHONY: jstest-updateSnapshots
jstest-updateSnapshots:
	npm run updateSnapshots

.PHONY: coverage
coverage:
	$(VIRTUAL_ENV_BIN)/py.test --reuse-db --cov --cov-report=html

.PHONY: lint
lint:
ifeq ($(OS), Windows_NT)
	@powershell -Command "& { \
		$$EXIT_STATUS = 0; \
		& $(VIRTUAL_ENV_BIN)\isort.exe --diff -c $(SOURCE_DIRS); if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		& $(VIRTUAL_ENV_BIN)\flake8.exe $(SOURCE_DIRS) --exclude migrations,settings; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		npm run lint; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		& $(VIRTUAL_ENV_BIN)\python.exe manage.py makemigrations --dry-run --check --noinput; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		exit $$EXIT_STATUS; \
	}"
else
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV_BIN)/isort --diff -c $(SOURCE_DIRS) ||  EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV_BIN)/flake8 $(SOURCE_DIRS) --exclude migrations,settings ||  EXIT_STATUS=$$?; \
	npm run lint ||  EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV_BIN)/python manage.py makemigrations --dry-run --check --noinput || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}
endif


.PHONY: lint-quick
lint-quick:
ifeq ($(OS), Windows_NT)
	@powershell -Command "& { \
		$$EXIT_STATUS=0; \
		npm run lint-staged; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		& $(VIRTUAL_ENV_BIN)\python.exe manage.py makemigrations --dry-run --check --noinput; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		exit $$EXIT_STATUS; \
	}"
else
	EXIT_STATUS=0; \
	npm run lint-staged ||  EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV_BIN)/python manage.py makemigrations --dry-run --check --noinput || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}
endif

.PHONY: lint-js-fix
lint-js-fix:
ifeq ($(OS), Windows_NT)
	@powershell -Command "& { \
		$$EXIT_STATUS=0; \
		npm run lint-fix; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		exit $$EXIT_STATUS; \
	}"
else
	EXIT_STATUS=0; \
	npm run lint-fix ||  EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}
endif

# Use with caution, the automatic fixing might produce bad results
.PHONY: lint-html-fix
lint-html-fix:
ifeq ($(OS), Windows_NT)
	@powershell -Command "& { \
		$$EXIT_STATUS=0; \
		& $(VIRTUAL_ENV_BIN)\djlint.exe $(ARGUMENTS) --reformat --profile=django; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		exit $$EXIT_STATUS; \
	}"
else
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV_BIN)/djlint $(ARGUMENTS) --reformat --profile=django || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}
endif

.PHONY: lint-html-files
lint-html-files:
ifeq ($(OS), Windows_NT)
	@powershell -Command "& { \
		$$EXIT_STATUS=0; \
		& $(VIRTUAL_ENV_BIN)\djlint.exe $(ARGUMENTS) --profile=django --ignore=H006,H030,H031,H037,T002; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		exit $$EXIT_STATUS; \
	}"
else
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV_BIN)/djlint $(ARGUMENTS) --profile=django --ignore=H006,H030,H031,H037,T002 || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}
endif

.PHONY: lint-python-files
lint-python-files:
ifeq ($(OS), Windows_NT)
	@powershell -Command "& { \
		$$EXIT_STATUS=0; \
		& $(VIRTUAL_ENV_BIN)\black.exe $(ARGUMENTS); if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		& $(VIRTUAL_ENV_BIN)\isort.exe $(ARGUMENTS) --filter-files; if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		& $(VIRTUAL_ENV_BIN)\flake8.exe $(ARGUMENTS); if ($$LASTEXITCODE -ne 0) { $$EXIT_STATUS = $$LASTEXITCODE }; \
		exit $$EXIT_STATUS; \
	}"
else
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV_BIN)/black $(ARGUMENTS) || EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV_BIN)/isort $(ARGUMENTS) --filter-files || EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV_BIN)/flake8 $(ARGUMENTS) || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}
endif

.PHONY: po
po:
	$(VIRTUAL_ENV_BIN)/python manage.py makemessages --all --no-obsolete -d django --extension html,email,py --ignore '$(CURDIR)/node_modules/adhocracy4/adhocracy4/*'
	$(VIRTUAL_ENV_BIN)/python manage.py makemessages --all --no-obsolete -d djangojs --ignore '$(VIRTUAL_ENV)/*' --ignore '$(CURDIR)/node_modules/dsgvo-video-embed/dist/*'
	$(foreach file, $(wildcard locale-*/locale/*/LC_MESSAGES/django*.po), \
		$(SED) -i 's%#: .*/adhocracy4%#: adhocracy4%' $(file);)
	$(foreach file, $(wildcard locale-*/locale/*/LC_MESSAGES/django*.po), \
		$(SED) -i 's%#: .*/dsgvo-video-embed/js%#: dsgvo-video-embed/js%' $(file);)
	msgen locale-source/locale/en/LC_MESSAGES/django.po -o locale-source/locale/en/LC_MESSAGES/django.po
	msgen locale-source/locale/en/LC_MESSAGES/djangojs.po -o locale-source/locale/en/LC_MESSAGES/djangojs.po

.PHONY: mo
mo:
	$(VIRTUAL_ENV_BIN)/python manage.py compilemessages

.PHONY: release
release: export DJANGO_SETTINGS_MODULE ?= adhocracy-plus.config.settings.build
release:
	npm install --silent
	npm run build:prod
	$(VIRTUAL_ENV_BIN)/python -m pip install -r requirements.txt -q
	$(VIRTUAL_ENV_BIN)/python manage.py compilemessages -v0
	$(VIRTUAL_ENV_BIN)/python manage.py collectstatic --noinput -v0

.PHONY: postgres-start
postgres-start:
	sudo -u postgres PGDATA=pgsql PGPORT=5556 /usr/lib/postgresql/12/bin/pg_ctl start

.PHONY: postgres-stop
postgres-stop:
	sudo -u postgres PGDATA=pgsql PGPORT=5556 /usr/lib/postgresql/12/bin/pg_ctl stop

.PHONY: postgres-create
postgres-create:
	if [ -d "pgsql" ]; then \
		echo "postgresql has already been initialized"; \
	else \
		sudo install -d -m 774 -o postgres -g $(USER) pgsql; \
		sudo -u postgres /usr/lib/postgresql/12/bin/initdb pgsql; \
		sudo -u postgres PGDATA=pgsql PGPORT=5556 /usr/lib/postgresql/12/bin/pg_ctl start; \
		sudo -u postgres PGDATA=pgsql PGPORT=5556 /usr/lib/postgresql/12/bin/createuser -s django; \
		sudo -u postgres PGDATA=pgsql PGPORT=5556 /usr/lib/postgresql/12/bin/createdb -O django django; \
	fi

.PHONY: local-a4
local-a4:
	if [ -d "../adhocracy4" ]; then \
		$(VIRTUAL_ENV_BIN)/python -m pip install --upgrade ../adhocracy4; \
		$(VIRTUAL_ENV_BIN)/python manage.py migrate; \
		npm link ../adhocracy4; \
	fi

.PHONY: celery-worker-start
celery-worker-start:
	$(VIRTUAL_ENV_BIN)/celery --app adhocracy-plus worker --loglevel INFO

.PHONY: celery-worker-status
celery-worker-status:
	$(VIRTUAL_ENV_BIN)/celery --app adhocracy-plus inspect registered

.PHONY: celery-worker-dummy-task
celery-worker-dummy-task:
	$(VIRTUAL_ENV_BIN)/celery --app adhocracy-plus call dummy_task | awk '{print "celery-task-meta-"$$0}' | xargs redis-cli get | python3 -m json.tool

.PHONY: docs
docs:
	$(VIRTUAL_ENV_BIN)/mkdocs serve
