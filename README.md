# First Draft
```
photo-analyzer/              # Główne repo
│
├── analyzer_core/           # Submoduł (jako osobny repozytorium Git)
│   ├── file.py             # Function for working with files
│   ├── face_detector.py
│   ├── tagger.py
│   ├── recognizer.py
│   ├── model_store.py
│   ├── photo.py             # Bazowa klasa Photo + dziedziczenie
│   └── __init__.py
│
├── photo_manager/           # GUI/CLI - osobna aplikacja, osobne repo (drugi submoduł?)
│   ├── cli.py
│   ├── ui_kivy.py           # Wersja z GUI (Kivy)
│   └── commands/            # np. analyze_photo, correct_tags, etc
│
├── models/                  # Zapisane modele użytkownika (face encodings, metadane)
├── data/                    # Przykładowe zdjęcia
└── main.py                  # Entry point

```
