# Media

Looping clips for the project cards, once they're recorded. None are here yet: each card shows its screenshot until its clip lands. (The earlier placeholder loops of each screenshot were removed; they looked the same as the still but cost 65–200 KB each.)

To add a clip, follow [docs/INSTRUCTIONS.md](../../docs/INSTRUCTIONS.md#clips): keep it under 2 MB and swap the card's `<img>` for the `<video>` markup there. The tests check every clip is a silent, lazy-loaded loop with a matching poster.

## Clips worth recording

| File | Card | What it should show |
|---|---|---|
| `neural-signal-ml.mp4` | Neural Signal ML | Decoded reach paths tracing next to the true ones |
| `post-training.mp4` | Post Training Lab | The four-policy maze race |
| `alphago-lite.mp4` | AlphaGo Lite | A few moves with the search overlay |
| `drone-autonomy.mp4` | Drone Autonomy | A flight with the room mapping in and the A* plan |
| `driving-sim.mp4` | Autonomous Driving Sim | A drive with perception and planned path |
| `neuroimaging.mp4` | Neuroimaging Platform | Scrolling slices or rotating the 3D view |
| `sport-analyzer.mp4` | Sport Analyzer | A rep with the 3D pose and live metrics |
