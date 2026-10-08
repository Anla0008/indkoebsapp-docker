# Indkøbsapp med Docker Compose

## Om projektet

Projektet containeriserer en eksisterende indkøbsapp med Python og Flask. Brugeren kan tilføje varer med et antal, se indkøbslisten, markere varer som købt og slette dem. Data gemmes i MariaDB i databasen `to_do` og tabellen `items`.

Docker Compose bygger appens image og starter tre services: `web`, `mariadb` og `phpmyadmin`. Compose håndterer også portmapping, mounts, netværk og opstartsafhængigheder.

## Arkitektur

Browseren åbner Flask på `http://localhost:8000`. Flask leverer HTML, CSS og JavaScript fra `public/`. JavaScript kalder appens API på `/api/items`, og Flask læser og ændrer data i MariaDB via `x.py`.

phpMyAdmin er en separat brugerflade til MariaDB. Databasen ligger i MariaDB; phpMyAdmin bruges til at se og administrere den.

| Service      | Container          | Adgang fra computeren               | Port i containeren |
| ------------ | ------------------ | ----------------------------------- | ------------------ |
| `web`        | `to_do_flask`      | http://localhost:8000               | 5000               |
| `mariadb`    | `to_do_mariadb`    | localhost:3306 til databaseklienter | 3306               |
| `phpmyadmin` | `to_do_phpmyadmin` | http://localhost:8080               | 80                 |

Alle services bruger netværket `to_do_network`. MariaDB gemmer databasefiler i `/var/lib/mysql`, som er koblet til det navngivne volume `mariadb_data`.

## Forudsætninger

- Docker med Docker Compose, eksempelvis Docker Desktop på Mac.
- Docker skal være startet, før kommandoerne køres.
- Internetadgang ved første opstart til images og Pythonpakker.
- Ledige porte: 8000, 8080 og 3306.
- Git, hvis projektet hentes med `git clone`.

Python, MariaDB og Pythonpakkerne behøver ikke være installeret lokalt. De kører i containerne. Projektet bruger aktuelt lokale eksempeladgangskoder direkte i konfigurationen og kræver ingen `.env`-fil.

## Hent og start projektet

Klon repositoryet med dets faktiske URL, eller download og pak det ud. Åbn en terminal i projektmappen, hvor `docker-compose.yml` ligger.

Følgende filer skal være med og have disse navne:

| Fil eller mappe         | Formål                                                               |
| ----------------------- | -------------------------------------------------------------------- |
| `app.py`                | Flaskforside og API med GET, POST, PATCH og DELETE                   |
| `x.py`                  | Databaseforbindelse og validering af input                           |
| `public/`               | Appens HTML, CSS og JavaScript, herunder `index.html`                |
| `requirements.txt`      | Pythonpakker, der installeres under bygning                          |
| `Dockerfile`            | Bygger appens image og definerer startkommandoen                     |
| `docker-compose.yml`    | Konfigurerer services, porte, netværk og mounts                      |
| `to_do_med_indhold.sql` | Opretter tabellen og eksempelvarer ved første databaseinitialisering |

Kontrollér konfigurationen:

```bash
docker compose config
```

Byg og start i baggrunden:

```bash
docker compose up --build -d
docker compose ps
```

Compose venter på, at MariaDBs healthcheck melder databasen klar, før Flask og phpMyAdmin starter. Første opstart kan tage længere tid, fordi images og pakker skal hentes.

Åbn appen på **http://localhost:8000** og phpMyAdmin på **http://localhost:8080**. Brug Flaskadressen til appen; VS Codes Live Server starter ikke Flask eller appens databaseforbindelse.

I phpMyAdmin er brugernavnet `root` og adgangskoden `password`. Vælg databasen `to_do` og tabellen `items`. Dette er lokale eksempelværdier til skoleprojektet, ikke produktionsadgangskoder.

## Databaseinitialisering

`MYSQL_DATABASE: to_do` opretter databasen ved første initialisering. SQLfilen er monteret sådan i MariaDBservicen:

```yaml
- ./to_do_med_indhold.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
```

MariaDB kører initialiseringsscriptet, når databasevolumen er tom. Scriptet opretter `items` med kolonnerne `id`, `name`, `quantity` og `is_bought` og indsætter eksempelvarer. `:ro` betyder, at containeren kun må læse SQLfilen.

