# Source register

## Assessment and teaching basis supplied by the user
- WIL Project: Written Report (2650), COSC2669/COSC2816, 25-mark rubric and full written specification, including required sections, 20-page main-text limit, stakeholder value, quantitative effectiveness, genuine management/reflection and required submission files.
- Week 2 Responsible Agentic AI material: traceable claims, independent checks, edge cases, logging/versioning, responsibility and diminishing returns from repeated prompting.
- Week 4 guidance: coherent story, why/what as well as how, and substantial original research references.
- Week 8 enterprise GenAI material: source/data/meaning/reasoning trust, not just plausible output.
- Week 10 Data Storytelling: audience, outcomes, impact, central storyline and an actual use case.
- Supplied original milestone and presentation feedback; the latter requested clearer significance, explained terminology and a central argument.

The official supplied files remain the authority for the assignment. This package does not revise the rubric or invent guest-lecture content absent from the provided materials.

## Research sources
`corpus/manifest.json` identifies the 30 included papers, aliases and original identifiers. `corpus/corpus.lock.json` retains original pinned versions and PDF hashes. `corpus/sources.json` retains extracted passage text, page ranges and URLs. `knowledge/claims.json` identifies the exact source spans for every curated statement. Use complete original paper bibliographic records in the final report; source IDs alone are not a bibliography.

The catalogue is derived from the versions already supplied for this project, not a search of all newer literature. Some works have later published versions. Report the analysed version accurately and verify any publication metadata before submission.

## Implementation references retained from the original release
- Python official documentation, `http.server` and Security Considerations: local HTTP serving is not a production-deployment security guarantee. https://docs.python.org/3/library/http.server.html
- Official MLX LM repository: Apple-silicon inference and generation interface. https://github.com/ml-explore/mlx-lm

These references were recorded in the preceding delivery; no new dependency or model revision is introduced by this presentation-only update.

Default operation uses Python's standard library only. MLX is optional and retains the previously recorded model revision; no new model-weight distribution or claim of measured live MLX improvement is included.
