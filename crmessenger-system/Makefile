.PHONY: deploy start stop update rebuild

deploy:
	@cd ..
	@git clone git@github.com:CRMessenger/crmessenger-authorization.git
	@git clone git@github.com:CRMessenger/crmessenger-authentication.git
	@git clone git@github.com:CRMessenger/crmessenger-account.git
	@git clone git@github.com:CRMessenger/crmessenger-telegram.git
	@git clone git@github.com:CRMessenger/crmessenger-whatsapp.git
	@./infrastructure/nginx/install.sh
	@./infrastructure/docker/install.sh


build:
	@docker-compose -f docker-compose.db.yaml up -d --build
	sleep 20
	@docker-compose -f docker-compose.monitoring.yaml up -d --build
	sleep 20
	@docker-compose -f docker-compose.apps.yaml up -d --build

stop:
	@docker-compose -f docker-compose.apps.yaml down
	@docker-compose -f docker-compose.monitoring.yaml down
	@docker-compose -f docker-compose.db.yaml down

update:
	@git pull
	@cd ../crmessenger-authorization/ && git pull && cd ../crmessenger-system/
	@cd ../crmessenger-authentication/ && git pull && cd ../crmessenger-system/
	@cd ../crmessenger-account/ && git pull && cd ../crmessenger-system/
	@cd ../crmessenger-telegram/ && git pull && cd ../crmessenger-system/
	@cd ../crmessenger-whatsapp/ && git pull && cd ../crmessenger-system/

rebuild:
	@update
	@start