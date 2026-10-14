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
- **Selected writeups**: the `<section id="writeups">` block after Projects, laid out like Research & work. Each entry links its report in `papers/`; the link text gives the file's size (e.g. "Report (PDF, 3.1 MB)"), so update it if the PDF changes.
- **Skills**: the `<section id="skills">` block after Selected writeups, the most current list of skills, one row per group. Add a skill as a `<span class="chip">` in its row and update the date in the "updated" line. The resume's Technical Skills must stay a subset: the tests fail if a resume skill is missing here.
- **Musings**: the `<section id="musings">` block after Selected writeups, hidden until its first note: when you add one, delete `hidden` from the section and put `<a href="#musings">Musings</a>` back in the header (`index.html#musings` on the other pages). It has three groups: Adventure, Life and Discovery. To add a note, copy the commented-out `<article class="musing">` template inside its group, fill in the date, title and a few sentences, and put it above older notes. Delete the group's "First note coming soon." line once its first note is in.
- **Things I'm thinking about**: its own page, `thinking.html`, linked from the Interests page and the footer. To add a thought, copy the commented-out `<li class="thought">` template, fill in the question, a few sentences and the date, and put it above older ones (they number themselves). Delete "First thought coming soon." once the first one is in.
- **Photos**: its own page, `photos.html`, linked from the Interests page and the footer. See [Add a photo](#add-a-photo). A skier on the Hokkaido drawing in Places I'd like to go is a hidden button that opens Pong (`pong.js`).
- **Values & inspiration**: its own page, `values.html`, linked only from the footer ("Values"). Each section (Values, Inspiration, Things I care about) has a commented-out template to copy; delete that section's "Coming soon." once its first entry is in.
- **Live interests**: its own page, `interests.html`, linked in the header of every page as "Interests". Only current interests belong here: remove an entry when it stops being one. It ends with links to Things I'm thinking about (Ideas) and the Photos page (Travel). Hobbies and Curious about work the same way as the Values page: copy the commented-out template, and delete "Coming soon." once the first entry is in.

Colours, fonts and spacing are in `styles.css`. The fonts are self-hosted: the `@font-face` rules at the top of `styles.css` point at `fonts/`, and each page preloads the two Latin files. The colour values at the top (`:root`) have a second set under `prefers-color-scheme: dark` for dark mode.

## Screenshots

Project screenshots live in `images/` as JPEG about 1400 px wide. The page shows a 960 px WebP copy as each clip's poster, built from the JPEG:

```bash
sips -s format jpeg -s formatOptions 80 --resampleWidth 1400 shot.png --out images/name.jpg
tools/make-images.sh images/name.jpg
```

Then set the `poster` on the card's `<video>` to `images/name-960.webp` and its `width`/`height` to that file's size (the tests check they match). `make-images.sh` needs `brew install libavif webp`.

Cards crop images to a 16:10 frame from the top left. For a wide chart that shouldn't be cropped, add `contain` to its figure: `<figure class="shot contain">`. For a wide screenshot whose useful part is on the right, add `crop-right` instead.

## Clips

Each project card has a looping clip in `assets/media/`, with a poster image shown before it plays (and instead of it with no JavaScript or reduced motion on). `assets/media/README.md` lists every file and what it should show. To replace one, save the new clip under the same name.

Keep each clip under 2 MB: about 5–8 seconds, 960 px wide, no audio. With [ffmpeg](https://ffmpeg.org) (`brew install ffmpeg`):

```bash
ffmpeg -i input.mov -t 8 -an -vf "scale=960:-2,fps=24" -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -movflags +faststart assets/media/name.mp4
```

Raise `-crf` (30–32) or shorten `-t` if it's still over 2 MB. To turn a GIF into a clip, use the same command with the `.gif` as input.

The tests fail if a clip or poster is over 2 MB or a poster's size doesn't match the `width`/`height` on its `<video>`.

## Research drawings

PhysicsAI, Hybrid Robotics Lab, the Video & Image Processing Lab and the Abbasi-Asl Lab each show a drawing (`images/physicsai.svg`, `robot-soccer.svg`, `vip-lab.svg`, `brain-emd.svg`), not a photo or clip. They're illustrations, not real results: the detection scores, settings, tumour outline and decomposition layers in them are made up. The Reward Hack Zoo project card also shows a drawing (`images/reward-hack-zoo.svg`) until its runs finish and real plots exist. `tools/draw-research-art.py` draws all five; edit it and run `python3 tools/draw-research-art.py` to redraw them.

## Writing (archived)

The blog is archived in `_archive/` and not published. Follow `_archive/README.md` to bring it back.

## Portrait

`images/portrait.jpg` is a 480 px square; the page crops it to a circle. To replace it, save a new square image there. Leave white space around the head so the circle doesn't clip it.

## Add a photo

Photos live in `images/photos/` as WebP, at most 1600 px on the long side. Converting with `cwebp` drops the photo's location and camera data, so GPS coordinates aren't published. From the repo root (works with JPEG and HEIC):

```bash
mkdir -p images/photos && sips -Z 1600 -s format png ~/Pictures/IMG_1234.HEIC --out /tmp/photo.png && cwebp -q 80 -metadata none /tmp/photo.png -o images/photos/place-year.webp
```

Then copy the commented-out `<figure class="photo">` template in `photos.html`. Fill in the file name, alt text (what the photo shows), the place and year, and one line about the moment, and put it above older photos. Set `width` and `height` to the new file's size (`sips -g pixelWidth -g pixelHeight images/photos/place-year.webp`); the tests check they match. Delete "Photos coming soon." once the first photo is in.

Below your photos, **Places I’d like to go** shows drawings (not photos) of one iconic spot per place, in `images/places/`. `tools/draw-places.py` draws them; edit it and run `python3 tools/draw-places.py` to redraw.

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
