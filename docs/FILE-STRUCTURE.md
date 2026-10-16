# File structure

Back to the [README](../README.md) · [Instructions](INSTRUCTIONS.md) · [System design](SYSTEM-DESIGN.md)

```
index.html                    The whole site: intro, research & work, projects, writeups, skills, musings (hidden for now)
thinking.html                 "Things I'm thinking about": its own page, linked from the profile
photos.html                   Travel: places I'd like to go, then photos; linked from Interests and the footer
values.html                   Values & inspiration: its own page, unlinked until it has entries
interests.html                Interests: fan of, hobbies, curious about; linked in the header of every page
404.html                      Page not found: GitHub Pages shows it for any missing address (full URLs only)
favicon.svg                   Browser-tab icon (AM monogram)
styles.css                    Layout, typography, light and dark colours, @font-face rules
media.js                      Lazy-loads and plays looping clips; on the page only once a card has one
messi.js                      Hidden replay of Messi's 2011 solo goal at the Bernabéu, behind "soccer tournaments" on the profile
pong.js                       Hidden Pong game behind the skier on the Hokkaido drawing (photos.html)
fonts/                        Self-hosted Newsreader and Inter (WOFF2) and their OFL licences
_archive/                     Archived blog (not published; see its README)
_drafts/                      Unpublished drafts (Pages skips _ folders); values.md holds draft values
assets/media/                 Looping project clips (MP4) once recorded; empty for now
  README.md                   Which files to supply, and what each should show
images/                       Project screenshots (and their WebP copies the cards show) and research drawings (SVG)
  portrait.jpg                Pencil-sketch portrait in the intro (served as portrait-240/-480 AVIF and WebP)
  og.png                      Link-preview image (1200×630)
  apple-touch-icon.png        Home-screen icon (180×180)
  <project>.jpg               Full-size screenshot per project (the source for its poster)
  <project>-960.webp          960 px copy shown on the card (the poster, once it has a clip)
papers/                       PDFs linked from the site: the robot soccer thesis and school reports
resume/
  Amal Mehta Resume.tex       Resume source (latest resume, no phone number)
  Amal Mehta Resume.pdf       Built resume, linked from the site
tools/
  make-images.sh              Builds the WebP posters and portrait AVIF/WebP from the JPEGs in images/
  draw-research-art.py        Draws the research-entry and Reward Hack Zoo SVGs in images/
  draw-places.py              Draws the "Places I'd like to go" SVGs in images/places/
tests/
  test_site.py                 Automated checks: links, images, media, cards, contrast, resume
docs/
  INSTRUCTIONS.md             Preview, edit, rebuild the resume, publish
  SYSTEM-DESIGN.md            Architecture, decisions, testing, limits
  FILE-STRUCTURE.md           This file
  images/                     README screenshots of the site itself
README.md                     What it is, screenshots, links
```
