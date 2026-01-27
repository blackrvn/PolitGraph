main.py wird mithilfe von pyinstaller in ein .exe kompiliert.
Damit alle Abhängigkeiten (inklusive spacy-model) verfügbar sind, benutze folgenden Befehl:
```shell

pyinstaller --onefile --collect-all de_core_news_sm --collect-all spacy --collect-submodules spacy .\main.py

```