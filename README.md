# PowerOffice Radar (Python)

Leser data fra **PowerOffice Go** (kun API-lesing) og lager en enkel likviditetsoversikt.  
Godkjenning og fakturering gjør du fortsatt i Go.

## Forutsetninger

- Python 3.11+ ([python.org](https://www.python.org/downloads/))
- Test-nøkler fra [developer.poweroffice.net](https://developer.poweroffice.net/gettingstarted) (demo-miljø)

## Kom i gang (Windows)

```powershell
cd C:\Users\Sigmund\projects\poweroffice-radar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

Fyll inn i `.env`:

- `POWEROFFICE_APPLICATION_KEY` (applikasjonsnøkkel)
- `POWEROFFICE_CLIENT_KEY` (klientnøkkel)
- `POWEROFFICE_SUBSCRIPTION_KEY` (fra Developer Portal → Profile)

Kjør:

```powershell
python src\run_daily.py
```

Ved suksess får du tekstrapport i konsollen og filene:

- `data/latest_liquidity.txt`
- `data/*.json` (rådata til finjustering)

## Plan (med Cursor)

1. **Steg 1 (nå):** Likviditet – bank + utestående kundefakturaer  
2. **Steg 2:** Leverandørgjeld + enkel prognose  
3. **Steg 3:** Likviditetsbudsjett (CSV/Excel)  
4. **Steg 4:** Prosjektregnskap fra kontotransaksjoner  
5. **Steg 5:** AI-oppsummering (valgfritt) på ferdige tall  

## Sikkerhet

- Legg aldri `.env` i git (står i `.gitignore`)
- Bruk kun **demo** til du er klar for produksjon og integrasjonsavtale

## Hjelp

Feil ved innlogging: sjekk at alle tre nøkler er fra **samme miljø** (demo vs. prod).  
Spørsmål om API: [go-api@poweroffice.no](mailto:go-api@poweroffice.no)
