import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/somesh/Desktop/College/Sem 7/Mini-project";
const SKILL_DIR = "/Users/somesh/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations";
const buildDir = path.join(workspaceDir, ".presentation-build");
const finalPath = path.join(workspaceDir, "presentation/output/Tox21_Project_Defense_Final.pptx");
const stagingDir = path.join(workspaceDir, ".codex-finalizer");

const {
  resolvePresentationFont,
  applyPresentationChartFont,
  makeNativeBulletParagraphs,
  finalizePresentation,
} = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href);

const font = resolvePresentationFont();
const W = 1280;
const H = 720;
const C = {
  navy: "#071F33",
  ink: "#122638",
  blue: "#155E75",
  cyan: "#38BDF8",
  teal: "#0F9D8A",
  lightTeal: "#DFF7F2",
  pale: "#F4F7FA",
  white: "#FFFFFF",
  gray: "#5F7181",
  lightGray: "#D9E2E8",
  orange: "#F59E0B",
  red: "#C2413A",
};

const presentation = Presentation.create({ slideSize: { width: W, height: H } });

function addText(slide, text, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: font,
    fontSize: options.fontSize ?? 24,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    alignment: options.alignment ?? "left",
    verticalAlignment: options.verticalAlignment ?? "top",
    autoFit: "none",
  };
  return shape;
}

function addRect(slide, left, top, width, height, fill, radius = false, lineFill = fill) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: { left, top, width, height },
    fill,
    line: { fill: lineFill, width: 1 },
  });
}

function addTitle(slide, title, number, dark = false) {
  addText(slide, title, 64, 38, 1070, 58, {
    fontSize: 34,
    bold: true,
    color: dark ? C.white : C.navy,
  });
  addText(slide, String(number).padStart(2, "0"), 1170, 45, 46, 35, {
    fontSize: 16,
    bold: true,
    alignment: "right",
    color: dark ? C.cyan : C.teal,
  });
  addRect(slide, 64, 104, 1152, 3, dark ? C.cyan : C.teal);
}

function addFooter(slide, dark = false) {
  addText(slide, "BT5230  |  Somesh Jaiswal  |  CO23BTECH11022", 64, 685, 620, 22, {
    fontSize: 11,
    color: dark ? "#B6C8D5" : "#7B8C99",
  });
}

function addBullets(slide, items, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = makeNativeBulletParagraphs(items, {
    marginLeftPoints: options.marginLeftPoints ?? 20,
    hangingPoints: options.hangingPoints ?? 9,
    spaceAfterPoints: options.spaceAfterPoints ?? 12,
  });
  shape.text.style = {
    typeface: font,
    fontSize: options.fontSize ?? 22,
    color: options.color ?? C.ink,
    autoFit: "none",
  };
  return shape;
}

function addNotes(slide, text) {
  slide.speakerNotes.textFrame.setText(text);
}

function addProcessNode(slide, x, y, w, h, heading, detail, fill = C.white) {
  addRect(slide, x, y, w, h, fill, true, C.blue);
  addText(slide, heading, x + 14, y + 12, w - 28, 48, {
    fontSize: 18,
    bold: true,
    color: C.navy,
    alignment: "center",
  });
  addText(slide, detail, x + 14, y + 66, w - 28, h - 76, {
    fontSize: 15,
    color: C.gray,
    alignment: "center",
  });
}

function addArrow(slide, x, y, w = 38, h = 22) {
  slide.shapes.add({
    geometry: "rightArrow",
    position: { left: x, top: y, width: w, height: h },
    fill: C.teal,
    line: { fill: C.teal, width: 0 },
  });
}

