# CME Visualizer

Overlays LASCO C2 coronagraph movies with lines for the propagation direction (central position angle, CPA)
and angular width of a coronal mass ejection, using parameters from the
[SOHO/LASCO CME catalog](https://cdaw.gsfc.nasa.gov/CME_list/). Output is an mp4 (H.264) that plays in VLC.

Pick a date and time; the app finds the nearest CME in the catalog, draws the overlay on that day's C2 movie
and offers the result for download.

Overlay legend: **cyan** = CPA, **yellow** = CPA ± width/2. Halo CMEs (width 360°) are shown as a yellow circle.

## Setup

Requires [uv](https://docs.astral.sh/uv/). ffmpeg comes bundled via `imageio-ffmpeg`, no system install needed.

```bash
uv sync
```

## Usage

Web app:

```bash
uv run streamlit run app.py   # http://localhost:8501
```

From Python:

```python
from datetime import datetime
import cme

ev = cme.find_cme(datetime(2025, 2, 1, 2, 12))   # time, cpa, width, remark
path = cme.render(datetime(2025, 2, 1, 2, 12))   # -> cache/renders/20250201_021205_c2.mp4
```

Downloads and renders are cached in `cache/`; delete it to force a refresh.

## Tests

```bash
uv run pytest                  # all tests
uv run pytest -m "not network" # skip the end-to-end render that downloads from CDAW
```

## How it works

1. Fetch the monthly catalog pages (previous, current, next month) and parse them with `pandas.read_html`.
2. Pick the event closest to the requested time.
3. Download the daily C2 movie (`/CME_list/nrl_mpg/YYYY_MM/YYMMDD_c2.mpg`).
4. Draw a transparent PNG with PIL: rays from the Sun centre at CPA and CPA ± width/2
   (angles counter-clockwise from solar north, north up).
5. Overlay the PNG on every frame and encode to H.264 with ffmpeg.

## Known limitations

- The video is the whole-day C2 movie, not trimmed to the event window.
- The Sun centre is assumed at the image centre; adjust `SUN_OFFSET` in `cme.py` if the rays look off.
- An event just before midnight uses that day's movie, even if it mostly develops the next day.

See [SPEC.md](SPEC.md) for the project specification and [PLAN.md](PLAN.md) for milestones.
