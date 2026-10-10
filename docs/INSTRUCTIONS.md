# Instructions

Back to the [README](../README.md) · [System design](SYSTEM-DESIGN.md) · [File structure](FILE-STRUCTURE.md)

## Preview locally

No build step. Serve the folder and open it:

```bash
python3 -m http.server 8000
```

Then visit <http://localhost:8000>. Opening `index.html` directly also works.

## Run the tests

From the repo root, with no installs:

```bash
python3 -m unittest discover tests
```

The resume PDF check is skipped unless `pypdf` is installed. Run the tests before pushing.

## Edit content

Everything visible lives in `index.html`:

- **Intro**: the `<section class="hero">` block at the top.
- **Projects**: one `<article class="project">` per project, with a looping clip (its screenshot as poster), a heading, a description, a line of tags and an optional link. Copy one to add a project, or delete one to remove it.
- **Research & work**: one `<article class="role">` per role.

Colours, fonts and spacing are in `styles.css`. The colour values at the top (`:root`) have a second set under `prefers-color-scheme: dark` for dark mode.

## Screenshots

Project images live in `images/`, saved as JPEG about 1400 px wide to keep the page light:

```bash
sips -s format jpeg -s formatOptions 80 --resampleWidth 1400 shot.png --out images/name.jpg
```

Cards crop images to a 16:10 frame from the top left. For a wide chart that shouldn't be cropped, add `contain` to its figure: `<figure class="shot contain">`.

## Clips

Each project card has a looping clip in `assets/media/`, with a poster image shown before it plays (and instead of it with no JavaScript or reduced motion on). `assets/media/README.md` lists every file and what it should show. To replace one, save the new clip under the same name.

Keep each clip under 2 MB: about 5–8 seconds, 960 px wide, no audio. With [ffmpeg](https://ffmpeg.org) (`brew install ffmpeg`):

```bash
ffmpeg -i input.mov -t 8 -an -vf "scale=960:-2,fps=24" -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -movflags +faststart assets/media/name.mp4
```

Raise `-crf` (30–32) or shorten `-t` if it's still over 2 MB. To turn a GIF into a clip, use the same command with the `.gif` as input.

The tests fail if a clip or poster is over 2 MB or a poster's size doesn't match the `width`/`height` on its `<video>`.

## Research drawings

PhysicsAI, Hybrid Robotics Lab, the Video & Image Processing Lab and the Abbasi-Asl Lab each show a drawing (`images/physicsai.svg`, `robot-soccer.svg`, `vip-lab.svg`, `brain-emd.svg`), not a photo or clip. They're illustrations, not real results: the detection scores, settings, tumour outline and decomposition layers in them are made up. `tools/draw-research-art.py` draws all four; edit it and run `python3 tools/draw-research-art.py` to redraw them.

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
