# File structure

Back to the [README](../README.md) · [Instructions](INSTRUCTIONS.md) · [System design](SYSTEM-DESIGN.md)

```
index.html                    The whole site: intro, research & work, projects
favicon.svg                   Browser-tab icon (AM monogram)
styles.css                    Layout, typography, light and dark colours, blog styles
media.js                      Lazy-loads and plays the looping clips
_archive/                     Archived blog (not published; see its README)
assets/media/                 Looping project clips (MP4); placeholders for now
  README.md                   Which files to supply, and what each should show
images/                       Project screenshots (also the clips' posters) and research drawings (SVG)
  portrait.jpg                Pencil-sketch portrait in the intro
  og.png                      Link-preview image (1200×630)
  apple-touch-icon.png        Home-screen icon (180×180)
  neural-signal-ml.jpg
  post-training.jpg
  alphago-lite.jpg
  drone-bench.jpg
  driving-sim.jpg
  neuroimaging.jpg
  sport-analyzer.jpg
resume/
  Amal Mehta Resume.tex       Resume source (latest resume, no phone number)
  Amal Mehta Resume.pdf       Built resume, linked from the site
tools/
  make-images.sh              Builds AVIF/WebP copies of the JPEGs in images/
  draw-research-art.py        Draws the four research-entry SVGs in images/
tests/
  test_site.py                 Automated checks: links, images, media, cards, contrast, resume
docs/
  INSTRUCTIONS.md             Preview, edit, rebuild the resume, publish
  SYSTEM-DESIGN.md            Architecture, decisions, testing, limits
  FILE-STRUCTURE.md           This file
  images/                     README screenshots of the site itself
README.md                     What it is, screenshots, links
```
