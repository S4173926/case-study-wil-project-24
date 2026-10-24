# Assessment and course alignment

This is an evidence map, not a prediction of marks. Criterion names and maxima follow the six-part rubric mapping supplied earlier in this project. The original marking sheet is not reproduced or replaced by this document.

## Source basis

- Supplied WIL Project: Written Report specification, COSC2669/COSC2816: Aim; Written Report; Project Management; Appendix. It requires quantitative effectiveness, demonstrated stakeholder value and a report for a business decision maker. It says a working pipeline alone is insufficient.
- Supplied Responsible Agentic AI in Your Workflow deck: PDF pages 30–35 on minimal permissions, versioning, logs, verification and stopping ineffective iteration.
- Supplied DataStoryTelling-20260929 deck: audience-focused communication, filtering content against its intended outcome and a demo centred on a core use case.
- Earlier supplied written-report rubric audit: scope 5, methodology 5, findings 4, impact 3, management 5, communication 3. These sum to 25; they are not this application's score.

## Evidence mapping

| Criterion | Software evidence now available | Evidence outside the software |
|---|---|---|
| Project scope and achieved aims (5) | Bounded 30-paper research/comparison workflow; source search; support limits. | State stakeholder and research questions; explain the move from the earlier eight-paper prototype and the changed answering architecture. |
| Methodology and functionality (5) | Reproducible retrieval/claim-composition path; citation spans; original PDFs; input/output hashes; clause-selection repair; regression and interface tests. | Explain why the approach was chosen, catalogue creation and maintenance effort, metric definitions and limitations. Do not call composition unrestricted model generation. |
| Findings (4) | Original 67 repaired outputs and verifiable before/after defects; refusal/partial states; controlled retrieval-ablation tooling; real-rating export. | Interpret successes and failures against research questions. Report exact denominators and distinguish technical audits from independent human judgments. |
| Impact and significance (3) | Functional source inspection, comparison workflow, searchable records and a task-timing pilot tool. | Actual task/user observations or carefully labelled technical proxies. No user time saving or business benefit is automatically established. |
| Management and reflection (5) | Release identity, changelog, recoverable original results and explicit usability feedback addressed. | Genuine repository recovery, Trello activity, actual roles and contributions, mentoring where it occurred, and individual reflections. |
| Written communication (3) | Exportable answers, original evidence, coherent product labels and documented result boundaries. | Final course-provided Overleaf report, readable figures, references, working links, required supporting documents and page-limit compliance. |

## Course-guided design decisions

Versioned data and preserved input/output records support reproducibility. A localhost-only default follows minimal-access design. Source links enable verification but do not certify an answer. The UI starts from a research question and separates findings from their sources. The finalisation change addresses observed user difficulty instead of tuning a model against the same answer again.

## Readiness boundary

This release can be frozen as the software deliverable. Highest-band project marks still depend on the final report and genuine supporting evidence. A new interface does not turn development questions into an independent test or complete the outstanding stakeholder-value and teamwork evidence.
