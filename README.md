# Socrates Leertool Argumenteren

Een educatieve tool voor basisschoolleerlingen (bovenbouw) om argumenteren te oefenen via gesimuleerde online discussies.

## Features

- **10 unieke agents** met verschillende persoonlijkheden en standpunten
- **RAG systeem** met PRO, CONTRA en FAKENEWS bronnen
- **Discussiemeester** met uitleg op 3 niveaus (groep 6/7/8)
- **Bronnen checker** om te zien waar informatie vandaan komt
- **Logging** voor onderzoek en analyse

## Structuur

```
leertool/
├── app.py                  # Streamlit entry point
├── core/                   # Core logica (UI-onafhankelijk)
│   ├── config.py           # Stelling configuratie
│   ├── engine.py           # Hoofd logica
│   ├── agents/             # Agent definities
│   ├── llm/                # LLM client integratie
│   ├── rag/                # RAG database
│   └── utils/              # Hulpfuncties
├── documents/              # RAG bronnen
│   └── elektrische_autos/
│       ├── PRO/
│       ├── CONTRA/
│       └── FAKENEWS/
├── assets/                 # Afbeeldingen
│   ├── socrates_header.jpeg
│   └── avatars/
└── requirements.txt
```

## Installatie (lokaal)

```bash
pip install -r requirements.txt
```

Maak een `config.py` aan met je API keys:

```python
API_KEYS = {
    "model_1": {
        "provider": "anthropic",
        "api_key": "sk-ant-...",
        "model_name": "claude-sonnet-4-20250514"
    },
    # ... meer modellen
}
```

Start de app:

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push naar GitHub
2. Ga naar share.streamlit.io
3. Deploy vanuit je repository
4. Voeg Secrets toe in Settings:

```toml
[api_keys.model_1]
provider = "anthropic"
api_key = "sk-ant-..."
model_name = "claude-sonnet-4-20250514"

[api_keys.model_2]
provider = "openai"
api_key = "sk-..."
model_name = "gpt-4o"
```

## Stelling wijzigen

In `core/config.py`:

```python
ACTIEVE_STELLING_ID = "elektrische_autos"  # of "social_media", etc.
```

Voeg documenten toe in de juiste folder:
- `documents/{stelling_id}/PRO/`
- `documents/{stelling_id}/CONTRA/`
- `documents/{stelling_id}/FAKENEWS/`

## Document formaat

```
---
bron: TNO
auteur: TNO Onderzoek
datum: 2024-01-15
url: https://...
type: artikel
---

De eigenlijke tekst hier...
```

Types: `artikel`, `social_media`, `complot`, `onzin`

## Auteur

Johan Schokker - Boom Publishers
