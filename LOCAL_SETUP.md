# Divine Media 2.0 — Windows Local Development

**Status:** Instructions prepared; the application has not been started on your computer.

## Requirements
- Windows 11 or supported Windows 10, WSL2 and Docker Desktop (Linux containers).
- Prefer at least 16 GB RAM and ample free SSD space for video transcoding.
- Run the commands below in a **WSL Ubuntu terminal**, with Docker Desktop WSL integration enabled.
- Keep the legacy repository on `master`; this setup checks out a **separate upstream AVideo source directory**.

## Install

```bash
docker version
docker compose version
mkdir -p ~/projects/divine-media-2
cd ~/projects/divine-media-2
git clone https://github.com/WWBN/AVideo.git avideo-current
cd avideo-current
git rev-parse HEAD  # record the exact upstream revision used
cp env.example .env
```

Edit `.env` before starting:

```dotenv
SERVER_NAME=localhost
WEBSITE_TITLE=Divine Media
CONTACT_EMAIL=admin@localhost
SYSTEM_ADMIN_PASSWORD=REPLACE_WITH_A_UNIQUE_LONG_PASSWORD
DB_MYSQL_PASSWORD=REPLACE_WITH_ANOTHER_UNIQUE_LONG_PASSWORD
CPUS_LIMIT=2
MEMORY_LIMIT=4G
```

**Do not commit `.env`.** These values are local-development placeholders. Check ports 80, 443, 8080, 8443 and 1935 for conflicts. The upstream Compose stack includes a live server and two databases; it can be resource intensive.

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 avideo
```

Try `https://localhost/` or `http://localhost/`. The upstream configuration attempts TLS certificate setup and may not support localhost without additional configuration; a browser certificate warning or installer error needs troubleshooting, not bypassing on a public host. Do not expose this instance to the internet.

## Verify
1. Log in as `admin` with the configured password.
2. Confirm the site loads and the admin dashboard opens.
3. Create a test user and channel.
4. Upload a small video you own and verify encoding and playback.
5. Check `docker compose ps` and service logs if any component fails.

## Stop without losing databases
```bash
docker compose down
```

**Never use `docker compose down -v` unless intentionally deleting the database volumes.**

## Design next
Once the backend works, test the built-in Flix homepage and branding. Then create a separate modern frontend only for features the built-in design cannot deliver.

## Reference
- https://github.com/WWBN/AVideo#quickstart-docker-compose
- https://github.com/WWBN/AVideo/wiki/Running-AVideo-with-Docker

The upstream Docker Compose quickstart is primarily documented for Linux servers with public domains and HTTPS. Localhost support must be verified during the first run.
