## SPEC.md

**Project description:** Overlay LASCO coronagraph videos of coronal mass ejections (CMEs) with lines indicating the propapagation direction and the width of the CME. The direction (principal angle) and the width can be obtained from the LASCO CME catalog (https://cdaw.gsfc.nasa.gov/CME_list/).

**Goals & Outcomes**: What do we want to achieve?
We want to see a coronagraph video of one CME which is specified in advance, and in the video there should be lines indicating the propagation direction and the width of the CME.

**Stakeholders & users :** Who is involved or affected?
Researchers (e.g. data scientists, solar physicists)

**User needs / use cases :** What do users need to do?
Users need to specify a date around which the closest CME from the LASCO catalog is searched.

**Scope** : What is included and excluded?
For now, we only include the direction of the CME and the width of only one event at a time.

**Requirements & constraints :** What must we consider from
the start?
The videos and parameters to visualized are hosted on https://cdaw.gsfc.nasa.gov/CME_list/. We select the videos of type C2. 

We aim to produce video outputs in mp4 format to be played with VLC. 

**Technical approach :** Interactive WebApp using established packages for Web-Development based on Python (Streamlit), see Technical Stack

**Development approach :** Three developers deploying AI agents. For a first prototype we will use the video from the first row of the table, corresponding to 2025/02/01	02:12:05, accessible under https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL_ver2/2025_02/univ2025_02.html.

**Quality, security & compliance :** Fast Development and Deployment and short feedback loops

**Success criteria :** A downloadable video (mp4) has been created

## Technical Stack
### Frontend
Streamlit (single app; calls the Python core directly, no separate API server)
### Backend
Plain Python module exposing `render(date) -> path to mp4`, called by Streamlit:
- `requests` to download the catalog HTML and the daily C2 `.mpg` (`/CME_list/nrl_mpg/YYYY_MM/YYMMDD_c2.mpg`)
- `pandas.read_html` (+ `lxml`) to parse the monthly catalog table; nearest CME to the given date by |t - t0|, also checking the neighbouring month near month boundaries
- PIL to draw one transparent PNG overlay, the same size as the video frame: central ray at CPA, two edge rays at CPA ± width/2, starting at Sun centre (CPA measured counter-clockwise from solar north; north up: dx = -sin θ, dy = -cos θ). Sun-centre offset is a config value (default: image centre). Halo CMEs (width 360°): draw a circle instead of edge rays
- ffmpeg (binary from `imageio-ffmpeg`) to read the frame size, overlay the PNG on every frame and encode the result: H.264, `yuv420p`, even frame dimensions, so it plays in VLC and browsers
- Downloads and rendered videos cached on disk / via `st.cache_data`
- Later, if other clients need it: wrap the core in FastAPI
### UI/UX
- Date input (and optional time) to search for the nearest CME
- Table of the matched event: date/time, CPA, width, remark
- Video preview (`st.video`) and mp4 download button (`st.download_button`)
- Clear error message if no event or no C2 movie is found
### Testing
pytest, focused:
- Catalog parsing against a saved HTML fixture (`univ2025_02.html`)
- Nearest-event search, including month boundaries
- Angle → pixel math (0°, 90°, 180°, 270°, halo)
- One end-to-end render of the 2025/02/01 02:12:05 event (CPA 247°, width 38°), marked as needing the network
### Build
uv + `pyproject.toml` with a committed `uv.lock`; run with `uv run streamlit run app.py`, test with `uv run pytest`
### Deployment
Local only for now (each developer runs the app locally)

