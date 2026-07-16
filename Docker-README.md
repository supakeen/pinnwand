# Running pinnwand with Docker

## Quick start

### Building from source

1. Clone the repository and enter it:
   ```
   git clone https://github.com/supakeen/pinnwand
   cd pinnwand
   ```

2. Copy the example configuration:
   ```
   cp etc/pinnwand.toml-example etc/pinnwand.toml
   ```

3. Edit `etc/pinnwand.toml` to your liking — at minimum set `base_url`.

4. Start the container:
   ```
   docker compose up -d --build
   ```

### Pulling from a registry

1. Pull the `compose.yml` and the example configuration from the repository,
   or copy them manually:
   ```
   curl -O https://raw.githubusercontent.com/supakeen/pinnwand/master/compose.yml
   curl -O https://raw.githubusercontent.com/supakeen/pinnwand/master/etc/pinnwand.toml-example
   mv pinnwand.toml-example pinnwand.toml
   ```

2. Edit `pinnwand.toml` to your liking — at minimum set `base_url`.

3. Start the container:
   ```
   docker compose up -d
   ```

## Configuration

The container reads its configuration from `pinnwand.toml` mounted at
`/etc/pinnwand.toml`. The example file at `etc/pinnwand.toml-example` documents
all available options.

Pinnwand listens on `http://127.0.0.1:1377` and is designed to run behind a
reverse proxy (nginx, Apache, Caddy, etc.) for HTTPS termination.

## Persistent storage

By default, pinnwand uses an in-memory SQLite database and **pastes will be
lost when the container restarts**. To persist pastes, use a SQLite file on
disk:

1. Set `database_uri` in `pinnwand.toml`:
   ```toml
   database_uri = "sqlite:////data/pinnwand.db"
   ```

2. Create the database file before starting the container (Docker will otherwise
   create it as a directory):
   ```
   touch pinnwand.db
   ```

3. Uncomment the volume line in `compose.yml`:
   ```yaml
   - ./pinnwand.db:/data/pinnwand.db
   ```

4. Restart the container:
   ```
   docker compose up -d
   ```

For higher-traffic instances, pinnwand also supports PostgreSQL and
MySQL/MariaDB — see `etc/pinnwand.toml-example` for the `database_uri` format.
