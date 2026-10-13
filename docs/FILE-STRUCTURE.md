# File structure

Back to the [README](../README.md) · [Instructions](INSTRUCTIONS.md) · [System design](SYSTEM-DESIGN.md)

```
index.html                    The whole site: intro, research & work, projects, musings
thinking.html                 "Things I'm thinking about": its own page, linked from the profile
photos.html                   Photos from travels: its own page, linked from the profile
values.html                   Values & inspiration: its own page, linked quietly from the footer
favicon.svg                   Browser-tab icon (AM monogram)
styles.css                    Layout, typography, light and dark colours, @font-face rules
media.js                      Lazy-loads and plays the looping clips
fonts/                        Self-hosted Newsreader and Inter (WOFF2) and their OFL licences
_archive/                     Archived blog (not published; see its README)
_drafts/                      Unpublished drafts (Pages skips _ folders); values.md holds draft values
assets/media/                 Looping project clips (MP4); placeholders for now
  README.md                   Which files to supply, and what each should show
images/                       Project screenshots, the clips' WebP posters, and research drawings (SVG)
  portrait.jpg                Pencil-sketch portrait in the intro (served as portrait-240/-480 AVIF and WebP)
  og.png                      Link-preview image (1200×630)
  apple-touch-icon.png        Home-screen icon (180×180)
  <project>.jpg               Full-size screenshot per project (the source for its poster)
  <project>-960.webp          960 px poster shown on the card before its clip plays
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
