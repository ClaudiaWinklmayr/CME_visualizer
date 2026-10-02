# Project plan

Goal (from `SPEC.md`): for a user-chosen date, find the nearest CME in the LASCO catalog and produce a
downloadable mp4 of the C2 movie with lines for its direction (CPA) and angular width.

Three developers, each working with AI agents. Suggested ownership:
**A** = catalog & data, **B** = video & overlay, **C** = UI, tests & tooling.

## Milestone 1 – Prototype ✅ done

Single event (2025/02/01 02:12:05) rendered end to end.

- [x] Spec and technical stack (`SPEC.md`)
- [x] Parse the monthly catalog, search for the nearest event across neighbouring months (A)
- [x] Download the daily C2 movie, PIL overlay, ffmpeg H.264 encode (B)
- [x] Streamlit app: date/time input, event table, preview, download (C)
- [x] pytest suite (11 tests) and uv setup (C)
- [x] README

**Done when:** a downloadable mp4 with correct lines exists for the prototype event. ✔

## Milestone 2 – Correct geometry

The lines must start at the true Sun centre and point the right way for any event.

- [ ] Measure the Sun centre in C2 movies (fit the occulter disc) and set or derive `SUN_OFFSET` (B)
- [ ] Check several events against the catalog's own JS movies, in all four quadrants (B)
- [ ] Optional: draw the rays from the occulter edge instead of the centre, for readability (B)
- [ ] Tests for the calibrated centre (C)

**Done when:** for 5+ hand-checked events, the CPA line visibly runs through the CME.

## Milestone 3 – Event-focused video

Show the CME itself, not the whole day.

- [ ] Find frame timestamps: read the per-event JS-movie frame list, or read the clock burned into the image (A/B)
- [ ] Trim to a window around the event, e.g. 1 h before to 3 h after first appearance (B)
- [ ] Events near midnight: join the next day's movie when the window crosses into it (B)
- [ ] Optional: running-difference frames (`c2_rdif`) as an alternative source to make the CME easier to see (A/B)
- [ ] UI: show the window used; optionally let the user adjust it (C)

**Done when:** the video starts shortly before the CME appears and ends after it leaves the field of view.

## Milestone 4 – Robustness & usability

- [ ] Clear errors for missing movies, server outages and dates outside the catalog (A/C)
- [ ] When several CMEs are close in time, list them and let the user pick (A/C)
- [ ] Show more catalog fields (speed, MPA, links) in the event table (C)
- [ ] Limit cache growth, or add a "clear cache" button (C)
- [ ] CI: run `pytest -m "not network"` on each push (C)

**Done when:** a researcher can explore arbitrary dates without hitting a stack trace.

## Milestone 5 – Sharing & extension (optional, on demand)

- [ ] Deployment: Docker image or Streamlit Community Cloud (C)
- [ ] FastAPI wrapper around `cme.render` for scripts and other clients (A)
- [ ] C3 movies as a second instrument option (B)
- [ ] Raw FITS via sunpy for accurate, science-grade geometry (B)

## Working agreement

- Small PRs, one task per branch; `uv run pytest` must pass before merging.
- Record design decisions in `SPEC.md` and update it when scope changes.
- Check every visual change on a real frame (extract one with ffmpeg and look at it).
