# Session 2 quiz

1. Why does the generator redraw the cause mask instead of adding the cause probability on top of the baseline draw?
2. What does the Wilson interval return for 0 invalids out of 100, and why is there a snap-to-zero?
3. A lot and an instrument both look high. Which design choice in `generate.py` makes those two claims separable?
4. Name the four Western Electric rules this p-chart implements.
5. Where do the Mendeley HIL rows live in this repo?

## Answers

1. Adding a second Bernoulli on top would raise the complement too, or double-count the mask. Replacing the mask leaves every other row at the baseline rate, which is the contrast the stratum test needs.
2. The analytic lower bound is 0. Floating point leaves a residue around 1e-18, and the function sets anything under 1e-12 back to 0.
3. Site, instrument, lot, software, and operator are drawn independently. The story is a reference lab, so a collection site is not tied to one instrument. Lot calendars are shared across the lab.
4. One point beyond 3 sigma; two of three beyond 2 sigma on one side; four of five beyond 1 sigma on one side; eight in a row on one side of the center line.
5. They do not. `seeds.py` holds a lognormal stand-in and the DOI. The dataset is not redistributed. See `DATA_LICENSES.md`.