Hvis volumen allerede indeholder en database, køres scriptet ikke igen. Ændringer i SQLfilen ændrer derfor ikke automatisk en eksisterende database. Hvis en eksisterende database mangler tabellen, kan SQLfilen importeres via phpMyAdmins Importfunktion. Bevar eksisterende data; slet ikke volumen som rutinemæssig fejlfinding.

## Stop og start igen

```bash
docker compose down
docker compose up -d
```

`down` stopper og fjerner containerne og Compose-netværket. Det navngivne databasevolume bevares. Ved næste opstart tilsluttes volumen igen, så MariaDB bruger de gemte data.

**`docker compose down -v` sletter også databasevolumen og dermed de gemte indkøbsdata. Brug det kun ved en bevidst nulstilling.**

Efter ændringer i Dockerfile eller `requirements.txt` skal appens image bygges igen med `docker compose up --build -d`.

## Dockerkonfiguration

`docker-compose.yml` definerer følgende:

- `web` bygges fra projektets Dockerfile og publicerer port `8000:5000`.
- `mariadb` bruger imaget `mariadb:10.6.20` og gemmer data i et navngivet volume.
- `phpmyadmin` bruger imaget `phpmyadmin/phpmyadmin` og forbinder til `mariadb` via `PMA_HOST`.
- MariaDBs healthcheck bruger `healthcheck.sh --connect --innodb_initialized`. Der kontrolleres hvert 10. sekund med timeout på 5 sekunder, 5 forsøg og en startperiode på 30 sekunder.
- Flask og phpMyAdmin har `depends_on` med `condition: service_healthy`.

Healthcheck kontrollerer databaseparathed. Det kontrollerer ikke i sig selv, om tabellen `items` findes, eller om hele appen virker.

Dockerfile bygger appen i to faser. Første fase installerer Pythonpakker under `/install`. Anden fase kopierer pakkerne og appfilerne ind i runtime-imaget. Begge faser bruger `python:3.12-slim`. Appen kører som `appuser` med UID 10001 og starter Flask på `0.0.0.0:5000` med debug aktiveret.

## Volumes og netværk

| Mount                                                | Type                  | Formål                                                                  |
| ---------------------------------------------------- | --------------------- | ----------------------------------------------------------------------- |
| `mariadb_data:/var/lib/mysql`                        | Navngivet volume      | Bevarer databasefiler, når containerne fjernes                          |
| `.:/app`                                             | Bind mount            | Gør lokale projektfiler tilgængelige i Flaskcontaineren under udvikling |
| SQLfil til `/docker-entrypoint-initdb.d/01-init.sql` | Bind mount, read-only | Leverer SQLscript til første databaseinitialisering                     |

Docker opretter det navngivne volume automatisk. Dets faktiske navn får normalt et Compose-projektpræfiks. Start projektet med samme projektnavn for at bruge samme volume igen.

På `to_do_network` finder Flask databasen via servicenavnet `mariadb` på port 3306. `localhost` inde i Flaskcontaineren ville pege på Flaskcontaineren selv. Browseren bruger derimod computerens publicerede porte, eksempelvis 8000.

Databasens port 3306 er publiceret til computeren, så lokale databaseklienter kan forbinde. Flask og phpMyAdmin bruger den interne forbindelse og behøver ikke denne publicering. En fremtidig opsætning kan fjerne databaseportmappingen, hvis lokale databaseklienter ikke skal bruges.

## Sikkerhed og effektivitet

- Flask kører som en almindelig bruger i containeren. Det er ikke det samme som at køre Docker Engine i rootless mode.
- `python:3.12-slim` er valgt som en mindre base end det fulde Pythonimage.
- To byggefaser adskiller installation fra runtime. Der er ikke dokumenteret en målt størrelsesbesparelse sammenlignet med en enkelt byggefase.
- `pip install --no-cache-dir` undgår at gemme pips downloadcache i byggefase-imaget.
- API'et validerer input og bruger parameteriserede SQLforespørgsler.

Opsætningen er til lokal udvikling. Flask bruger debugserveren, appen forbinder til databasen som `root`, og eksempeladgangskoden står i Compose og `x.py`. Portmappingerne er ikke begrænset eksplicit til `127.0.0.1`. Opsætningen bør tilpasses før offentlig hosting.

## Test og verifikation

