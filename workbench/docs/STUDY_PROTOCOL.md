# Source review and exploratory stakeholder pilot

## Before collecting data
Freeze the release and record its hashes. Use the actual 30-paper PDF collection. Obtain voluntary consent and use pseudonyms. State whether participants are project developers, classmates or external volunteers. They need enough technical background to perform the research tasks; do not call team convenience testing an independent customer study.

A person not answering the task should first inspect the original PDFs and write a reference answer with pages and essential claims. The four built-in pilot questions are proposed tasks, not independently validated gold answers. Replace an ambiguous task before collection and preserve the change in the protocol.

## Conditions
**Manual:** use the Paper library and PDF viewer, without the assistant's explanations or claim catalogue.

**Assistant:** use Ask & compare plus the original PDF to check the result. Include all verification, correction and help time.

Suggested four-person counterbalance:
- P01: manual A, assistant B
- P02: assistant A, manual B
- P03: manual C, assistant D
- P04: assistant C, manual D

Each participant gets different tasks in the two conditions, while each task appears in both conditions across participants. Record order and prior familiarity. Do not train participants on the answers immediately before measuring them. More participants/tasks may improve precision; four is the proposed counterbalance, not a statistical adequacy claim.

## In the application
1. Open Stakeholder pilot. Enter a pseudonym, real relationship, task and condition; obtain consent.
2. Reveal the task and start the timer.
3. Perform the assigned workflow, leaving the timer running during PDF checking.
4. Submit the actual answer and source pages, including inability to answer when applicable. Record help/corrections.
5. A separate reviewer uses Completed task review to check correctness and source support. Until then both are NOT_RATED.
6. Export the real bundle. The application starts with no observations and never fills missing values.

## Human answer review
Score delivered responses against the original PDFs, not against the assistant's self-description. Use 0/1/2 for each dimension:
- Correctness: incorrect; mixed/partly correct; all material claims correct.
- Completeness: fails the requested task; only some essential parts; covers all essential requested parts.
- Citation support: missing/wrong; partial; every material claim supported by its cited passage.
- Relevance: mostly irrelevant; some distracting/omitted focus; directly answers the question.

For unsupported questions, judge whether the limitation is appropriate and no requested value/claim is invented. Lack of an indexed claim is not proof of absence from the whole literature. Confirm answerability from the corpus before scoring. Source-search output is not a complete generated answer, although its evidence utility can be rated separately.

Record reviewer identity as a pseudonym, relationship and source-check confirmation. A second reviewer should check disagreements and a subset of agreements. Keep original ratings. The app flags disagreement rather than silently choosing the more favourable score; discuss any adjudication and keep a record.

## Analysis
Report attempted/completed/rated task counts, correct-and-supported outcomes, individual times, and medians by condition. Show task balance and failures. Compare time among successful tasks as a secondary view, not by silently excluding failures. With a small nonrandom convenience sample, report descriptive evidence rather than causal/statistical significance or general commercial savings.

The UI's pilot summary is descriptive. Correctness is self-reported by the reviewer and not certified by the software. Clock changes or interruptions should be documented. Do not backfill times from memory as measured observations.

## Independence and scope
All existing 52 questions are development/regression cases. To make a fresh-question claim, lock the system and then have another person source-check a new set before execution. Do not tune on that set and still call it unseen. New phrasings within the same curated methods test question generalisation; they do not establish generalisation to new papers or domains.
