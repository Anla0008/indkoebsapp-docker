# Shopping List App with Docker Compose

## 1. Overview

An existing Flask app containerised with Docker Compose.
Users can add items with quantities, mark them as bought and delete them.
MariaDB stores the data in `to_do.items`; phpMyAdmin provides a database interface.

## 2. Requirements

- Docker with Compose support, running locally.
- Internet access for the first build.
- Available ports: 8000 and 8080;

No local Python or MariaDB installation is required. The current setup uses local example credentials and requires no `.env` file.

## 3. Run and Stop

Clone or download the repository. Open a terminal in the folder containing `docker-compose.yml`:

```bash
docker compose config
docker compose up --build
docker compose ps
```

- App: http://localhost:8000
- phpMyAdmin: http://localhost:8080
- Database login: `root` / `password`. Select `to_do`, then `items`

Stop and remove containers:

```bash
docker compose down
```

Restart with `docker compose up`
Rebuild with `docker compose up --build` after changes to Dockerfile or `requirements.txt`

## 4. Services and Configuration

| Service      | Container          | Access from the computer          | Port in the container |
| ------------ | ------------------ | --------------------------------- | --------------------- |
| `web`        | `to_do_flask`      | http://localhost:8000             | 5000                  |
| `mariadb`    | `to_do_mariadb`    | localhost:3306 to databaseclients | 3306                  |
| `phpmyadmin` | `to_do_phpmyadmin` | http://localhost:8080             | 80                    |

The browser loads files from `public/` through Flask
JavaScript calls `/api/items`;
Flask connects to MariaDB through `x.py`
All services share `to_do_network`, using `mariadb:3306` for database connections.

Compose defines services, ports, mounts and the healthcheck. Flask and phpMyAdmin wait for MariaDB via `condition: service_healthy`. The healthcheck checks connectivity and InnoDB readiness.

Keep `app.py`, `x.py`, `public/`, `requirements.txt`, `Dockerfile`, `docker-compose.yml` and `to_do_med_indhold.sql` in the repository.

## 5. Database and Persistence

| Mount                                                 | Type                 | Purpose                                                   |
| ----------------------------------------------------- | -------------------- | --------------------------------------------------------- |
| `mariadb_data:/var/lib/mysql`                         | Named volume         | Preserve database files when containers are removed       |
| `.:/app`                                              | Bind mount           | Make local project files available in the Flask container |
| SQL file to `/docker-entrypoint-initdb.d/01-init.sql` | Read-only bind mount | Supply the SQL script for initial database setup          |

Mount `./to_do_med_indhold.sql` at `/docker-entrypoint-initdb.d/01-init.sql` with `:ro` in Compose. `MYSQL_DATABASE` creates `to_do`. The SQL script creates `items` with `id`, `name`, `quantity` and `is_bought`. It runs only when the database volume is empty. For an existing database missing the table, import the SQL file through phpMyAdmin.

`docker compose down` preserves the volume. **`docker compose down -v` deletes it and its database data.**

## 6. Security and Efficiency

The Dockerfile uses two build stages with `python:3.12-slim`: one installs dependencies; the other runs the app as `appuser` (UID 10001). The API validates input and uses parameterised SQL queries.

This is a local development setup: Flask debug is enabled, the app uses the database root account, and credentials are stored in the YAML file.

## 7. Testing & Verification

| Test                                | Expected result                    |
| ----------------------------------- | ---------------------------------- |
| Add an item and reload              | Item remains visible               |
| Mark an item as bought or delete it | Database reflects the change       |
| Add an item, run `down`, then `up`  | Item survives container recreation |

Inspect status, logs and resource usage:

```bash
docker compose ps
docker compose logs --tail=50
docker stats
```

Inspect the table from the terminal:

```bash
docker compose exec mariadb mariadb -u root -p to_do
```

Enter `password`, then run:

```sql
SHOW TABLES
SELECT * FROM items;
exit;
```

## 8. Limitations and Next Steps

No documented load test or explicit CPU/memory limits. The phpMyAdmin image is not version-pinned, and fixed container/network names can conflict with another copy of the project.

Future improvements: a restricted database user, environment-based configuration, a production server without debug, fewer published ports. Verify automatic SQL setup using a fresh checkout and a separate empty database volume before submission.
