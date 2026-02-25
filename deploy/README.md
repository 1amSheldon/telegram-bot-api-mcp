# Podman Quadlet deploy example

The example below is intended for rootless Podman + a systemd user service on a remote server.

## 1) Build the image on the server

From the project root:

```bash
podman build -t localhost/telegram-bot-api-mcp:latest -f Containerfile .
```

## 2) Prepare configuration and data

Create the directory structure (example):

```bash
mkdir -p ~/telegram-bot-api-mcp/data
cp settings.example.toml ~/telegram-bot-api-mcp/settings.toml
```

If needed, put `botapi.json` into `~/telegram-bot-api-mcp/data/`.

## 3) Install the Quadlet file

```bash
mkdir -p ~/.config/containers/systemd
cp deploy/telegram-bot-api-mcp.container ~/.config/containers/systemd/
```

If your paths are different, adjust the `Volume=` lines in the `.container` file.

## 4) Start the service

```bash
systemctl --user daemon-reload
systemctl --user enable --now telegram-bot-api-mcp.service
```

Check status/logs:

```bash
systemctl --user status telegram-bot-api-mcp.service
journalctl --user -u telegram-bot-api-mcp.service -f
```

To enable autostart without an active user session:

```bash
loginctl enable-linger $USER
```
