"""Find the CME nearest to a date in the LASCO catalog and render its C2 movie with CPA/width lines."""
import math
import subprocess
from datetime import datetime
from io import StringIO
from pathlib import Path

import imageio_ffmpeg
import pandas as pd
import requests
from PIL import Image, ImageDraw

BASE = "https://cdaw.gsfc.nasa.gov/CME_list"
CACHE = Path(__file__).parent / "cache"
SUN_OFFSET = (0, 0)  # (dx, dy) in px of the Sun centre from the image centre; calibrate if rays look off
COLORS = {"cpa": (0, 255, 255, 255), "edge": (255, 255, 0, 255)}


def fetch(url: str) -> Path:
    """Download url once into CACHE (mirroring the server path) and return the local file."""
    path = CACHE / url.split("/CME_list/", 1)[1]
    if not path.exists():
        r = requests.get(url, timeout=60)
        if r.status_code == 404:
            raise FileNotFoundError(f"Not found on CDAW server: {url}")
        r.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(r.content)
    return path


def parse_catalog(html: str) -> pd.DataFrame:
    """Monthly catalog HTML -> DataFrame[time, cpa, width, remark]. Halo CMEs get cpa = NaN."""
    df = pd.read_html(StringIO(html))[0]
    return pd.DataFrame({
        "time": pd.to_datetime(df.iloc[:, 0] + " " + df.iloc[:, 1], format="%Y/%m/%d %H:%M:%S"),
        "cpa": pd.to_numeric(df["Central PA [deg]"], errors="coerce"),
        "width": df["Angular Width [deg]"].astype(str).str.extract(r"(\d+)")[0].astype(int),
        "remark": df["Remarks"].fillna(""),
    })


def months_around(t: datetime) -> list[tuple[int, int]]:
    """(year, month) of the previous, current and next month, so events across a month boundary are found."""
    m = t.year * 12 + t.month - 1
    return [(y, mo + 1) for y, mo in (divmod(m + d, 12) for d in (-1, 0, 1))]


def load_month(year: int, month: int) -> pd.DataFrame:
    try:
        path = fetch(f"{BASE}/UNIVERSAL_ver2/{year}_{month:02d}/univ{year}_{month:02d}.html")
    except FileNotFoundError:  # month not (yet) in the catalog
        return pd.DataFrame(columns=["time", "cpa", "width", "remark"])
    return parse_catalog(path.read_text(errors="replace"))


def nearest(catalog: pd.DataFrame, t: datetime) -> pd.Series:
    if catalog.empty:
        raise LookupError(f"No CME in the catalog near {t}")
    return catalog.loc[(catalog["time"] - pd.Timestamp(t)).abs().idxmin()]


def find_cme(t: datetime) -> pd.Series:
    catalog = pd.concat([load_month(y, m) for y, m in months_around(t)], ignore_index=True)
    return nearest(catalog, t)


def ray_end(center: tuple[float, float], angle_deg: float, length: float) -> tuple[float, float]:
    """End point of a ray at position angle angle_deg (CCW from solar north; north up, image y down)."""
    th = math.radians(angle_deg)
    return center[0] - length * math.sin(th), center[1] - length * math.cos(th)


def make_overlay(size: tuple[int, int], cpa: float, width: int) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = (size[0] / 2 + SUN_OFFSET[0], size[1] / 2 + SUN_OFFSET[1])
    length = math.hypot(*size)  # long enough to reach any image edge; PIL clips
    if math.isnan(cpa) or width >= 360:
        r = 0.45 * min(size)
        draw.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], outline=COLORS["edge"], width=2)
        label = f"Halo CME, width {width}°"
    else:
        for a in (cpa - width / 2, cpa + width / 2):
            draw.line([center, ray_end(center, a, length)], fill=COLORS["edge"], width=2)
        draw.line([center, ray_end(center, cpa, length)], fill=COLORS["cpa"], width=2)
        label = f"CPA {cpa:g}°  width {width}°"
    draw.text((10, 10), label, fill=(255, 255, 255, 255))
    return img


def render(t: datetime) -> Path:
    """Render the daily C2 movie of the CME nearest to t with the overlay; returns the mp4 path."""
    ev = find_cme(t)
    out = CACHE / "renders" / f"{ev.time:%Y%m%d_%H%M%S}_c2.mp4"
    if out.exists():
        return out
    # ponytail: whole-day movie, no trimming to the event window (mpg has no frame timestamps)
    mpg = fetch(f"{BASE}/nrl_mpg/{ev.time:%Y_%m}/{ev.time:%y%m%d}_c2.mpg")
    frames = imageio_ffmpeg.read_frames(str(mpg))
    size = next(frames)["size"]
    frames.close()
    out.parent.mkdir(parents=True, exist_ok=True)
    png = out.with_suffix(".png")
    make_overlay(size, ev.cpa, ev.width).save(png)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(mpg), "-i", str(png),
        "-filter_complex", "[0][1]overlay,scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out),
    ], check=True)
    return out
