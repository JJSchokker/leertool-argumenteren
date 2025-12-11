# Leertool Argumenteren

Een educatieve tool voor basisschoolleerlingen (bovenbouw) om kritisch denken en argumenteren te oefenen via gesimuleerde discussies in een chatroom.


## Agenten

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

## Structuur

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


## Gedragsparameters

Elke agent heeft drie parameters (0-1) & max. aantal tokens:

- **p_bronnen**: Kans dat agent feiten uit kennisbank gebruikt
- **p_cv_detail**: Kans dat agent persoonlijke details deelt
- **p_referentie**: Kans dat agent terugverwijst naar eerder gesprek
- **Max. aantal tokens: Maximale lengte van de respons in de chat