// Slide 1: Cover
{
  const slide = presentation.slides.add();
  slide.background.fill = C.navy;
  const coverBytes = await fs.readFile(path.join(workspaceDir, "presentation/assets/ai_toxicity_cover.png"));
  slide.images.add({
    blob: coverBytes,
    contentType: "image/png",
    alt: "Scientific illustration of a molecule connected to a neural network",
    fit: "cover",
    position: { left: 0, top: 0, width: W, height: H },
  });
  addRect(slide, 0, 0, 610, H, "#071F33CC");
  addText(slide, "Multi-Task Prediction of\nTox21 Assay Activity", 72, 145, 560, 180, {
    fontSize: 46,
    bold: true,
    color: C.white,
  });
  addText(slide, "AI for early toxicity screening from molecular structure", 76, 350, 500, 75, {
    fontSize: 23,
    color: "#CDEAF3",
  });
  addRect(slide, 76, 450, 135, 4, C.cyan);
  addText(slide, "Somesh Jaiswal\nCO23BTECH11022\nBT5230 AI for Drug Discovery", 76, 480, 460, 120, {
    fontSize: 20,
    color: C.white,
  });
  addNotes(slide, "Introduce yourself and the project. State that the model predicts activity in 12 Tox21 pathway assays from a SMILES string. Clarify that this is an educational early-screening model, not a clinical toxicity decision tool. Cover image was generated for this presentation using OpenAI image generation and carries no factual claim.");
}

// Slide 2: Project overview
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "Project overview", 2);
  addText(slide, "Research question", 72, 150, 300, 42, { fontSize: 21, bold: true, color: C.teal });
  addText(slide, "Can one molecular model predict activity across 12 related toxicity assays?", 72, 198, 510, 100, { fontSize: 31, bold: true, color: C.navy });
  addRect(slide, 640, 150, 4, 430, C.lightGray);
  addBullets(slide, [
    "Input: one SMILES string",
    "Output: 12 assay activity probabilities",
    "Data: 7,823 valid Tox21 molecules",
    "Main model: shared multi-task neural network",
    "Evaluation: scaffold split with ROC-AUC and PR-AUC",
    "Interface: Streamlit web application",
  ], 700, 155, 485, 430, { fontSize: 21, spaceAfterPoints: 15 });
  addText(slide, "Goal", 72, 365, 140, 34, { fontSize: 19, bold: true, color: C.teal });
  addText(slide, "Prioritise compounds for further testing before expensive laboratory work.", 72, 405, 505, 100, { fontSize: 25, color: C.ink });
  addFooter(slide);
  addNotes(slide, "Use this slide as the map of the talk. The project starts with a SMILES string and returns 12 assay-specific probabilities. The main scientific question is whether sharing information among assays improves performance over separate models.");
}

// Slide 3: Problem
{
  const slide = presentation.slides.add();
  slide.background.fill = C.pale;
  addTitle(slide, "The screening problem", 3);
  addText(slide, "Experimental testing", 78, 155, 320, 40, { fontSize: 23, bold: true, color: C.navy });
  addBullets(slide, [
    "Reliable biological evidence",
    "Requires time, reagents and equipment",
    "Difficult to run every compound in every assay",
  ], 78, 210, 430, 230, { fontSize: 21 });
  addText(slide, "Computational screening", 730, 155, 370, 40, { fontSize: 23, bold: true, color: C.navy });
  addBullets(slide, [
    "Ranks candidates before experiments",
    "Uses molecular structure alone",
    "Cannot replace experimental validation",
  ], 730, 210, 430, 230, { fontSize: 21 });
  addArrow(slide, 570, 275, 90, 48);
  addRect(slide, 180, 485, 920, 135, C.navy, true, C.navy);
  addText(slide, "Problem statement", 215, 505, 200, 30, { fontSize: 18, bold: true, color: C.cyan });
  addText(slide, "Predict the probability that a molecule is active in each Tox21 assay while handling missing and imbalanced labels.", 215, 548, 835, 66, { fontSize: 22, color: C.white });
  addFooter(slide);
  addNotes(slide, "Explain the role of computation as a prioritisation layer. Laboratory assays remain necessary. The machine-learning problem is multi-label and partially labelled because each molecule may have several activities and many assay entries are blank.");
}

