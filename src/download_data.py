from __future__ import annotations
from pathlib import Path
from urllib.request import urlretrieve

BASE = "https://raw.githubusercontent.com/lightdash/lightdash-demo-saas/main/seeds"
FILES = ["accounts_raw.csv", "deals_raw.csv", "users_raw.csv", "tracks_raw.csv"]


def download_data(output_dir: str = "data/raw") -> list[Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    for name in FILES:
        target = out / name
        if not target.exists():
            urlretrieve(f"{BASE}/{name}", target)
        downloaded.append(target)
    return downloaded


if __name__ == "__main__":
    paths = download_data()
    for path in paths:
        print(path)