### Funktionalitet

1. Åbn appen og kontrollér, at varerne vises.
2. Tilføj en vare med antal 2, og genindlæs. Den skal stadig vises.
3. Marker varen som købt. Kontrollér status i appen og phpMyAdmin.
4. Slet varen. Den skal også forsvinde fra databasen.

### Persistens

Tilføj en vare, kør `docker compose down`, og start igen med `docker compose up -d`. Varen skal stadig findes. Testen kontrollerer, at data bevares i volumen, selv når containerne fjernes.

### Dynamiske ændringer

Ret en synlig overskrift i `public/index.html`, mens Flaskcontaineren kører. Gem og genindlæs browseren. Ændringen skal vises uden en ny imagebygning på grund af bind mountet. Flasks debugfunktion genindlæser Pythonkode ved ændringer.

### Database i terminalen

```bash
docker compose exec mariadb mariadb -u root -p to_do
```

Indtast den lokale eksempeladgangskode, og kør:

```sql
SHOW TABLES;
SELECT * FROM items;
exit;
```

### Status, logs og ressourceforbrug

```bash
docker compose ps
docker compose logs --tail=50
docker stats
```

Stop statsvisningen med `Ctrl+C`; det stopper ikke containerne.

Ved en aflæsning med `docker stats` den 8. oktober 2026, mens de tre containere kørte lokalt, blev følgende observeret:

| Container          | CPU    | Hukommelse |
| ------------------ | ------ | ---------- |
| `to_do_phpmyadmin` | 0,04 % | 122,5 MiB  |
| `to_do_mariadb`    | 0,04 % | 71,1 MiB   |
| `to_do_flask`      | 0,32 % | 55,38 MiB  |

Samlet hukommelsesforbrug var cirka 249 MiB. Det er et øjebliksbillede; belastningen blev ikke registreret systematisk, og målingen er ikke en belastningstest. Den viste hukommelsesgrænse var 3,825 GiB pr. container; det er ikke det faktiske forbrug eller separat reserveret hukommelse.

**Teststatus:** Ressourcemålingen ovenfor er dokumenteret. Resultaterne af funktionstest, persistens, dynamiske ændringer og opstart med tom databasevolume er endnu ikke dokumenteret i denne README. Registrér de faktiske resultater efter gennemførelse; testvejledningerne alene er ikke bevis for, at testene er bestået.

## Fejlfinding

- **Docker kan ikke kontaktes:** Start Docker Desktop og vent, til Docker er klar.
- **Porten er optaget:** Ret computersiden af portmappingen, eksempelvis fra `8000:5000` til `8001:5000`, og åbn localhost:8001.
- **Compose afviser YAML:** Kør `docker compose config`. Topniveauerne `services`, `volumes` og `networks` skal stå helt til venstre.
- **MariaDB er unhealthy:** Kør `docker compose logs --tail=50 mariadb`. Se det konkrete healthcheckresultat med `docker inspect --format '{{json .State.Health}}' to_do_mariadb`.
- **Tabellen mangler:** Kontrollér SQLfilens navn og placering. En eksisterende databasevolume bliver ikke initialiseret igen.
- **Appen fejler:** Kør `docker compose logs --tail=50 web`, og kontrollér databasenavnet `to_do` og forbindelsen til `mariadb` i `x.py`.
- **CSS eller JavaScript mangler:** Åbn appen gennem Flask på localhost:8000, og kontrollér, at de relevante filer findes i `public/`.

## Begrænsninger og næste skridt

Projektet er en lokal udviklingsopsætning uden dokumenteret belastningstest eller eksplicitte CPU- og hukommelsesgrænser. phpMyAdminimage er ikke låst til en bestemt version. Et fast netværksnavn og faste containernavne kan give konflikter, hvis flere kopier startes samtidig på samme Dockerinstallation.

Næste forbedringer er en dedikeret databasebruger med begrænsede rettigheder, konfiguration gennem miljøvariabler, en server egnet til produktion uden Flaskdebug og kun nødvendige publicerede porte. En `.dockerignore` kan holde eksempelvis lokal `.venv` og Gitfiler ude af buildkonteksten. Før aflevering bør en frisk checkout med et separat, tomt databasevolume testes for at kontrollere, at alle nødvendige filer er med, og at automatisk SQLimport virker uden manuel opsætning.