// Slide 4: Dataset
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "Tox21 dataset", 4);
  addText(slide, "7,831", 78, 145, 260, 90, { fontSize: 60, bold: true, color: C.blue });
  addText(slide, "raw rows", 82, 230, 220, 35, { fontSize: 20, color: C.gray });
  addText(slide, "8", 400, 145, 180, 90, { fontSize: 60, bold: true, color: C.red });
  addText(slide, "invalid SMILES removed", 404, 230, 230, 55, { fontSize: 20, color: C.gray });
  addText(slide, "7,823", 730, 145, 260, 90, { fontSize: 60, bold: true, color: C.teal });
  addText(slide, "valid molecules", 734, 230, 230, 35, { fontSize: 20, color: C.gray });
  addText(slide, "12", 1040, 145, 150, 90, { fontSize: 60, bold: true, color: C.orange });
  addText(slide, "assay tasks", 1044, 230, 150, 35, { fontSize: 20, color: C.gray });
  addRect(slide, 78, 330, 530, 180, C.lightTeal, true, C.lightTeal);
  addText(slide, "Nuclear receptor assays", 110, 360, 470, 36, { fontSize: 25, bold: true, color: C.navy });
  addText(slide, "AR, AR-LBD, AhR, Aromatase, ER,\nER-LBD and PPAR-gamma", 110, 412, 450, 75, { fontSize: 21, color: C.ink });
  addRect(slide, 670, 330, 530, 180, "#E8F1FA", true, "#E8F1FA");
  addText(slide, "Stress response assays", 702, 360, 460, 36, { fontSize: 25, bold: true, color: C.navy });
  addText(slide, "ARE, ATAD5, HSE, MMP and p53", 702, 412, 450, 75, { fontSize: 21, color: C.ink });
  addText(slide, "Blank label = not measured. It must not be treated as inactive.", 78, 565, 1100, 45, { fontSize: 23, bold: true, color: C.red, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "The public Tox21/MoleculeNet CSV contained 7,831 rows. RDKit rejected eight SMILES, leaving 7,823 valid molecules. Explain the two assay families. Source: Huang et al. 2016; MoleculeNet; project results/data_summary.json.");
}

