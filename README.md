# Korhoname

By Mauk Tenieb & Korhogo. Build guide: [MaukTenieb/method](https://github.com/MaukTenieb/method).

Korhoname checks whether a name is free on Discogs and MusicBrainz: artists and labels, names, name variations and aliases. It also checks notable uses on Wikidata and Wikipedia, and trademarks on TMview and at the INPI.

For each name, Korhoname lists two kinds of matches:

- the exact spelling, with accents, macrons and ligatures kept;
- the matches once diacritics, ligatures and punctuation drop: `Ā-î-Ā` matches `AIA`, `Skál` matches `Skal`.

The status of a name depends on the second kind. A conflict over a name turns on what the names share. The signs that set them apart count for little, so `Ā-î-Ā` is `TAKEN` as soon as an `AIA` exists.

## Command line

Python 3.9+, standard library only.

```
python3 korhoname.py "Marumero" "Egyensúly" "Ā"
python3 korhoname.py "Gy, Zs, Ly"
python3 korhoname.py --dump "Gy"
```

Korhoname prints the result to the screen and writes it to `korhoname.md` and `korhoname.json`. Each name gets a status, `FREE`, `TAKEN`, or `NO MATCH FOUND, BUT PART UNREAD` when a search stayed out of reach, and every match with its link.

## Sources

| Source | Route | Reach |
|---|---|---|
| Discogs, whole database (`--dump`) | the monthly data dump listed on data.discogs.com: every artist and label name, name variation, alias (about 500 MB, read as a stream) | home connections; servers often get a refusal |
| Discogs, site search | discogs.com/search, read through the r.jina.ai reader, up to eight tries per query | anywhere; first page of results, best matches first |
| MusicBrainz | the web service: artist and label search with aliases, up to five tries | anywhere |

With `--dump`, Korhoname tries the dump first and falls back to the site search when the dump stays out of reach.

## Notable uses

Korhoname searches Wikidata (items, through their English, French, Hindi, Persian and Japanese labels and aliases) and Wikipedia (English, French) for the same shared form. A film, a book, a group, a company or a place of that name makes the name `TAKEN`, since a search engine already ranks it. `--no-notable` skips this step.

## Trademarks

Korhoname also queries TMview, the trademark search of the European Union Intellectual Property Office. TMview spans the EU offices, the French INPI, WIPO, the USPTO and some seventy others, and asks for zero keys. Korhoname keeps the marks whose shared form equals the name's and flags those in force in Nice classes 9 (recordings) and 41 (entertainment). Such a mark makes the name `TAKEN`. The report lists ended, expired, withdrawn and refused marks for reference and counts only marks in force. It singles out the marks valid in France: French marks, EU marks, and international marks designating France.

For France, Korhoname also reads the INPI's own base (French, EU and international marks) through its official API. It does so when `INPI_USER` and `INPI_PASSWORD` hold the login of a free INPI technical account; in GitHub Actions, these are repository secrets of the same names. `--no-trademarks` skips both steps.

## GitHub Actions

Two routes start a check on GitHub. Both write the result to the branch `result`.

- Fork the repository, then Actions → Korhoname → Run workflow, and type the names, comma-separated. The result also shows in the run summary.
- Write the names in `queue.txt`, one per line, and commit it on `main`. The push starts the check.

## Method

- Korhoname compares names on their shared form. Diacritics, ligatures and punctuation drop, along with Discogs's `(2)` suffix, and Korhoname transliterates the letters a European reader transliterates (`θ` as `th`: `Miθra` matches `Mithra`). A dispute over a name turns on what the names share: Korhoname reads `Ā-î-Ā` as `AIA` and `Ā-Ā` as `AA`.
- Korhoname searches Discogs up to three times per name and per type: the name as written, the name stripped of diacritics, and the name stripped of punctuation (`Ā-Ā`, `A-A`, `AA`). The Discogs search engine matches each form differently.
- The reader proxy limits its rate. Korhoname paces its requests, then retries up to eight times with a growing wait. When a page stays unreadable, Korhoname saves it as `unread-….txt`, names it in the report, and gives the status `PART UNREAD` in place of `FREE`.
- Korhoname searches MusicBrainz on names and aliases, with up to five tries.
- A `FREE` status concerns these sources only. For legal clearance, a lawyer or the offices themselves settle a dispute.

Related: [mauktenieb.github.io](https://mauktenieb.github.io/) · [MaukTenieb/method](https://github.com/MaukTenieb/method)

## Rights

Code under MIT, method under CC BY 4.0, Korhogo material reserved; credit Mauk Tenieb & Korhogo. Details: [LICENSE](LICENSE).
