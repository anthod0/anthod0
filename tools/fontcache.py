# Fonts are not committed. They are fetched from a pinned google/fonts commit into tools/fonts/
# (gitignored) on first use, and checked against a known hash.
import hashlib
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent / "fonts"
BASE = "https://raw.githubusercontent.com/google/fonts/e7db6ca603fd4862010383ff17ffd6cc4ffac1c0/ofl"
FONTS = {  # local name: (path under ofl/, sha256)
    "InterTight-VF.ttf": (
        "intertight/InterTight%5Bwght%5D.ttf",
        "b81b73dcb64df3c230cabade7df6c5773bf863233f24c9ee51087519f1f88b6f",
    ),
    "IBMPlexMono-Regular.ttf": (
        "ibmplexmono/IBMPlexMono-Regular.ttf",
        "6a3412f058c7d8dfd9170c41e85ade48e5156ecb89356110ca57a0a27734af46",
    ),
}


def font(name):
    """Return the local path of a font, downloading it first if missing."""
    path = DIR / name
    src, sha = FONTS[name]
    if not path.exists():
        DIR.mkdir(exist_ok=True)
        data = urllib.request.urlopen(f"{BASE}/{src}").read()
        if hashlib.sha256(data).hexdigest() != sha:
            raise RuntimeError(f"{name}: sha256 mismatch")
        path.write_bytes(data)
    return path
