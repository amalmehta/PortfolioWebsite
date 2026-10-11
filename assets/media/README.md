# Media

Looping clips for the media slots on the site. Every file here is a **placeholder** until replaced.

Project clips are still loops of the card's existing screenshot, so a card looks the same as before until a real clip lands. (The research entries use drawings in `images/` instead; see `tools/draw-research-art.py`.)

Replace a file by saving the real one under the same name. Keep each file under 2 MB; the tests fail on anything larger. Encoding steps are in [docs/INSTRUCTIONS.md](../../docs/INSTRUCTIONS.md#clips).

## Files to supply

| File | Slot | What it should show |
|---|---|---|
| `neural-signal-ml.mp4` | Project · Neural Signal ML | Decoded reach paths tracing next to the true ones |
| `post-training.mp4` | Project · Post Training Lab | The four-policy maze race |
| `alphago-lite.mp4` | Project · AlphaGo Lite | A few moves with the search overlay |
| `drone-bench.mp4` | Project · Sim to Real Drone Bench | The course flown by each controller |
| `driving-sim.mp4` | Project · Autonomous Driving Sim | A drive with perception and planned path |
| `neuroimaging.mp4` | Project · Neuroimaging Platform | Scrolling slices or rotating the 3D view |
| `sport-analyzer.mp4` | Project · Sport Analyzer | A rep with the 3D pose and live metrics |

Project posters are the existing screenshots in `images/`. If a new clip's first frame differs a lot from its screenshot, replace the screenshot too and update the `width`/`height` on its `<video>` to match.
