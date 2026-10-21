# Data sources and licenses

This project does **not** vendor third-party clinical datasets. The generator draws synthetic rows. The sources below are cited because their published characteristics informed the distributions and the failure-mode themes.

## openFDA Device Adverse Events (MAUDE)

- Docs: https://open.fda.gov/apis/device/event/
- Endpoint: `https://api.fda.gov/device/event.json`
- Access: public US government data. Anonymous calls are limited (about 240 requests/minute and 1,000/day per IP). A free key raises the daily cap. The key is optional and read from `OPENFDA_API_KEY`.
- What we use: the public product-problem vocabulary (software, mechanical, calibration, incorrect result) as **themes** for synthetic complaint wording. The default generator does not call the API. `invalid_agent.sim.openfda` can fetch a count of recent IVD events when the operator passes `--with-openfda`, and it caches nothing that contains a narrative.
- Disclaimer: openFDA states that the data are unvalidated and not for medical decision-making.

## Mendeley: Icteric Interference with Clinical Chemistry Testing

- Merrill, Mainali, Krasowski (2021)
- Dataset: https://data.mendeley.com/datasets/vxkkdmw55f/1
- DOI: 10.17632/vxkkdmw55f.1
- Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8743196/
- What we use: the published idea of a strongly right-skewed hemolysis / icterus / lipemia index, mostly low, with a long tail past typical package-insert cutoffs. The generator samples a lognormal **stand-in**, documented in `src/invalid_agent/sim/seeds.py`. It is not a fit to the authors' row-level file, and that file is not in this repo.
- License: confirm CC BY 4.0 (the Mendeley Data default) on the dataset page before redistributing any original file. We do not redistribute it. Cite the authors if you quote their results.

## Zenodo: Pseudonymized Complete Blood Count Test Data

- Klinikum Lippe (2025)
- Record: https://zenodo.org/records/15674541
- License: CC BY 4.0 (Zenodo record)
- What we use: nothing row-level. The record is cited as the public CBC source considered for wrong-blood-in-tube / delta-check flavor. v1 does not download the workbook (about 45.9 MB). Pre-analytical scenarios use the HIL-style index instead, which keeps the repo small and avoids republishing clinical rows.

## Our files

- `scenarios/*.yaml`, complaint text, FAQ-style sentences inside prompts, and the backlog JSON are written for this simulation and covered by the repository license (MIT).
- Do not add proprietary IFUs, SOPs, or employer data.

## Not used

NHANES CBC files that are access-restricted were not used. No GenMark or Roche internal content is used.
