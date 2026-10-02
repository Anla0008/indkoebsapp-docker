# Indkøbsapp med Flask, MariaDB og phpMyAdmin

## Start i VS Code

1. Pak zipfilen ud og åbn mappen `indkoebsapp-docker` i VS Code.
2. Start Docker Desktop på din Mac, og vent til Docker er klar.
3. Åbn en VS Code terminal i samme mappe som `docker-compose.yml`.
4. Kør:

```bash
docker compose up --build
```

Første opstart henter images og installerer Python pakker inde i app imaget. Der kræves ingen lokal `.venv`, pip installation eller MariaDB installation.

Åbn indkøbsappen: **http://localhost:8000**.
Åbn phpMyAdmin: **http://localhost:8080**.

Log ind i phpMyAdmin med `shopping_app` og `shopping_password`. Vælg databasen `shopping_list` og tabellen `items`. Databaseadministratorens login er `root` og `root_password`. Adgangskoderne er lokale eksempelværdier i Compose.

## Hvordan er delene koblet sammen?

- Browseren henter HTML, CSS og JavaScript fra Flask på port 8000.
- JavaScript sender GET, POST, PATCH og DELETE til `/api/items`.
- Flask bruger `x.db()` til at kontakte databaseservicen `mariadb` på port 3306 i Docker netværket.
- MariaDB gemmer varerne i tabellen `items`.
- phpMyAdmin er en separat hjemmeside til at se databasen; appen bruger ikke phpMyAdmin til databasekald.

`x.py` bruger `mysql.connector`, ligesom referenceprojektet. Forbindelsen og dens cursor lukkes i hver routes `finally`. `requirements.txt` installeres under imagebygningen.

## Filer

| Fil | Formål |
| --- | --- |
| `app.py` | Flask routes i try/except/finally struktur |
| `x.py` | Databaseforbindelse og inputvalidering |
| `public/` | HTML, CSS og JavaScript til browseren |
| `items.sql` | Opretter tabellen ved første databaseopstart |
| `requirements.txt` | Python biblioteker til appen |
| `Dockerfile` | Bygger appens image i to faser og kører Flask som non-root bruger |
| `docker-compose.yml` | Starter de tre services, volume og navngivet netværk |
| `.dockerignore` | Undgår at sende fx `.venv` med til imagebygningen |

Dockerfile bruger en non-root bruger i appcontaineren. Det er ikke det samme som at køre hele Docker Engine i rootless mode.

## Test selv

1. Tilføj fx Mælk med antal 2. Genindlæs browseren: varen skal blive stående.
2. Marker varen som købt. Se status både i appen og i phpMyAdmin.
3. Slet en vare. Den skal også forsvinde fra `items`.
4. Tilføj en ny vare, kør `docker compose down` fra en anden terminal i projektmappen, og start igen. Varen skal stadig findes. Dette tester named volume.
5. Ret en overskrift i `public/index.html` og genindlæs browseren. Dette tester bind mount. Python filer genindlæses af Flask automatisk.
6. Kør `docker stats` i en anden terminal for at se CPU og hukommelse.

## Stop og start igen

```bash
docker compose down
docker compose up
```

`down` fjerner containerne og netværket, men bevarer named volume. Brug kun `docker compose down -v`, hvis du vil slette alle indkøbsdata og starte forfra. SQL init scriptet kører kun, når databasevolumen er tomt.

## Fejlfinding

- Hvis Docker ikke svarer, start Docker Desktop.
- Hvis en port er optaget, ændr kun porten på computersiden af mappingen: fx `127.0.0.1:8001:5000`. Åbn derefter localhost:8001.
- Hvis serveren fejler, se `docker compose logs web` og `docker compose logs mariadb`.
- `docker compose config` kontrollerer den samlede Compose konfiguration.
- Efter ændringer i `requirements.txt` eller Dockerfile skal du køre `docker compose up --build` igen.
- Projektet bruger sit eget Compose navn og named volume. Det genbruger ikke Washworlds database.

## Kontrolstatus

Python syntaks, API logik og forbindelseskonfiguration er kontrolleret med simulerede databasekald. Compose YAML er læst og kontrolleret for sammenhæng mellem services, netværk og volume. Docker og MariaDB findes ikke i dette arbejdsområde, så imagebygning, containeropstart og ægte databasekald skal verificeres med testtrinene ovenfor.

Dette er en lokal udviklingsopsætning med Flasks debugserver.
