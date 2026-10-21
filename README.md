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

## Notable uses

Korhoname searches Wikidata (items through English, French, Hindi, Persian and Japanese labels and aliases) and Wikipedia (English, French) for the same shared form: a film, a book, a group, a company or a place of that name makes the name `TAKEN`, since a search engine already ranks it. `--no-notable` skips this step.

## Trademarks

Korhoname also queries TMview, the trademark search run by the European Union Intellectual Property Office over the EU offices, the French INPI, WIPO, the USPTO and some seventy others, without a key. It keeps the marks whose shared form equals the name's and flags those in force in Nice classes 9 (recordings) and 41 (entertainment); such a mark makes the name `TAKEN`. Ended, expired, withdrawn or refused marks are listed, not counted. The report singles out the marks valid in France: French marks, EU marks, and international marks designating France.

For France, Korhoname also reads the INPI's own base (French, EU and international marks) through its official API, when `INPI_USER` and `INPI_PASSWORD` hold the login of a free INPI technical account (in GitHub Actions: repository secrets of the same names). `--no-trademarks` skips both steps.


From GitHub without the form: write the names in `queue.txt`, one per line, and commit it on `main`; the check starts by itself and its result lands on the branch `result`.

## Method

- The verdict rests on the shared form: diacritics, ligatures and punctuation drop, letters a European reader transliterates are transliterated (`θ` as `th`: `Miθra` is `Mithra`), and so does Discogs's `(2)` suffix. A dispute over a name turns on what the names share: `Ā-î-Ā` is read as `AIA`, `Ā-Ā` as `AA`.
- Discogs is searched three times per name and per type: the name as written, without diacritics, and without punctuation (`Ā-Ā`, `A-A`, `AA`), since its search engine matches each form differently.
- The reader proxy is rate-limited: requests are paced, then retried up to eight times with a growing wait. A page that stays unreadable is kept as `unread-….txt` and named in the report; the verdict then says `PART UNREAD` instead of `FREE`.
- MusicBrainz is searched on names and aliases, with five tries.
- A free verdict covers these sources only. It is no legal clearance: a lawyer or the offices themselves settle a dispute.

## GitHub Actions

Fork the repository, then Actions → Korhoname → Run workflow, and type the names, comma-separated. The result shows in the run summary and lands on the branch `result`.

## Licence

MIT for the code. The names Korhoname and Korhogo, the characters and the lore of Korhogo stay © Korhogo, all rights reserved.
