const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("./apply_theme.js");

// Ink-and-highlighter palette: dark slate ink, deep teal for "grounded / correct", amber highlighter for the key point.
const THEME = {
  name: "Grounded Ink",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1E2A2E", lt1: "FFFFFF", dk2: "0F4C52", lt2: "EDF3F2",
    accent1: "0F6E73", accent2: "E08A2C", accent3: "8A9A9D", accent4: "B3412E",
    accent5: "5E8C61", accent6: "2D3E43", hlink: "0F6E73", folHlink: "5E7D80",
  },
};
const HEX = THEME.colors;

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
  pres.title = "Paper-Grounded RAG Research Assistant";
  pres.author = "WIL Project 24";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // ---------- layouts ----------
  pres.defineSlideMaster({
    title: "DARK_TITLE",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.35, w: 8.8, h: 1.5, fontSize: 38, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.0, w: 8.8, h: 0.8, fontSize: 18, color: C.background2, valign: "top", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.5, 0.5, 0.5],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 30, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
      { text: { text: "WIL Project 24 · Paper-grounded RAG research assistant", options: { x: 0.5, y: 5.2, w: 6, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
    ],
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent3, align: "right" },
  });

  pres.defineSlideMaster({
    title: "DARK_CONTENT",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 30, bold: true, color: C.background1, valign: "middle", margin: 0 }, text: "" } },
    ],
  });

  // ---------- 1. Title ----------
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "DARK_TITLE", sectionTitle: "Introduction" });
  s.addText("A source-grounded RAG research assistant", { placeholder: "title" });
  s.addText("Comparing methods across academic papers without mixing up who said what", { placeholder: "body" });
  s.addImage({ data: await icon(fa.FaBookOpen, HEX.accent2), x: 0.6, y: 0.55, w: 0.6, h: 0.6, objectName: "Book icon" });
  s.addText("Chetan Bera · Imranjit Singh Kohli · Deboprio Saha Argha · Qiling Huang · Dhanush Sridhar · Amritpal Singh Gill",
    { x: 0.6, y: 4.35, w: 8.8, h: 0.35, fontSize: 12, color: C.background1, margin: 0, isTextBox: true, objectName: "Team" });
  s.addText("WIL Project 24 · Sprint 3 update · October 2026",
    { x: 0.6, y: 4.7, w: 8.8, h: 0.3, fontSize: 12, color: C.accent3, margin: 0, isTextBox: true, objectName: "Date" });
  s.addNotes("Presenter: Dhanush (0:25).\n\nHi everyone, we're WIL Project 24. I'm Dhanush, and I'm presenting with Imranjit and Chetan.\n\nOur project is a research assistant that answers questions about a collection of academic papers, using retrieval-augmented generation, or RAG. The difference is that it has to stay grounded. Every answer cites the passage it came from, and if the evidence isn't there, it says so instead of guessing.");

  // ---------- 2. Problem & approach ----------
  pres.addSection({ title: "Problem and approach" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem and approach" });
  s.addText("The risk: right answer, wrong paper", { placeholder: "title" });
  // user story card
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.25, w: 4.3, h: 3.3, fill: { color: C.background2 }, line: { type: "none" }, rectRadius: 0.12, objectName: "User story card" });
  s.addText([
    { text: "User story", options: { bold: true, fontSize: 16, color: C.accent1, breakLine: true } },
    { text: "“As a researcher, I want to query and compare methods across papers so I can find reliable evidence quickly without searching every document.”", options: { italic: true, fontSize: 15, color: C.text1, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "Why it's hard", options: { bold: true, fontSize: 16, color: C.accent1, breakLine: true } },
    { text: "Our 8 papers share the same vocabulary (retriever, passages, BM25, RAG), so a system can easily credit one paper's method to another.", options: { fontSize: 15, color: C.text1 } },
  ], { x: 0.75, y: 1.4, w: 3.8, h: 3.0, valign: "top", margin: 0, isTextBox: true, objectName: "User story text" });
  // approach rows
  const rows = [
    [fa.FaFlask, "Test-driven evaluation", "24 questions with exact evidence sentences, written before any tuning"],
    [fa.FaBalanceScale, "Walert as the baseline", "Every change compared against a Walert-style BM25 setup"],
    [fa.FaQuoteRight, "Cite or decline", "Each sentence cites a passage, or the answer is INSUFFICIENT_EVIDENCE"],
  ];
  for (let i = 0; i < rows.length; i++) {
    const y = 1.3 + i * 1.2;
    s.addShape(pres.shapes.OVAL, { x: 5.2, y, w: 0.6, h: 0.6, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `Approach icon bg ${i + 1}` });
    s.addImage({ data: await icon(rows[i][0], "FFFFFF"), x: 5.35, y: y + 0.15, w: 0.3, h: 0.3, objectName: `Approach icon ${i + 1}` });
    s.addText([
      { text: rows[i][1], options: { bold: true, fontSize: 16, color: C.text1, breakLine: true } },
      { text: rows[i][2], options: { fontSize: 14, color: C.accent6 } },
    ], { x: 6.0, y: y - 0.08, w: 3.5, h: 1.0, valign: "top", margin: 0, isTextBox: true, objectName: `Approach text ${i + 1}` });
  }
  s.addNotes("Presenter: Dhanush (0:50).\n\nOur user is a researcher who wants to compare methods across papers without reading every one.\n\nOur eight papers are all about retrieval-augmented question answering, so they share the same vocabulary: retriever, passages, BM25, RAG. That means the real risk isn't a missing answer. It's a confident answer credited to the wrong paper.\n\nSo we worked test-first. Before tuning anything, we wrote 24 questions, each with an exact sentence from the paper as its evidence. Seven of them can't be answered from the papers at all, to check that the system knows when to stop. Walert, the RMIT chatbot, is our baseline. And the answer step follows one rule: every sentence cites a passage, or the reply is 'insufficient evidence'.\n\nHANDOVER: Imranjit will now show how it all fits together.");

  // ---------- 3. Pipeline ----------
  pres.addSection({ title: "What we built" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What we built" });
  s.addText("What we built: a pipeline we can test end to end", { placeholder: "title" });
  const steps = [
    [fa.FaFilePdf, "Corpus", "8 arXiv papers, versioned by checksum"],
    [fa.FaBroom, "Ingest", "Clean text from two-column PDFs, headings found"],
    [fa.FaCut, "Chunk", "4 ways: 200 / 400 words, sentence, section"],
    [fa.FaSearch, "Retrieve", "BM25, TF-IDF, dense, hybrid, + routing"],
    [fa.FaQuoteRight, "Answer", "Every sentence cited, or a refusal when evidence is missing"],
  ];
  const bw = 1.6, gap = 0.25, x0 = 0.5;
  for (let i = 0; i < steps.length; i++) {
    const x = x0 + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.35, w: bw, h: 2.35, fill: { color: C.background2 }, line: { type: "none" }, rectRadius: 0.1, objectName: `Step card ${i + 1}` });
    s.addShape(pres.shapes.OVAL, { x: x + bw / 2 - 0.35, y: 1.55, w: 0.7, h: 0.7, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `Step icon bg ${i + 1}` });
    s.addImage({ data: await icon(steps[i][0], "FFFFFF"), x: x + bw / 2 - 0.18, y: 1.72, w: 0.36, h: 0.36, objectName: `Step icon ${i + 1}` });
    s.addText(steps[i][1], { x: x + 0.1, y: 2.4, w: bw - 0.2, h: 0.4, fontSize: 16, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true, objectName: `Step name ${i + 1}` });
    s.addText(steps[i][2], { x: x + 0.12, y: 2.8, w: bw - 0.24, h: 0.85, fontSize: 12, color: C.accent6, align: "center", valign: "top", margin: 0, isTextBox: true, objectName: `Step detail ${i + 1}` });
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + 0.04, y: 2.4, w: 0.17, h: 0.25, fill: { color: C.accent3 }, line: { type: "none" }, objectName: `Arrow ${i + 1}` });
    }
  }
  // evaluation band
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 3.95, w: 9.0, h: 0.95, fill: { color: C.text2 }, line: { type: "none" }, rectRadius: 0.1, objectName: "Evaluate band" });
  s.addImage({ data: await icon(fa.FaChartBar, HEX.accent2), x: 0.75, y: 4.2, w: 0.45, h: 0.45, objectName: "Evaluate icon" });
  s.addText([
    { text: "Evaluate  ", options: { bold: true, color: C.background1 } },
    { text: "4 chunkers × 5 retrievers = 20 setups, each scored on the same 24 questions. A validate step stops the run if any evidence sentence goes missing from the extracted text.", options: { color: C.background2 } },
  ], { x: 1.4, y: 4.0, w: 7.9, h: 0.85, fontSize: 14, valign: "middle", margin: 0, isTextBox: true, objectName: "Evaluate text" });
  s.addNotes("Presenter: Imranjit (0:55).\n\nThanks, Dhanush. This is our pipeline.\n\nWe download the eight papers from arXiv and pin each one by version and checksum, so every result is tied to an exact copy of the corpus. Ingestion then turns the PDFs into clean text. That was harder than we expected. Real papers gave us author affiliations read as section headings, an abstract read after the introduction, and figure labels dropped into the middle of sentences. We fixed all three.\n\nNext, we split the text four ways, retrieve with five methods, and generate a cited answer. That's twenty combinations, all scored on the same 24 questions. A validate step stops the run if any evidence sentence goes missing from the extracted text, and it caught several extraction bugs early.\n\nHANDOVER: Chetan will take you through what we found.");

  // ---------- 4. Results ----------
  pres.addSection({ title: "Results" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
  s.addText("Results: more evidence found, right paper cited", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [
    { name: "Walert-style baseline (200-word + BM25)", labels: ["Recall@5", "Right paper cited", "Unsupported declined", "MRR"], values: [0.59, 0.81, 0.86, 0.42] },
    { name: "Best setup (400-word + hybrid + routing)", labels: ["Recall@5", "Right paper cited", "Unsupported declined", "MRR"], values: [0.71, 1.0, 1.0, 0.32] },
  ], {
    x: 0.5, y: 1.2, w: 5.6, h: 3.8, barDir: "col", barGapWidthPct: 60,
    chartColors: [HEX.accent3, HEX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: HEX.dk1, dataLabelFormatCode: "0.00", dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 1.15, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 11, legendColor: HEX.dk1, legendFontFace: "+mn-lt",
    objectName: "Baseline vs best chart",
  });
  const stats = [
    ["7 / 7", "unsupported questions declined (baseline 6 / 7)"],
    ["1.00", "citation precision: every cited passage from the right paper"],
    ["0.42 → 0.32", "MRR fell: the right passage is found more often but ranked lower"],
  ];
  for (let i = 0; i < stats.length; i++) {
    const y = 1.3 + i * 1.25;
    s.addText(stats[i][0], { x: 6.4, y, w: 3.1, h: 0.55, fontSize: 28, bold: true, fontFace: "Cambria", color: i === 2 ? C.accent4 : C.accent1, margin: 0, isTextBox: true, objectName: `Stat ${i + 1}` });
    s.addText(stats[i][1], { x: 6.4, y: y + 0.55, w: 3.1, h: 0.6, fontSize: 13, color: C.accent6, valign: "top", margin: 0, isTextBox: true, objectName: `Stat label ${i + 1}` });
  }
  s.addNotes("Presenter: Chetan (0:55).\n\nThanks, Imranjit. This chart compares the Walert-style baseline, in grey, with our best setup, in teal.\n\nRecall at five, which means the right passage is somewhere in the top five results, rose from 0.59 to 0.71. Citation precision reached 1.00, so every cited passage came from the right paper. And the system declined all seven unanswerable questions, against six for the baseline.\n\nOne trade-off we want to be upfront about: MRR fell from 0.42 to 0.32. We find the right passage more often, but it tends to rank lower in the top five. We chose the best setup with a stated rule that combines recall, citation precision and correct refusals. Choosing on MRR alone picked a setup that answered three of the seven unanswerable questions.");

  // ---------- 5. Error analysis ----------
  pres.addSection({ title: "What we learned" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What we learned" });
  s.addText("Error analysis led to one targeted fix", { placeholder: "title" });
  const card = async (x, ico, head, body, tint) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.25, w: 4.25, h: 2.2, fill: { color: tint }, line: { type: "none" }, rectRadius: 0.12, objectName: head + " card" });
    s.addImage({ data: await icon(ico, tint === C.text2 ? HEX.accent2 : HEX.accent4), x: x + 0.25, y: 1.45, w: 0.4, h: 0.4, objectName: head + " icon" });
    s.addText(head, { x: x + 0.8, y: 1.42, w: 3.25, h: 0.45, fontSize: 17, bold: true, color: tint === C.text2 ? C.background1 : C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: head + " heading" });
    s.addText(body, { x: x + 0.25, y: 2.0, w: 3.8, h: 1.35, fontSize: 14, color: tint === C.text2 ? C.background2 : C.text1, valign: "top", margin: 0, isTextBox: true, objectName: head + " body" });
  };
  await card(0.5, fa.FaExclamationTriangle, "Main failure: wrong paper",
    [{ text: "“Which retrieval models did Walert use?” returned RAG-paper passages. Shared words like “retrieval” and “RAG” outweighed the paper's name.", options: {} }], C.background2);
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 4.85, y: 2.15, w: 0.3, h: 0.4, fill: { color: C.accent2 }, line: { type: "none" }, objectName: "Fix arrow" });
  await card(5.25, fa.FaRoute, "Fix: paper-aware routing",
    [{ text: "When a question names papers, the top 5 results are shared among those papers. Citation precision rose to 1.00 for every chunker.", options: {} }], C.text2);
  const findings = [
    ["Dense retrieval alone is weakest", "MiniLM: Recall@5 0.35–0.47"],
    ["Bigger chunks inflate recall", "400 words gives ~170 chunks vs ~490"],
    ["Remaining misses are wording", "“out-of-knowledge-base” vs “out of KB”"],
  ];
  for (let i = 0; i < findings.length; i++) {
    const x = 0.5 + i * 3.08;
    s.addText([
      { text: findings[i][0], options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
      { text: findings[i][1], options: { fontSize: 13, color: C.accent6 } },
    ], { x, y: 3.75, w: 2.85, h: 0.85, valign: "top", margin: 0, isTextBox: true, objectName: `Finding ${i + 1}` });
  }
  s.addText("Caveat: routing was designed after seeing these failures, so we are confirming it on new, held-out questions.",
    { x: 0.5, y: 4.65, w: 9.0, h: 0.4, fontSize: 12, italic: true, color: C.accent4, margin: 0, isTextBox: true, objectName: "Caveat" });
  s.addNotes("Presenter: Chetan (0:55).\n\nWe gave every failure a label, and one pattern dominated: retrieving from the wrong paper. When we asked which retrieval models Walert used, the system returned passages from the RAG paper. Words like 'retrieval' and 'RAG' appear everywhere, and they outweighed the word 'Walert'.\n\nSo we added paper-aware routing. When a question names papers, the top five results are shared among those papers. That took citation precision to 1.00 for every chunking method.\n\nWe also learned that dense retrieval on its own was the weakest option, and that bigger chunks make recall look better than it is. One caveat: we designed the routing after seeing these failures, so we're now testing it on new questions it hasn't seen.\n\nHANDOVER: Imranjit will close with where we are.");

  // ---------- 6. Progress & next steps ----------
  pres.addSection({ title: "Next steps" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Next steps" });
  s.addText("Where we are and what's next", { placeholder: "title" });
  const sprints = [
    ["Sprint 1 · 15–21 Sep", "Roles, corpus, questions, Walert baseline", C.accent5, "Done"],
    ["Sprint 2 · 22–28 Sep", "Ingestion, chunking, retrieval, cited answers", C.accent5, "Done"],
    ["Sprint 3 · 29 Sep–5 Oct", "20-setup evaluation, error analysis, routing", C.accent2, "In progress"],
  ];
  for (let i = 0; i < sprints.length; i++) {
    const x = 0.5 + i * 3.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.2, w: 2.85, h: 1.45, fill: { color: C.background2 }, line: { type: "none" }, rectRadius: 0.1, objectName: `Sprint card ${i + 1}` });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.2, y: 1.35, w: 1.15, h: 0.3, fill: { color: sprints[i][2] }, line: { type: "none" }, rectRadius: 0.15, objectName: `Sprint status ${i + 1}` });
    s.addText(sprints[i][3], { x: x + 0.2, y: 1.35, w: 1.15, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Sprint status text ${i + 1}` });
    s.addText([
      { text: sprints[i][0], options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
      { text: sprints[i][1], options: { fontSize: 13, color: C.accent6 } },
    ], { x: x + 0.2, y: 1.75, w: 2.5, h: 0.85, valign: "top", margin: 0, isTextBox: true, objectName: `Sprint text ${i + 1}` });
  }
  const next = [
    [fa.FaCheckDouble, "Validate routing on held-out questions", "Deboprio", C.accent1],
    [fa.FaRobot, "Run LLM answer generation (blocked: needs an API key)", "Dhanush", C.accent4],
    [fa.FaGithub, "Push experiment commits (blocked: GitHub 403)", "Amritpal", C.accent4],
    [fa.FaWrench, "Fix PDF text errors: garbled equations, “Query” read as “Qery”", "Imranjit", C.accent1],
  ];
  for (let i = 0; i < next.length; i++) {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 3.0 + row * 0.95;
    s.addShape(pres.shapes.OVAL, { x, y, w: 0.5, h: 0.5, fill: { color: next[i][3] }, line: { type: "none" }, objectName: `Next icon bg ${i + 1}` });
    s.addImage({ data: await icon(next[i][0], "FFFFFF"), x: x + 0.12, y: y + 0.12, w: 0.26, h: 0.26, objectName: `Next icon ${i + 1}` });
    s.addText([
      { text: next[i][1], options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
      { text: "Owner: " + next[i][2], options: { fontSize: 12, color: C.accent6 } },
    ], { x: x + 0.65, y: y - 0.05, w: 3.75, h: 0.8, valign: "top", margin: 0, isTextBox: true, objectName: `Next text ${i + 1}` });
  }
  s.addNotes("Presenter: Imranjit (0:35).\n\nSprints one and two are done: the corpus, question set and baseline, then the full pipeline. Sprint three, this week, delivered the evaluation, the error analysis and the routing fix.\n\nNext, Deboprio is validating the routing on held-out questions, and I'm fixing the remaining PDF text errors, like garbled equations and a font that turns 'Query' into 'Qery'. Two items are blocked: model-written answers need an API key, and pushing to GitHub needs an access fix. Both have owners on our Trello board.");

  // ---------- 7. Scaling roadmap (closing) ----------
  pres.addSection({ title: "Scaling up" });
  s = pres.addSlide({ masterName: "DARK_CONTENT", sectionTitle: "Scaling up" });
  s.addText("How we'll scale it up", { placeholder: "title" });
  const phases = [
    ["1", "Finish Sprint 3", "Test routing on held-out questions; run LLM answers once we get an API key", "A trustworthy baseline"],
    ["2", "8 → 20–30 papers, same topic", "More similar papers make the wrong-paper test harder", "Does citation precision stay near 1.00?"],
    ["3", "A second topic, then hundreds", "Check the system isn't tuned to one research field", "Does it generalise?"],
  ];
  const pw = 2.75, pg = 0.375;
  for (let i = 0; i < phases.length; i++) {
    const x = 0.5 + i * (pw + pg);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.3, w: pw, h: 3.05, fill: { color: C.accent6 }, line: { type: "none" }, rectRadius: 0.12, objectName: `Phase card ${i + 1}` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.5, w: 0.55, h: 0.55, fill: { color: C.accent2 }, line: { type: "none" }, objectName: `Phase number bg ${i + 1}` });
    s.addText(phases[i][0], { x: x + 0.25, y: 1.5, w: 0.55, h: 0.55, fontSize: 18, bold: true, fontFace: "Cambria", color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Phase number ${i + 1}` });
    s.addText(phases[i][1], { x: x + 0.25, y: 2.2, w: pw - 0.5, h: 0.6, fontSize: 16, bold: true, color: C.background1, valign: "top", margin: 0, isTextBox: true, objectName: `Phase title ${i + 1}` });
    s.addText(phases[i][2], { x: x + 0.25, y: 2.85, w: pw - 0.5, h: 0.95, fontSize: 13, color: C.background2, valign: "top", margin: 0, isTextBox: true, objectName: `Phase detail ${i + 1}` });
    s.addText(phases[i][3], { x: x + 0.25, y: 3.8, w: pw - 0.5, h: 0.5, fontSize: 13, italic: true, bold: true, color: C.accent2, valign: "top", margin: 0, isTextBox: true, objectName: `Phase question ${i + 1}` });
    if (i < phases.length - 1) {
      s.addShape(pres.shapes.RIGHT_ARROW, { x: x + pw + 0.08, y: 2.6, w: 0.22, h: 0.3, fill: { color: C.accent3 }, line: { type: "none" }, objectName: `Phase arrow ${i + 1}` });
    }
  }
  s.addText("Thank you. Questions?", { x: 0.5, y: 4.6, w: 9.0, h: 0.5, fontSize: 22, bold: true, fontFace: "Cambria", color: C.background1, margin: 0, isTextBox: true, objectName: "Closing" });
  s.addNotes("Presenter: Imranjit (0:25).\n\nFinally, how we'll scale this up. First, we finish Sprint 3, so we have a trustworthy baseline. Then we grow from eight to about twenty or thirty papers on the same topic. More similar papers make the wrong-paper test harder, and the question is whether citation precision stays near 1.00. After that, we add a second topic to check the system isn't tuned to one field, and only then go to hundreds of papers.\n\nThank you. We're happy to take questions.");

  await pres.writeFile({ fileName: "WIL-Project-24-RAG-Presentation.pptx" });
  await applyTheme("WIL-Project-24-RAG-Presentation.pptx", THEME);
  console.log("written");
})();
