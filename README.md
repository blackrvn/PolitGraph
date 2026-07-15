# PolitGraph

## Beschrieb
Diese Anwendung visualisiert die Ähnlichkeiten zwischen den Parlamentarier:innen des Schweizer Parlamentes. Dadurch sollen Gruppierungen und Verbindungen modelliert und dargestellt werden können.
## Methodik
Es werden alle deutschen Geschäftstexte über die API abgerufen, lemmatisiert und anschliessend mit einem Doc2Vec Modell vektorisiert.
Die dadurch entstehenden Vektoren werden verwendet, um die Ähnlichkeit (Cosinus-Ähnlichkeit) zu bestimmen.
Da die Datengewinnung aufwändig ist, werden die wichtigsten Daten zusammen mit den Vektoren und Ähnlichkeiten in einer Datenbank gespeichert.

## Deployment
### Images
Die Github workflows werden Images erstellen, auf die Registry pushen und sicherstellen, dass der Server die neuste Version pulled. 

### .env Setup
Um die Container auf einem Server laufen lassen zu können werden folgende Umgebungsvariablen benötigt.
```bash
REGISTRY=ghcr.io
IMAGE_NAME=blackrvn/politgraph
TAG=latest

POSTGRES=***
READER_PASSWORD=***
WRITER_PASSWORD=***
```

### Datenbank-Initialisierung
Beim ersten Start wird `init.sh` automatisch ausgeführt (via `/docker-entrypoint-initdb.d/`).
Das Script erstellt die Rollen (`reader`, `writer`) mit entsprechenden Berechtigungen sowie alle Tabellen (`vector`, `member`, `affair`, `edge`).

> **Hinweis:** Das Script wird nur bei einem frischen Volume ausgeführt. Bei einem bestehenden Volume wird es ignoriert.

### Docker Compose
Die Container werden mit dem `docker-compose.yml` file orchestriert.

### Befehle
```bash
# Images aktualisieren
docker compose pull

# UI und DB starten
docker compose up -d

# Update manuell starten
docker compose run --rm update

# Update mit anderen Argumenten starten
docker compose run --rm -d update --threshold 0.5

# Logs des Update-Containers anzeigen
docker logs politgraph-update

# Alle Container stoppen
docker compose down
```

### Cronjob
Der `update` Container wird immer montags über einen Cronjob auf dem Hostsystem gestartet:
```
0 0 * * 1 ~/politgraph/cron.update-db.sh
```

## Quellen

API: https://api.openparldata.ch/v1/

API-Dokumentation: https://api.openparldata.ch/documentation#/

## Lizenzen 

### httpx
[Copyright © 2019, Encode OSS Ltd. All rights reserved](https://github.com/encode/httpx?tab=BSD-3-Clause-1-ov-file)


### numpy
[Copyright (c) 2005-2025, NumPy Developers.All rights reserved.](https://github.com/numpy/numpy/blob/main/LICENSE.txt)


### scipy
[Copyright (c) 2001-2002 Enthought, Inc. 2003, SciPy Developers.All rights reserved.](https://github.com/scipy/scipy?tab=BSD-3-Clause-1-ov-file)

### tqdm
[Copyright (c) 2013 noamraph](https://github.com/tqdm/tqdm?tab=License-1-ov-file)

### BeautifulSoup
[Crummy is © 1996-2026 Leonard Richardson. Unless otherwise noted, all text licensed under a Creative Commons License.](https://www.crummy.com/software/BeautifulSoup/)

### spacy
[Copyright (C) 2016-2024 ExplosionAI GmbH, 2016 spaCy GmbH, 2015 Matthew Honnibal](https://github.com/explosion/spaCy?tab=MIT-1-ov-file)

### nltk
[Apache License Version 2.0, January 2004](https://github.com/nltk/nltk?tab=Apache-2.0-1-ov-file)

### gensim
[GNU LESSER GENERAL PUBLIC LICENSE](https://github.com/piskvorky/gensim?tab=LGPL-2.1-1-ov-file)

### sklearn
[Copyright (c) 2007-2026 The scikit-learn developers. All rights reserved.](https://github.com/scikit-learn/scikit-learn?tab=BSD-3-Clause-1-ov-file)


## Nützliche Links
[JsInterop Events](https://learn.microsoft.com/en-us/aspnet/core/blazor/components/event-handling?view=aspnetcore-6.0#custom-event-arguments-1)
[JsInterop](https://learn.microsoft.com/en-us/aspnet/core/blazor/javascript-interoperability/?view=aspnetcore-9.0)
[Dockerize Python](https://docs.docker.com/guides/python/containerize/)


