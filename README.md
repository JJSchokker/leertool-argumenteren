# 🚗⚡ Leertool Digitale Geletterdheid

Een educatieve tool voor basisschoolleerlingen (groep 7/8) om kritisch denken en mediawijsheid te oefenen via gesimuleerde online discussies over elektrische auto's.

## 🎯 Doel

Leerlingen leren:
- Betrouwbare bronnen herkennen
- Misleidende informatie identificeren
- Trollen en afleidingen doorzien
- Een onderbouwde mening vormen

## 👥 Agenten

De tool bevat 10 verschillende discussiedeelnemers:

| Agent | Rol | Bijzonderheid |
|-------|-----|---------------|
| Elisabeth van Meer | Expert PRO | Wetenschapsjournalist, veel bronnen |
| Jeroen van der Munt | Expert CONTRA | Ingenieur, kritisch maar eerlijk |
| Elaidya Basia | Helper PRO | Moeder met eigen ervaring |
| Rob van Dijk | Complotdenker | Mixt feiten met misleiding |
| Kevin123 | Trol | Flauwe grappen, geen kennis |
| Najiba Dop | Voorbijganger | Onzeker, herhaalt anderen |
| Judith Janssen | PRO gemiddeld | Evenwichtig, luistert |
| Peter Mercier | PRO afleider | Obsessief over F1 |
| Jessica Stekelenburg | PRO afleider | Obsessief over yoga |
| Jim Duister | CONTRA bondig | Extreem kort, conservatief |

## 📁 Structuur

```
leertool_online/
├── app.py                 # Hoofdapplicatie (Streamlit UI)
├── config.py.example      # Voorbeeld configuratie
├── requirements.txt       # Dependencies
├── README.md
│
├── agents/                # Agent definities
│   ├── __init__.py
│   ├── definitions.py     # Agent dataclass & AGENTEN dict
│   ├── cv_data.py         # Persoonlijke details
│   └── kennisbank.py      # PRO/CONTRA feiten
│
├── llm/                   # LLM integratie
│   ├── __init__.py
│   ├── clients.py         # Client initialisatie
│   ├── generate.py        # Response generatie
│   └── moderation.py      # Vangrail (content filter)
│
├── utils/                 # Hulpfuncties
│   ├── __init__.py
│   ├── context_weaver.py  # Dynamische prompts
│   └── logging.py         # Response logging
│
└── assets/                # Media bestanden
    ├── socrates_header.jpeg
    └── avatars/
        └── *.png
```

## 🚀 Installatie

### Lokaal

```bash
# Clone repository
git clone https://github.com/JOUW_USERNAME/leertool-digitale-geletterdheid.git
cd leertool-digitale-geletterdheid

# Installeer dependencies
pip install -r requirements.txt

# Configureer API keys
cp config.py.example config.py
# Vul je API keys in

# Start de app
streamlit run app.py
```

### Streamlit Cloud

1. Fork deze repository
2. Ga naar [share.streamlit.io](https://share.streamlit.io)
3. Maak nieuwe app aan met je repo
4. Voeg secrets toe in App Settings:

```toml
[api_keys.model_1]
provider = "anthropic"
api_key = "sk-ant-..."
model_name = "claude-sonnet-4-20250514"

[api_keys.model_2]
provider = "openai"
api_key = "sk-..."
model_name = "gpt-4o"

[api_keys.model_3]
provider = "mistral"
api_key = "..."
model_name = "mistral-large-latest"

[api_keys.model_4]
provider = "google"
api_key = "..."
model_name = "gemini-2.0-flash"
```

## ⚙️ Gedragsparameters

Elke agent heeft drie parameters (0-1):

- **p_bronnen**: Kans dat agent feiten uit kennisbank gebruikt
- **p_cv_detail**: Kans dat agent persoonlijke details deelt
- **p_referentie**: Kans dat agent terugverwijst naar eerder gesprek

## 📝 Licentie

MIT License

## 👤 Auteur

Johan Schokker - Boom Uitgevers
