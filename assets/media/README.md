# Media

Looping clips for the media slots on the site. Every file here is a **placeholder** until replaced.

- Project clips are still loops of the card's existing screenshot, so a card looks the same as before until a real clip lands.
- Research posters and clips are generic "clip coming soon" cards.

Replace a file by saving the real one under the same name. Keep each file under 2 MB; the tests fail on anything larger. Encoding steps are in [docs/INSTRUCTIONS.md](../../docs/INSTRUCTIONS.md#clips).

## Files to supply

| File | Slot | What it should show |
|---|---|---|
| `physicsai.mp4` | Research · PhysicsAI | RL agents tuning the synthetic-image generator; detector results on real drone imagery |
| `physicsai-poster.jpg` | Research · PhysicsAI | 1280×720 still from that clip |
| `robot-soccer.mp4` | Research · Hybrid Robotics Lab | The Go1 walking to the ball and shooting at the target (real robot, or sim and real side by side) |
| `robot-soccer-poster.jpg` | Research · Hybrid Robotics Lab | 1280×720 still from that clip |
| `vip-lab.mp4` | Research · Video & Image Processing Lab | Melanoma segmentation drawn over a whole-slide image, panning or zooming |
| `vip-lab-poster.jpg` | Research · Video & Image Processing Lab | 1280×720 still from that clip |
| `neural-signal-ml.mp4` | Project · Neural Signal ML | Decoded reach paths tracing next to the true ones |
| `post-training.mp4` | Project · Post Training Lab | The four-policy maze race |
| `alphago-lite.mp4` | Project · AlphaGo Lite | A few moves with the search overlay |
| `drone-bench.mp4` | Project · Sim to Real Drone Bench | The course flown by each controller |
| `driving-sim.mp4` | Project · Autonomous Driving Sim | A drive with perception and planned path |
| `neuroimaging.mp4` | Project · Neuroimaging Platform | Scrolling slices or rotating the 3D view |
| `sport-analyzer.mp4` | Project · Sport Analyzer | A rep with the 3D pose and live metrics |

Project posters are the existing screenshots in `images/`. If a new clip's first frame differs a lot from its screenshot, replace the screenshot too and update the `width`/`height` on its `<video>` to match.
