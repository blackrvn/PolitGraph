# PolitGraph

## Beschrieb
Diese Anwendung visualisiert die Ähnlichkeiten zwischen den Parlamentarier:innen des Schweizer Parlamentes. Dadurch sollen Gruppierungen und Verbindungen modelliert und dargestellt werden können.
## Methodik
Es werden die Texte (//TODO: Welche Texte genau ?) über die API abgerufen, lemmatisiert und anschliessend mit einem TF-IDF Algorithmus verarbeitet.
Die dadurch entstehenden Vektoren werden verwendet, um die Ähnlichkeit (Cosinus-Ähnlichkeit) zu bestimmen.
Da die Datengewinnung aufwändig ist, werden die wichtigsten Daten zusammen mit den Vektoren und Ähnlichkeiten lokal in einer (Graph?-)DB abgespeichert.
## Aufbau
### Phase 1 
In der ersten Phase wird die Anwendung stark reduziert und besteht nur aus folgenden Elementen:
- ParliamentServiceClient (kommuniziert mit der API)
- SimilarityService (Berechnet TF-IDF sowie die Ähnlichkeiten)
- Program (Einstiegspunkt für die CLI und gibt nur die berechnete Ähnlichkeit wieder)
- Diverse DTO's

Hierbei wird bewusst auf eine graphische Darstellung, das Speichern sowie das Säubern verzichtet.

#### Usage
``` bash
politgraph <name 1> <name 2>
```
```bash
politgraph "Cyrill Aellen" "Pascal Broulis"
```
### Phase 2
In dieser Phase werden folgende Services ergänzt:
- DBService (Zuständig für das Speichern und Bereitstellen der Ähnlichkeiten)

Die bereits berechneten Ähnlichkeiten werden in der DB gespeichert zwecks schnellerem Abrufen. In dieser Phase ist dies zwar noch nicht essenziell, da der CLI-Command immer noch nur zwei Namen als Argumen aktzeptiert, jedoch ist dies ein wichtiger Schritt für spätere Phasen.
Die DB kann über einen Command aktiv aktualisiert werden.
### Phase 3 
In dieser Phase wird eine graphische Oberfläche erstellt, die das Berechnete Netzwerk als Graph darstellt und gewisse Filter zulässt.
### Phase 4 
Hier wird ein Wizard zur Installation zur Verfügung gestellt sowie ein finaler Clean-Up durchgeführt.
## Termine
Phase 1: 19.01
Phase 2: 02.02 ?? -> Nachfragen zur Einschätzung des Aufwandes
Phase 3.1: 16.02 -> Erster UI Prototyp zum Start von Semester fertig
Phase 3.2: 06.04 -> UI fertigstellen
Phase 4: 06.07
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
https://learn.microsoft.com/en-us/aspnet/core/blazor/components/event-handling?view=aspnetcore-6.0#custom-event-arguments-1


