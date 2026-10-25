# Source register

## Research sources

- `corpus/manifest.json`: the 30 included paper identifiers, aliases and source locations.
- `corpus/corpus.lock.json`: pinned versions and original PDF hashes.
- `corpus/sources.json`: extracted passages, page ranges and URLs.
- `knowledge/claims.json`: explanation entries and their supporting source spans.

The analysed versions are those pinned in the supplied corpus. Later publication versions may differ. A source identifier identifies an item in this collection; it is not a substitute for a full bibliographic record.

## Course context

The project was developed for RMIT COSC2669/COSC2816 WIL Project: Written Report. The supplied course materials address test-driven RAG evaluation, traceable source claims, logging and versioning, enterprise data trust and audience-focused data storytelling. The written report presents those connections separately from this software reference register.

## Technical references retained from the implementation

- Python `http.server` documentation and security considerations: https://docs.python.org/3/library/http.server.html
- MLX LM repository for the optional historical Apple-silicon adapter: https://github.com/ml-explore/mlx-lm

The default application uses the Python standard library. Optional model dependencies and their recorded revision are separate from the default runtime. No new dependency or model version is introduced by the documentation edition.
