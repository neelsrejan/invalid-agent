"""Distribution stand-ins and the invalid-code vocabulary.

Hemolysis indices are a lognormal stand-in for the right-skewed HIL
indices published by Merrill, Mainali, and Krasowski (DOI
10.17632/vxkkdmw55f.1). They are not a fit to that dataset and the
dataset is not shipped here.

Complaint themes use the public FDA device product-problem vocabulary.
They are labels, not MAUDE narratives.
"""

from __future__ import annotations

import numpy as np

INVALID_CODES: tuple[str, ...] = (
    "INV-IC",   # internal control failure
    "INV-EXT",  # extraction failure
    "INV-INH",  # inhibition
    "INV-HEM",  # hemolysis / pre-analytical
    "INV-VOL",  # insufficient volume
    "INV-TMP",  # temperature flag
    "INV-SW",   # software / instrument abort
    "INV-USR",  # operator / process
)

# Shares among baseline invalids. They sum to 1.
BASE_CODE_WEIGHTS: dict[str, float] = {
    "INV-IC": 0.22,
    "INV-EXT": 0.16,
    "INV-INH": 0.14,
    "INV-HEM": 0.10,
    "INV-VOL": 0.14,
    "INV-TMP": 0.06,
    "INV-SW": 0.10,
    "INV-USR": 0.08,
}

# FDA device product-problem themes (public vocabulary, paraphrased as labels).
COMPLAINT_THEMES: tuple[str, ...] = (
    "Incorrect, inadequate, or imprecise result",
    "Computer software problem",
    "Mechanical problem",
    "Calibration problem",
    "Device operates differently than expected",
    "Failure to run",
)

# Shipping temperature for a controlled lane, degrees C. Excursions are applied
# by the generator on top of this, not drawn from it.
NOMINAL_SHIPPING_TEMP_C = (20.0, 1.2)

# Lognormal parameters (mu, sigma) on the natural log of the hemolysis index.
# Baseline median is exp(1.5) ≈ 4.5. The severe site median is exp(4.3) ≈ 74,
# so a large share clears an index cutoff of 100.
HEMOLYSIS_BASELINE = (1.5, 0.85)
HEMOLYSIS_SEVERE = (4.3, 0.55)


def sample_hemolysis(rng: np.random.Generator, n: int, *, severe: bool = False) -> np.ndarray:
    mu, sigma = HEMOLYSIS_SEVERE if severe else HEMOLYSIS_BASELINE
    return rng.lognormal(mean=mu, sigma=sigma, size=n)


def sample_codes(rng: np.random.Generator, n: int, dominant: str | None, dominant_weight: float) -> np.ndarray:
    """Draw invalid-code labels. ``n`` is the number of invalid rows, not all rows."""
    if n <= 0:
        return np.array([], dtype=object)
    codes = list(BASE_CODE_WEIGHTS)
    if dominant is None or dominant not in BASE_CODE_WEIGHTS:
        weights = np.array([BASE_CODE_WEIGHTS[c] for c in codes], dtype=float)
        weights = weights / weights.sum()
        return rng.choice(codes, size=n, p=weights)
    other = [c for c in codes if c != dominant]
    other_w = np.array([BASE_CODE_WEIGHTS[c] for c in other], dtype=float)
    other_w = other_w / other_w.sum() * (1.0 - dominant_weight)
    labels = [dominant, *other]
    weights = np.concatenate([[dominant_weight], other_w])
    return rng.choice(labels, size=n, p=weights)
