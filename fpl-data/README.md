# fpl-data

Automatický snímek veřejných dat z Fantasy Premier League API.
GitHub Action běží každou hodinu a commituje jen tehdy, když se data změní.

## Co je ve složce `data/`

| Soubor | Obsah |
|---|---|
| `players.csv` | všichni hráči - cena, forma, body, xG/xA, defensive contribution, **status zranění a text novinky**, vlastnictví, standardky |
| `teams.csv` | 20 klubů - pozice, body, síla útoku/obrany doma i venku |
| `fixtures.csv` | všech 380 zápasů sezóny - termíny, výsledky, obtížnost (FDR) |
| `meta.json` | čas posledního stažení, aktuální a příští kolo, deadline |
| `history/players_gw{N}.csv` | snímek za každé odehrané kolo - historie sezóny |

## Ruční spuštění

Actions → „FPL snapshot" → Run workflow.

## Zdroj

`https://fantasy.premierleague.com/api/` - veřejné, bez klíče a bez přihlášení.
