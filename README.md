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