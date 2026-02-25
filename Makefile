IMAGE_NAME := localhost/telegram-bot-api-mcp:latest
SERVICE_NAME := telegram-bot-api-mcp


.PHONY: build restart deploy logs

build:
	podman build \
		-t $(IMAGE_NAME) \
		-f Containerfile .

restart:
	systemctl --user daemon-reload
	systemctl --user restart $(SERVICE_NAME)

deploy: build restart

logs:
	journalctl --user -u $(SERVICE_NAME) --since "1 hour ago" -f