from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

import cme

FIXTURE = Path(__file__).parent / "univ2025_02.html"


@pytest.fixture(scope="module")
def catalog():
    return cme.parse_catalog(FIXTURE.read_text(errors="replace"))


def test_parse_first_row(catalog):
    first = catalog.iloc[0]
    assert first.time == pd.Timestamp("2025-02-01 02:12:05")
    assert (first.cpa, first.width) == (247, 38)
    assert first.remark == "Very Poor Event; Only C2"


def test_parse_halo(catalog):
    halos = catalog[catalog.width == 360]
    assert len(halos) == 4 and halos.cpa.isna().all()


def test_nearest(catalog):
    assert cme.nearest(catalog, datetime(2025, 2, 1, 2, 0)).time == pd.Timestamp("2025-02-01 02:12:05")


def test_nearest_across_month_boundary():
    cat = pd.DataFrame({"time": pd.to_datetime(["2025-01-31 23:50", "2025-02-03 12:00"]),
                        "cpa": [10.0, 20.0], "width": [30, 40], "remark": ["", ""]})
    assert cme.nearest(cat, datetime(2025, 2, 1, 0, 30)).cpa == 10


def test_months_around():
    assert cme.months_around(datetime(2025, 1, 15)) == [(2024, 12), (2025, 1), (2025, 2)]
    assert cme.months_around(datetime(2025, 12, 1)) == [(2025, 11), (2025, 12), (2026, 1)]


@pytest.mark.parametrize("angle, end", [(0, (0, -1)), (90, (-1, 0)), (180, (0, 1)), (270, (1, 0))])
def test_ray_end(angle, end):
    x, y = cme.ray_end((0, 0), angle, 1)
    assert (x, y) == pytest.approx(end, abs=1e-9)


def test_overlay_halo_draws_circle_not_rays():
    img = cme.make_overlay((100, 100), float("nan"), 360)
    assert img.getpixel((50, 30))[3] == 0  # straight up from centre: no ray
    assert img.getpixel((50, 5))[3] == 255  # on the circle, r = 45


@pytest.mark.network
def test_render_first_event():
    path = cme.render(datetime(2025, 2, 1, 2, 12, 5))
    assert path.exists() and path.stat().st_size > 0
