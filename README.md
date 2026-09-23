# NLP Application Using Streamlit

Reimplemented using **Claude Code** — a Streamlit web app that detects the language of a text, then translates it or fixes its spelling.

## Features

- **Language detection** (`langdetect`)
- **Translation** to Vietnamese, English, French, Spanish, German, Japanese, Korean, Chinese (`deep-translator`, requires internet)
- **Spelling correction** for en, es, fr, de, pt, ru, ar, eu, lv, nl, it (`pyspellchecker`; Vietnamese is not supported), preserving casing and punctuation

## Setup

Requires Python >= 3.10.

```
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Manual tests

- Translate `Bonjour, comment allez-vous?` to Vietnamese.
- Spellcheck `Yesturday, I recieveed a mesage` -> `Yesterday, I received a message`.
- Text shorter than 3 characters shows a warning and runs no pipeline.

## Project spec

See [CLAUDE.md](CLAUDE.md) for architecture and coding conventions.
