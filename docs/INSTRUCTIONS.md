# Instructions

Back to the [README](../README.md) · [System design](SYSTEM-DESIGN.md) · [File structure](FILE-STRUCTURE.md)

## Preview locally

No build step. Serve the folder and open it:

```bash
python3 -m http.server 8000
```

Then visit <http://localhost:8000>. Opening `index.html` directly also works.

## Edit content

Everything visible lives in `index.html`:

- **Intro**: the `<section class="hero">` block at the top.
- **Projects**: one `<article class="project">` per project, with a screenshot, a heading, a description, a line of tags and an optional link. Copy one to add a project, or delete one to remove it.
- **Research & work**: one `<article class="role">` per role.

Colours, fonts and spacing are in `styles.css`. The colour values at the top (`:root`) have a second set under `prefers-color-scheme: dark` for dark mode.

## Screenshots

Project images live in `images/`, saved as JPEG about 1400 px wide to keep the page light:

```bash
sips -s format jpeg -s formatOptions 80 --resampleWidth 1400 shot.png --out images/name.jpg
```

Cards crop images to a 16:10 frame from the top left. For a wide chart that shouldn't be cropped, add `contain` to its figure: `<figure class="shot contain">`.

## Writing (archived)

The blog is archived in `_archive/` and not published. Follow `_archive/README.md` to bring it back.

## Portrait

`images/portrait.jpg` is a 480 px square; the page crops it to a circle. To replace it, save a new square image there. Leave white space around the head so the circle doesn't clip it.

## Rebuild the resume

The resume PDF is built from `resume/Amal Mehta Resume.tex` with [Tectonic](https://tectonic-typesetting.github.io/) and the macOS Times New Roman font:

```bash
cd resume && tectonic -c minimal "Amal Mehta Resume.tex"
```

It has no phone number. Keep it to one page.

## Publish

The site is served by GitHub Pages from the `main` branch root. Pushing to `main` updates it within a minute or two:

```bash
git push
```
