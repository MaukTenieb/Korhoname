# Korhoname

Korhoname tells whether a name is free on Discogs and MusicBrainz: artists and labels, names, name variations and aliases.

Korhoname lists two kinds of matches for each name:

- the exact spelling, accents, macrons and ligatures kept;
- the matches once diacritics, ligatures and punctuation drop: `Ā-î-Ā` meets `AIA`, `Skál` meets `Skal`.

The verdict rests on the second kind. A conflict over a name turns on what the names share, not on the signs that set them apart: `Ā-î-Ā` is `TAKEN` as soon as an `AIA` exists.

## Command line (Python 3.9+, standard library only)

```
python3 korhoname.py "Marumero" "Egyensúly" "Ā"
python3 korhoname.py "Gy, Zs, Ly"
python3 korhoname.py --dump "Gy"
```

The result prints to the screen and lands in `korhoname.md` and `korhoname.json`, with a verdict per name: `FREE`, `TAKEN`, or `NO MATCH FOUND, BUT PART UNREAD` when a search stayed out of reach, and every match with its link.

## Sources

| Source | Route | Reach |
|---|---|---|
| Discogs, whole database (`--dump`) | the monthly data dump listed on data.discogs.com: every artist and label name, name variation, alias (about 500 MB, read as a stream) | home connections; servers often get a refusal |
| Discogs, site search | discogs.com/search, read through the r.jina.ai reader, four tries | anywhere; first page of results, best matches first |
| MusicBrainz | the web service, artist and label search with aliases, five tries | anywhere |

`--dump` tries the dump first and falls back to the site search when the dump stays out of reach.

## GitHub Actions

Fork the repository, then Actions → Korhoname → Run workflow, and type the names, comma-separated. The result shows in the run summary and lands on the branch `result`.

## Licence

MIT for the code. The names Korhoname and Korhogo, the characters and the lore of Korhogo stay © Korhogo, all rights reserved.
