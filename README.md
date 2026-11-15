# DREAMER programs for the DREAM 6800

Games published as hex listings in the **DREAMER**, the newsletter of the DREAM 6800 users
(N.S.W. 6800 Users Group, 1980–82), transcribed from the scans on archive.org, checked in a
simulation of the machine and offered as ready-to-load files.

**Site: https://aminta.github.io/DREAM6800_Programs/**

- `.c8` = CHIP-8 program at 0200 (start with `C000`, `FN 3`); `.d68` = 2 bytes load address +
  2 bytes run address (big-endian) + data.
- Made for the DREAM 6800 MiSTer core (release coming soon); they work on
  real hardware too (type in the listing, or convert to a tape).
- Every page credits the author and the source (issue, page). **Removal on request**: if you
  wrote one of these programs (or are an heir) and want it taken down, open an issue.

## Layout

- `data/games.json`: one entry per game (source, author, files, keys, description, corrections,
  doubts, screenshot choice).
- `build.py`: builds `docs/` (served by GitHub Pages) from the data, the program files, the
  transcribed listings and the screen dumps of the core's simulation tests.
- `docs/files/`, `docs/listings/`: the programs and the listings as transcribed, with notes.

## Licence

The programs and listings belong to their authors; they are here to keep them playable. The site
code (`build.py`, `style.css`) and the transcription notes are MIT-licensed.
