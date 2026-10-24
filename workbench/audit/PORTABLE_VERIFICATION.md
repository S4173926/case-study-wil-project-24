# Research Workbench · Portable delivery verification

Date: 24 October 2026. Release: 2.0-portable.

## Delivery scope

One executable Python archive, with its application, original 30 PDFs, processed source collection, fixed explanation catalogue, tests and historical repaired runs embedded. Python 3.10+ is required; no third-party package is needed for the default path. Local working files are unpacked automatically. Source code can be exported from the same file.

## Requested changes

- Removed the Submission evidence and Tests & limitations webpages and navigation entries. Kept the underlying documentation, regression records, source PDFs and contextual answer cautions.
- Four pages remain: Ask & compare, Paper library, Human review and Stakeholder pilot.
- Replaced the mixed bottom-aligned form rows with explicit responsive grids. Variable helper text no longer shifts adjacent controls.
- Kept searchable runs, version selection, current-answer filtering and run-specific ratings.
- Removed the Apple-specific optional-model toggle from the interface. No M4, MLX or GPU is needed for the default assistant.
- Added a single-file launcher, automatic safe extraction, record import, conflict preservation, port fallback and source-export command.
- Added explicit UTF-8 text I/O to avoid platform-default encoding problems.

## Executed checks

| Check | Observed result |
|---|---|
| Existing and new software tests | 118 passed; zero failures or skips |
| Browser-component checks | 40 passed; zero JavaScript errors |
| Existing repaired questions rerun | 67/67 matched |
| Fields compared | Question, mode, factual blocks, citations, retrieved passages, status, missing support, warnings and plan |
| Recorded output states | 52 explanations, 1 partial, 14 insufficient-support responses |
| Original PDFs | 30/30 hashes matched |
| Catalogue | 99 claims, 191 supporting spans |
| Source collection | 1,202 passages |
| New human ratings / user observations in delivery | None |

These test counts do not establish answer accuracy. They show known-case equivalence, mechanical integrity and tested interface behavior. The earlier HyDE limitation remains partial. The current source-linked composer is not a freshly trained generative model.

## Browser check details

Actual application HTML, CSS and JavaScript were rendered in Chromium. Network calls were bridged to the real local HTTP API because this environment blocks direct navigation to localhost. Checks included desktop field alignment, four-page navigation, removal of internal and hardware-specific controls, all 67 repaired run choices, F11 search, both-paper preview, source modal rendering, rating reset, saved fixture attribution, source-confirmation requirements, library filtering, empty states, pilot statistics, actual answer submission, changed-input warning and horizontal-overflow checks at 1440/1280/1024/768/390 px.

All browser fixture ratings were confined to a separate temporary workspace. None were added to the distributed research data. Original PDF responses were checked for file integrity, but native embedded-PDF viewing on macOS/Windows was not certified.

## Standalone archive checks

The executable archive was launched with Python's third-party site-packages disabled (`python -S`). The actual HTTP API returned the repaired two-paper F11 answer; the PDF route returned original PDF bytes; record export produced a valid ZIP without invented reviews. Two occupied local ports were skipped automatically. Source export produced an inspectable application directory with matching protected-file hashes. A fresh extracted archive also passed all 118 software tests and the corpus-integrity check. These are packaging and operation checks, not answer-accuracy ratings.

## Portability

The default runtime uses the Python standard library and makes no model or external API call. It is designed for macOS (Intel and Apple silicon), Windows and Linux with Python 3.10+. Runtime execution and packaging checks here use Linux/Python 3.13, not all three operating systems. Existing historical Apple-model code remains as optional source history; it is not required by the website.

One distribution file does not mean zero disk storage: launching creates a version-specific folder under Research_Workbench_Data in the user's home directory. It never overwrites the old Workbench project. Same-named conflicting imported records are retained separately rather than silently substituted.

## Scope and assessment

Thirty papers is the chosen experimental collection, not a hardware ceiling. The supplied assessment brief recommends a manageable knowledge base and requires quantitative effectiveness and demonstrated stakeholder value. It does not mandate a broad internet-wide paper collection or internal rubric webpages. Expanding source coverage requires ingestion, source validation and an updated explanation catalogue; no arbitrary-PDF ingestion or web search is claimed here.

The software contributes evidence for methodology and findings. It does not supply an independent user study, validate unseen-question accuracy, restore deleted Git history, write authentic team reflections or certify a 25/25 grade. The course/report mapping remains in docs/RUBRIC_MAP.md and docs/REPORT_ASSEMBLY.md inside the archive, not the product navigation.

## Record integrity

The 67 seed records are preserved byte-for-byte from the previous repaired batch. No original research PDFs or source passages were edited. Historical terms and original source attribution are preserved. New interface text is neutral, without development-tool branding. The package retains truthful provenance and known limitations.