// Slide 5: Existing approaches
{
  const slide = presentation.slides.add();
  slide.background.fill = C.pale;
  addTitle(slide, "Existing approaches", 5);
  const x = [72, 352, 632, 912];
  const headings = ["Experimental assays", "Rule-based alerts", "Single-task QSAR", "Deep learning"];
  const details = [
    "Direct biological measurement\n\nStrong evidence\nHigher cost and slower throughput",
    "Known toxicophores and expert rules\n\nEasy to explain\nLimited to recognised patterns",
    "One model for each assay\n\nSimple and fast\nDoes not share information",
    "Learns nonlinear structure patterns\n\nCan share representations\nNeeds careful validation",
  ];
  const fills = ["#E7EFF6", "#F8EED8", "#E2F4EF", "#E9E8F8"];
  for (let i = 0; i < 4; i++) {
    addRect(slide, x[i], 155, 230, 390, fills[i], true, fills[i]);
    addText(slide, String(i + 1).padStart(2, "0"), x[i] + 22, 178, 50, 32, { fontSize: 16, bold: true, color: C.teal });
    addText(slide, headings[i], x[i] + 22, 222, 186, 68, { fontSize: 24, bold: true, color: C.navy });
    addText(slide, details[i], x[i] + 22, 310, 186, 200, { fontSize: 18, color: C.ink });
  }
  addText(slide, "This project compares a shared multi-task neural network with 12 separate logistic-regression models.", 110, 585, 1060, 45, { fontSize: 23, bold: true, color: C.blue, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Describe the progression from experimental testing to computational prediction. The fair comparison in this project is the single-task logistic baseline, not every published toxicity model. Source: project methodology and Huang et al. 2016.");
}

// Slide 6: Proposed workflow
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "Proposed workflow", 6);
  const nodes = [
    [55, "Tox21 CSV", "Structures and sparse assay labels"],
    [260, "Clean molecules", "Validate and canonicalise SMILES"],
    [465, "Scaffold split", "80% train, 10% validation, 10% test"],
    [670, "Build features", "ECFP4 plus 8 descriptors"],
    [875, "Train model", "Shared MLP with 12 outputs"],
    [1080, "Use app", "SMILES to assay probabilities"],
  ];
  for (let i = 0; i < nodes.length; i++) {
    addProcessNode(slide, nodes[i][0], 235, 150, 165, nodes[i][1], nodes[i][2], i === 4 ? C.lightTeal : C.pale);
    if (i < nodes.length - 1) addArrow(slide, nodes[i][0] + 158, 305, 38, 24);
  }
  addText(slide, "Test set remains untouched until final evaluation", 410, 470, 460, 42, { fontSize: 23, bold: true, color: C.red, alignment: "center" });
  addText(slide, "The same feature calculation and saved scaler are used during training and Streamlit prediction.", 215, 550, 850, 55, { fontSize: 21, color: C.gray, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Walk through the end-to-end pipeline from left to right. Emphasise that the validation set selects the model and the test set is used only for the final reported result.");
}

// Slide 7: Molecular representation
{
  const slide = presentation.slides.add();
  slide.background.fill = C.pale;
  addTitle(slide, "Molecular representation", 7);
  addRect(slide, 75, 155, 470, 390, C.white, true, C.lightGray);
  addText(slide, "ECFP4 fingerprint", 112, 190, 390, 42, { fontSize: 28, bold: true, color: C.navy });
  addText(slide, "2,048 binary bits", 112, 246, 390, 42, { fontSize: 22, bold: true, color: C.teal });
  addBullets(slide, [
    "Captures local atom environments",
    "Represents structural fragments",
    "Used for model input and similarity",
  ], 112, 310, 370, 180, { fontSize: 20 });
  addText(slide, "+", 583, 285, 110, 100, { fontSize: 70, bold: true, color: C.blue, alignment: "center" });
  addRect(slide, 735, 155, 470, 390, C.white, true, C.lightGray);
  addText(slide, "Molecular descriptors", 772, 190, 390, 42, { fontSize: 28, bold: true, color: C.navy });
  addText(slide, "8 scaled values", 772, 246, 390, 42, { fontSize: 22, bold: true, color: C.teal });
  addText(slide, "Molecular weight\nlogP and TPSA\nH-bond donors and acceptors\nRotatable bonds\nRing count and heavy atoms", 772, 310, 370, 190, { fontSize: 20, color: C.ink });
  addText(slide, "Final input size: 2,056 features per molecule", 300, 590, 680, 42, { fontSize: 25, bold: true, color: C.blue, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Explain that ECFP4 encodes substructure presence while the eight descriptors provide global physicochemical information. The StandardScaler fits only on training descriptors to avoid data leakage. RDKit calculates all features.");
}

// Slide 8: Architecture
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "Multi-task neural network", 8);
  const layers = [
    [90, 215, 175, 205, "Input", "2,056 features", "#E7EFF6"],
    [330, 245, 175, 145, "Hidden layer", "256 units\nReLU + BatchNorm", "#DFF7F2"],
    [570, 260, 175, 115, "Hidden layer", "128 units\nReLU + Dropout", "#DFF7F2"],
    [810, 230, 175, 175, "Output", "12 logits", "#F8EED8"],
    [1050, 195, 150, 245, "Assays", "NR-AR\nNR-AhR\n...\nSR-p53", "#E9E8F8"],
  ];
  for (let i = 0; i < layers.length; i++) {
    addRect(slide, layers[i][0], layers[i][1], layers[i][2], layers[i][3], layers[i][6], true, layers[i][6]);
    addText(slide, layers[i][4], layers[i][0] + 12, layers[i][1] + 16, layers[i][2] - 24, 56, { fontSize: 21, bold: true, color: C.navy, alignment: "center" });
    addText(slide, layers[i][5], layers[i][0] + 12, layers[i][1] + 78, layers[i][2] - 24, layers[i][3] - 88, { fontSize: 16, color: C.ink, alignment: "center" });
    if (i < layers.length - 1) addArrow(slide, layers[i][0] + layers[i][2] + 18, 300, 36, 24);
  }
  addText(slide, "Shared hidden layers learn patterns that may be useful across related assays.", 245, 520, 790, 50, { fontSize: 25, bold: true, color: C.blue, alignment: "center" });
  addText(slide, "Sigmoid converts each output logit into an activity probability.", 320, 585, 640, 38, { fontSize: 20, color: C.gray, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Explain shared representation learning. All 12 tasks use the same feature extractor but have separate output neurons. Architecture: 2056 to 256 to 128 to 12, ReLU activations, batch normalisation and dropout.");
}

// Slide 9: Training strategy
{
  const slide = presentation.slides.add();
  slide.background.fill = C.pale;
  addTitle(slide, "Training strategy", 9);
  addRect(slide, 70, 150, 540, 190, C.white, true, C.lightGray);
  addText(slide, "Missing labels", 105, 180, 250, 38, { fontSize: 26, bold: true, color: C.navy });
  addText(slide, "L = sum(mask x BCE) / sum(mask)", 105, 235, 445, 42, { fontSize: 24, bold: true, color: C.teal, alignment: "center" });
  addText(slide, "A blank assay label contributes zero loss.", 105, 292, 450, 32, { fontSize: 18, color: C.gray, alignment: "center" });
  addRect(slide, 670, 150, 540, 190, C.white, true, C.lightGray);
  addText(slide, "Class imbalance", 705, 180, 300, 38, { fontSize: 26, bold: true, color: C.navy });
  addText(slide, "positive weight = inactive / active", 705, 235, 445, 42, { fontSize: 24, bold: true, color: C.teal, alignment: "center" });
  addText(slide, "Each assay receives its own positive-class weight.", 705, 292, 450, 32, { fontSize: 18, color: C.gray, alignment: "center" });
  addText(slide, "Scaffold split", 72, 400, 260, 40, { fontSize: 26, bold: true, color: C.navy });
  addRect(slide, 72, 470, 750, 58, C.lightGray, true, C.lightGray);
  addRect(slide, 72, 470, 600, 58, C.teal, true, C.teal);
  addRect(slide, 672, 470, 75, 58, C.orange);
  addRect(slide, 747, 470, 75, 58, C.blue, true, C.blue);
  addText(slide, "Train 6,258", 290, 482, 180, 30, { fontSize: 19, bold: true, color: C.white, alignment: "center" });
  addText(slide, "Val", 685, 482, 50, 30, { fontSize: 16, bold: true, color: C.white, alignment: "center" });
  addText(slide, "Test", 755, 482, 60, 30, { fontSize: 16, bold: true, color: C.white, alignment: "center" });
  addText(slide, "AdamW  |  batch 128  |  learning rate 0.001  |  early stopping", 72, 570, 1100, 38, { fontSize: 22, color: C.ink, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Describe two central technical decisions: label masking and per-task class weighting. The scaffold split holds related cores together, making the test harder and closer to prediction on new chemistry. Training completed 13 epochs and saved the checkpoint with the best validation mean ROC-AUC.");
}

// Slide 10: Overall results
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "Overall test performance", 10);
  const chart = slide.charts.add("bar", {
    position: { left: 70, top: 145, width: 770, height: 440 },
    categories: ["Mean ROC-AUC", "Mean PR-AUC"],
    series: [
      { name: "Single-task logistic", values: [0.7162621, 0.3067836], fill: C.gray },
      { name: "Multi-task MLP", values: [0.7411691, 0.3415235], fill: C.teal },
    ],
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 70 },
    hasLegend: true,
    legend: { position: "bottom", overlay: false, textStyle: { fill: C.ink, fontSize: 15 } },
    xAxis: { textStyle: { fill: C.ink, fontSize: 17 }, line: { style: "solid", fill: C.lightGray, width: 1 } },
    yAxis: { min: 0, max: 0.9, majorUnit: 0.1, numberFormatCode: "0.00", textStyle: { fill: C.gray, fontSize: 14 }, majorGridlines: { style: "solid", fill: C.lightGray, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.ink, fontSize: 15, bold: true } },
    chartFill: C.white,
    chartLine: { fill: C.white, width: 0 },
    plotAreaFill: C.white,
    plotAreaLine: { fill: C.white, width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: font });
  addText(slide, "+0.025", 925, 205, 220, 65, { fontSize: 44, bold: true, color: C.teal, alignment: "center" });
  addText(slide, "mean ROC-AUC", 925, 270, 220, 35, { fontSize: 19, color: C.gray, alignment: "center" });
  addText(slide, "+0.035", 925, 375, 220, 65, { fontSize: 44, bold: true, color: C.teal, alignment: "center" });
  addText(slide, "mean PR-AUC", 925, 440, 220, 35, { fontSize: 19, color: C.gray, alignment: "center" });
  addText(slide, "Held-out scaffold test set", 905, 525, 260, 40, { fontSize: 19, bold: true, color: C.blue, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "The multi-task model achieved mean ROC-AUC 0.741 and mean PR-AUC 0.342. The single-task logistic baseline achieved 0.716 and 0.307. State the absolute improvements, not percentages. Source: results/metrics_scaffold.csv.");
}

// Slide 11: Per-assay results
{
  const slide = presentation.slides.add();
  slide.background.fill = C.pale;
  addTitle(slide, "Per-assay ROC-AUC", 11);
  const tasks = ["NR-AR", "NR-AR-LBD", "NR-AhR", "NR-Aromatase", "NR-ER", "NR-ER-LBD", "NR-PPAR-gamma", "SR-ARE", "SR-ATAD5", "SR-HSE", "SR-MMP", "SR-p53"];
  const baseline = [0.724881, 0.869024, 0.787051, 0.715189, 0.610762, 0.714860, 0.680043, 0.672265, 0.687044, 0.667451, 0.773743, 0.692832];
  const mlp = [0.716874, 0.825846, 0.829625, 0.679087, 0.652099, 0.735767, 0.768988, 0.686069, 0.711688, 0.753059, 0.807037, 0.727890];
  const chart = slide.charts.add("bar", {
    position: { left: 65, top: 128, width: 930, height: 515 },
    categories: tasks,
    series: [
      { name: "Single-task logistic", values: baseline, fill: C.gray },
      { name: "Multi-task MLP", values: mlp, fill: C.teal },
    ],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 50 },
    hasLegend: true,
    legend: { position: "bottom", overlay: false, textStyle: { fill: C.ink, fontSize: 14 } },
    xAxis: { min: 0.5, max: 0.9, majorUnit: 0.1, numberFormatCode: "0.0", textStyle: { fill: C.gray, fontSize: 13 }, majorGridlines: { style: "solid", fill: C.lightGray, width: 1 } },
    yAxis: { textStyle: { fill: C.ink, fontSize: 12 }, line: { style: "solid", fill: C.lightGray, width: 1 } },
    chartFill: C.pale,
    chartLine: { fill: C.pale, width: 0 },
    plotAreaFill: C.pale,
    plotAreaLine: { fill: C.pale, width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: font });
  addText(slide, "9 of 12", 1015, 210, 205, 65, { fontSize: 43, bold: true, color: C.teal, alignment: "center" });
  addText(slide, "assays improved", 1015, 275, 205, 32, { fontSize: 18, color: C.gray, alignment: "center" });
  addText(slide, "Largest gains", 1020, 365, 195, 32, { fontSize: 21, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "NR-PPAR-gamma\nSR-HSE", 1020, 410, 195, 75, { fontSize: 22, color: C.blue, alignment: "center" });
  addText(slide, "Baseline wins\nNR-AR\nNR-AR-LBD\nNR-Aromatase", 1020, 520, 195, 120, { fontSize: 17, color: C.red, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Point out that multi-task learning helps 9 of 12 assays but not all of them. The baseline remains stronger for NR-AR, NR-AR-LBD and NR-Aromatase, which may indicate negative transfer or limited task-specific signal. Source: results/metrics_scaffold.csv.");
}

// Slide 12: Comparison
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "Why the proposed approach helps", 12);
  addText(slide, "Single-task logistic baseline", 72, 150, 500, 45, { fontSize: 27, bold: true, color: C.gray });
  addBullets(slide, [
    "Fits each assay independently",
    "Linear decision boundary",
    "Fast and easy to explain",
    "Higher ROC-AUC on 3 assays",
  ], 72, 220, 490, 280, { fontSize: 22, spaceAfterPoints: 16 });
  addRect(slide, 620, 145, 4, 420, C.lightGray);
  addText(slide, "Proposed multi-task MLP", 685, 150, 500, 45, { fontSize: 27, bold: true, color: C.teal });
  addBullets(slide, [
    "Shares chemical patterns across assays",
    "Learns nonlinear relationships",
    "Masks missing labels during training",
    "Improves mean ROC-AUC and PR-AUC",
  ], 685, 220, 490, 280, { fontSize: 22, spaceAfterPoints: 16 });
  addRect(slide, 150, 535, 980, 75, C.navy, true, C.navy);
  addText(slide, "Measured conclusion: better average performance on this scaffold split, not universal superiority.", 185, 553, 910, 42, { fontSize: 23, bold: true, color: C.white, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Use precise wording. The project demonstrates better average performance than its controlled baseline on one scaffold split. It does not prove superiority to every published Tox21 system or to laboratory assays.");
}

// Slide 13: Streamlit app
{
  const slide = presentation.slides.add();
  slide.background.fill = C.pale;
  addTitle(slide, "Streamlit prediction interface", 13);
  addProcessNode(slide, 70, 175, 205, 145, "1. Enter SMILES", "Example: aspirin", C.white);
  addArrow(slide, 300, 235, 55, 28);
  addProcessNode(slide, 380, 175, 205, 145, "2. Calculate features", "Fingerprint and descriptors", C.white);
  addArrow(slide, 610, 235, 55, 28);
  addProcessNode(slide, 690, 175, 205, 145, "3. Predict", "Load saved scaffold model", C.lightTeal);
  addArrow(slide, 920, 235, 55, 28);
  addProcessNode(slide, 1000, 175, 205, 145, "4. Explain output", "12 probabilities and similarity", C.white);
  const chart = slide.charts.add("bar", {
    position: { left: 150, top: 385, width: 670, height: 235 },
    categories: ["NR-ER", "NR-PPAR-gamma", "SR-HSE", "SR-ATAD5"],
    series: [{ name: "Aspirin example probability", values: [0.3814, 0.3741, 0.3619, 0.3322], fill: C.teal }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 55 },
    hasLegend: false,
    xAxis: { min: 0, max: 0.5, majorUnit: 0.1, numberFormatCode: "0.0", textStyle: { fill: C.gray, fontSize: 12 }, majorGridlines: { style: "solid", fill: C.lightGray, width: 1 } },
    yAxis: { textStyle: { fill: C.ink, fontSize: 13 }, line: { style: "solid", fill: C.lightGray, width: 1 } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fill: C.ink, fontSize: 13, bold: true } },
    chartFill: C.pale,
    chartLine: { fill: C.pale, width: 0 },
    plotAreaFill: C.pale,
    plotAreaLine: { fill: C.pale, width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: font });
  addText(slide, "Example run", 900, 400, 250, 36, { fontSize: 23, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "Nearest training similarity\n1.00", 900, 455, 250, 80, { fontSize: 21, color: C.blue, alignment: "center" });
  addText(slide, "Assay activity does not equal clinical toxicity.", 865, 565, 320, 55, { fontSize: 19, bold: true, color: C.red, alignment: "center" });
  addFooter(slide);
  addNotes(slide, "Demonstrate the app live if time permits. The example values shown here come from the saved scaffold model for aspirin. Explain the nearest-neighbour similarity warning. Do not interpret the probabilities as organ toxicity or patient risk. Source: app.py and saved model inference.");
}

// Slide 14: Limitations and conclusion
{
  const slide = presentation.slides.add();
  slide.background.fill = C.navy;
  addTitle(slide, "Conclusion and limitations", 14, true);
  addText(slide, "Conclusion", 72, 145, 250, 42, { fontSize: 24, bold: true, color: C.cyan });
  addText(slide, "A shared model predicted 12 Tox21 assays and improved average scaffold-test performance over the single-task baseline.", 72, 195, 520, 170, { fontSize: 31, bold: true, color: C.white });
  addRect(slide, 640, 145, 4, 430, "#375365");
  addText(slide, "Limitations", 700, 145, 250, 42, { fontSize: 24, bold: true, color: C.cyan });
  addBullets(slide, [
    "In-vitro pathway assays are not human toxicity outcomes",
    "Sparse and imbalanced labels limit some tasks",
    "Only 2D structure information is used",
    "One dataset and split require external validation",
    "Similarity warning is not calibrated uncertainty",
  ], 700, 205, 490, 320, { fontSize: 20, color: C.white, spaceAfterPoints: 13 });
  addText(slide, "Next step: external validation and uncertainty calibration before practical safety use.", 135, 590, 1010, 45, { fontSize: 23, bold: true, color: C.cyan, alignment: "center" });
  addFooter(slide, true);
  addNotes(slide, "Finish with the measured contribution and the limitations. Future work could test graph neural networks, calibration and external datasets, but the present project already provides a complete reproducible baseline-to-app workflow.");
}

// Slide 15: References
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "References", 15);
  const refs = [
    "Huang, R. et al. (2016). Tox21Challenge to Build Predictive Models of Nuclear Receptor and Stress Response Pathways. Frontiers in Environmental Science, 3:85.",
    "Wu, Z. et al. (2018). MoleculeNet: a benchmark for molecular machine learning. Chemical Science, 9, 513-530.",
    "Tox21 Data Challenge, National Institutes of Health. tripod.nih.gov/tox21/challenge/data.jsp",
    "RDKit: Open-source cheminformatics. rdkit.org",
    "PyTorch documentation. pytorch.org",
    "Streamlit documentation. docs.streamlit.io",
  ];
  let top = 145;
  refs.forEach((ref, i) => {
    addText(slide, `[${i + 1}]`, 80, top, 55, 35, { fontSize: 18, bold: true, color: C.teal });
    addText(slide, ref, 135, top, 1040, 62, { fontSize: 18, color: C.ink });
    top += 78;
  });
  addText(slide, "Project data source", 80, 620, 220, 30, { fontSize: 17, bold: true, color: C.blue });
  addText(slide, "deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz", 300, 620, 850, 30, { fontSize: 16, color: C.gray });
  addFooter(slide);
  addNotes(slide, "Full DOI links: Huang et al. https://doi.org/10.3389/fenvs.2015.00085; MoleculeNet https://doi.org/10.1039/C7SC02664A. Tox21 official challenge page: https://tripod.nih.gov/tox21/challenge/data.jsp. RDKit: https://www.rdkit.org/. PyTorch: https://pytorch.org/. Streamlit: https://docs.streamlit.io/.");
}

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });

const candidatePath = path.join(stagingDir, "Tox21_Project_Defense_Final_candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const requirements = {
  explicitTotalSlideCount: 15,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [10, 11, 13],
  requiredEmbeddedWorkbookChartOwnerSlides: [],
  materializeLiteralChartWorkbooks: true,
};

const result = await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: process.env.RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  fontPolicy: { basis: "design", families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "Tox21_Project_Defense_Final.validation.json"),
});

console.log(JSON.stringify({ finalPath, font, result }, null, 2));
