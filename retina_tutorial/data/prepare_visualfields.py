"""Recreate the supplied teaching CSVs from a fixed visualFields release.

Normal tutorial use does not need this script: the CSV files are bundled.
For provenance/reproduction only:
    python -m pip install rdata==1.1.0 pandas numpy
    python prepare_visualfields.py --output-dir recreated_data

The source data and coordinate map are from visualFields 1.0.7, distributed
under Apache License 2.0. Original attribution and the complete license are
preserved in DESCRIPTION.visualFields.txt and LICENSE.visualFields.txt.

Changes made for the tutorial: export the original R table as CSV; represent
R Date values (days since 1970-01-01) as ISO dates; add point names and a
blind-spot exclusion flag to the coordinate CSV. No measured values are
altered, filtered, imputed, mirrored, or relabelled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
import rdata


CRAN_COMMIT = "d4e4c408655d236dd23ff4f748495cfac74bc77a"
AUTHOR_COMMIT = "c05c2d7d3ae67332ee9f94c6299a492ce3a09191"
CRAN_BASE = f"https://raw.githubusercontent.com/cran/visualFields/{CRAN_COMMIT}"
AUTHOR_BASE = f"https://raw.githubusercontent.com/imarinfr/vf1/{AUTHOR_COMMIT}"

SOURCES = {
    "vfpwgRetest24d2.rda": (
        f"{CRAN_BASE}/data/vfpwgRetest24d2.rda",
        "8f74bc02995b213b0c448b0f9ce765c6e8e918a60f53c9ae0d1c130d839c6d8e",
    ),
    "locmaps.rda": (
        f"{CRAN_BASE}/data/locmaps.rda",
        "21d3f208cda0d302a264067f16d263c2d738257ace1a091690885952d99988b2",
    ),
    "DESCRIPTION.visualFields.txt": (
        f"{CRAN_BASE}/DESCRIPTION",
        "0230d4a071621a7ea78550fddf08b39c976464a34c5850211a7184bab41341e1",
    ),
    "LICENSE.visualFields.txt": (
        f"{AUTHOR_BASE}/LICENSE",
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    ),
}


def obtain(outdir: Path, filename: str, url: str, expected_sha: str) -> Path:
    path = outdir / filename
    if path.exists():
        body = path.read_bytes()
    else:
        with urlopen(url, timeout=45) as response:
            body = response.read()
    actual_sha = hashlib.sha256(body).hexdigest()
    if actual_sha != expected_sha:
        raise ValueError(f"SHA-256 mismatch for {filename}: {actual_sha}")
    path.write_bytes(body)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("recreated_data"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, (url, expected_sha) in SOURCES.items():
        obtain(args.output_dir, filename, url, expected_sha)

    raw = rdata.read_rda(args.output_dir / "vfpwgRetest24d2.rda")
    frame = raw["vfpwgRetest24d2"].copy()
    assert frame.shape == (360, 64)
    assert frame["id"].nunique() == 30
    assert frame.groupby(["id", "eye"]).size().eq(12).all()
    assert frame.isna().sum().sum() == 0
    # rdata 1.1.0 warns that R's Date class has no constructor and returns the
    # underlying numeric days. This explicit conversion is intentional.
    frame["date"] = pd.to_datetime(
        frame["date"].astype(float), unit="D", origin="unix"
    ).dt.strftime("%Y-%m-%d")
    frame.to_csv(args.output_dir / "vfpwgRetest24d2.csv", index=False)

    locmap = rdata.read_rda(args.output_dir / "locmaps.rda")["locmaps"]["p24d2"]
    coordinates = locmap["coord"].copy()
    coordinates.insert(0, "point", [f"l{i}" for i in range(1, 55)])
    blind_spots = np.asarray(locmap["bs"], dtype=int)
    assert blind_spots.tolist() == [26, 35]
    coordinates["is_blind_spot"] = np.isin(np.arange(1, 55), blind_spots)
    coordinates.to_csv(args.output_dir / "p24d2_coordinates.csv", index=False)

    manifest = {
        "package": "visualFields",
        "version": "1.0.7",
        "cran_commit": CRAN_COMMIT,
        "author_commit": AUTHOR_COMMIT,
        "license": "Apache License 2.0",
        "sources": {
            name: {"url": url, "sha256": sha}
            for name, (url, sha) in SOURCES.items()
        },
        "conversion": (
            "R table exported as CSV; R Date days since 1970-01-01 converted "
            "to ISO date strings; no measured values changed. Coordinate "
            "table exported from locmaps$p24d2. Excluded points l26/l35 "
            "identified by the source map's bs component (R 1-based)."
        ),
        "coordinate_convention": (
            "The package stores locations in a common right-eye coordinate "
            "frame. Original vfplots.R mirrors x-axis display for OS without "
            "reordering sensitivity columns. Preserve this convention during "
            "modelling; mirror only the displayed x coordinate for OS if "
            "showing actual left-eye field orientation."
        ),
        "coordinate_evidence": [
            f"{CRAN_BASE}/R/vfplots.R",
            f"{CRAN_BASE}/R/vfloaders.R",
            f"{CRAN_BASE}/R/locmap.R",
        ],
        "caveats": [
            "All participants have glaucoma; no healthy class or progression labels.",
            "The study assumes little clinically meaningful short-term change.",
            "Published dates include a 524-day span for subject 7 despite a study description of 12 weekly sessions.",
            "All published fpr values are zero; time/duration are placeholder-like constants.",
            "A prediction target is the next recorded test, not guaranteed one week later.",
        ],
    }
    (args.output_dir / "provenance.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created {args.output_dir / 'vfpwgRetest24d2.csv'}: {frame.shape}")
    print(f"Created {args.output_dir / 'p24d2_coordinates.csv'}: {coordinates.shape}")


if __name__ == "__main__":
    main()
