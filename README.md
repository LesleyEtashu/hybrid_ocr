# OCR Benchmark Framework for Document-to-Markdown Conversion

> Quantifying text extraction quality and structure preservation across leading OCR solutions.

## Highlights

| | |
|---|---|
| 🏆 **Best single model** | LlamaIndex — CER 6.3%, Similarity 90% |
| 🔀 **Best fused output** | G2 hybrid — CER 5.65%, Similarity 92.25% |
| 📄 **Models benchmarked** | 27 across open-source and API |

---

## Contributors

Thanks to the people who contributed to this project:

- [@GeisolUrbina](https://github.com/GeisolUrbina)
- [@sharminmousumi](https://github.com/sharminmousumi)
- [@LesleyEtashu](https://github.com/LesleyEtashu)
- [@Linniea](https://github.com/Linniea)

---

## Table of Contents

- [Background](#background)
- [Scope](#scope)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Models Evaluated](#models-evaluated)
- [Evaluation Methodology](#evaluation-methodology)
- [Quickstart](#quickstart)
- [Experiments & Notebooks](#experiments--notebooks)
- [Hybrid Pipeline](#hybrid-pipeline)
- [Results](#results)

---
## Architecture
 
The system is built around five layers: Model Inference, Structuring, Evaluation, Diversity Analysis, and Hybrid Reasoning. Together they form a full pipeline from raw PDF to validated Markdown output.
 
→ See [`docs/architecture.md`](docs/architecture.md) for the full system design.

## Background

Converting PDFs to machine-readable format is a critical step in modern data pipelines. This project establishes a **reproducible benchmark framework** for evaluating leading OCR solutions on complex document types: financial reports, technical documentation, and layout-intensive formats (tables, multi-column layouts, embedded figures).

The framework covers the full pipeline — from raw model output to structured JSON — and includes a hybrid fusion approach for optimized production output.

---

## Scope

| Area | What we measure |
|---|---|
| **OCR quality** | Character and word-level text extraction (CER / WER) |
| **Structure preservation** | Headings, lists, tables, multi-column layouts |
| **Image handling** | Text embedded in figures and diagrams |
| **Hybrid output** | Ensemble/LLM-based fusion of multiple model outputs |
| **Pipeline automation** | End-to-end PDF → Markdown → JSON |

---
## Future Improvements

Potential improvements and out-of-scope architectural changes (e.g., unified model interfaces, pipeline standardization, and code modularization) are documented in [FUTURE.md](./FUTURE.md).

---

## Repository Structure

```
.
├── README.md
├── CHANGELOG.md
├── requirements.txt
│
├── docs/
│   └── architecture.md               # System design and pipeline overview
│
├── data/
│   ├── benchmark/                    # PDFs used across all tests
│   ├── ground_truth/
│   │   ├── dataset/                  # Verified ground truth in JSON and Markdown
│   │   ├── notebooks/
│   │   │   └── model_analysis.ipynb  # Statistical analysis and baseline selection
│   │   └── llm_analysis/
│   │       └── run_llm_analysis_llamaindex_baseline.py
│   └── model_outputs/                # Raw model outputs (.md and .json per model)
│
├── structocr/
│   ├── hybrid/
│   │   └── fusion_pipeline.py        # LLM-based hybrid fusion
│   └── processing/
│       └── json_conversion.py        # Converts Markdown outputs to JSON
│
├── experiments/
│   ├── model_testing/                # Per-model OCR notebooks
│   │   ├── model_GLM_ocr.ipynb
│   │   ├── model_claude3_haiku.ipynb
│   │   └── ...
│   ├── model_evaluations/
│   │   └── ocr_model_comparison.ipynb  # Cross-model evaluation and ranking
│   └── error_analysis/
│       ├── component_segmentation.ipynb
│       ├── error_correlation.ipynb
│       ├── error_profile.ipynb
│       └── similarity.ipynb
│
└── Results/
        ├── fused_output_evaluation.png
        ├── results_description.md
        ├── similarity_score_across_all_ocrmodels.png
        └── wer_and_cer_across_all_ocrmodels.png

```


## Models Evaluated

27 models evaluated across open-source and API-based solutions, covering classical OCR engines, layout-aware parsers, and general-purpose LLMs used for extraction.

| Model | Type | Notes |
|---|---|---|
| llamaindex | API | Top performer across all three metrics |
| hunyuan | Open source | Solid CER with good similarity retention |
| deepseek_ocr2 | Open source | Good similarity, improved over v1 |
| docling | Open source | Layout-aware parser, struggles with tables |
| tesseract | Open source | Classic baseline, outperformed by most modern models |
| pdfplumber | Open source | Text-layer extraction only, no visual understanding |
| landingai | API | CER > 700% due to severe hallucination |

→ See [`docs/models.md`](docs/models.md) for the full list of all 27 models with type and notes.

---

## Evaluation Methodology

This project uses three complementary metrics to evaluate OCR quality: CER, WER, and Similarity Score. Together they provide a nuanced picture — from individual character errors to overall text similarity.

### Character Error Rate (CER)

CER measures the proportion of incorrect characters by comparing OCR output with ground truth (manually verified reference text). The metric is based on Levenshtein distance — the minimum number of operations (substitution, deletion, insertion) required to transform one string into another.

$$CER = \frac{S + D + I}{N}$$

Where:
- `S` = number of substitutions (incorrect character, e.g., `ä → a`)
- `D` = number of deletions (missing characters, e.g., `house → huse`)
- `I` = number of insertions (extra characters, e.g., `car → carr`)
- `N` = total number of characters in the reference text

Example:

```
Ground truth: "Greetings"
OCR result:   "Gretings"

Error: 1 deletion (e)
CER = 1/9 = 11%
```

**Normalized CER:** The standard formula can yield values over 100% if the OCR output is much longer than the reference.

$$CER_{norm} = \frac{S + D + I}{S + D + C}$$

Where `C` = correct characters — guarantees values between 0–100%.

**Why CER?** CER is invaluable for identifying systematic OCR errors, e.g., the engine consistently confusing `rn` with `m`, or missing diacritical marks like `å`, `ä`, `ö`. For texts with many special characters, this is particularly relevant.

| Text type | Good | Excellent |
|---|---|---|
| Printed text | < 5% | < 2% |
| Handwritten | < 10% | < 5% |
| Historical documents | < 15% | < 8% |


### Word Error Rate (WER)

WER applies the same Levenshtein principle but at word level instead of character level. This captures the practical consequence of errors: a single character error can corrupt an entire word.

$$WER = \frac{S_w + D_w + I_w}{N_w}$$

Where:
- `S_w` = number of substitutions (replaced words)
- `D_w` = number of deletions (removed words)
- `I_w` = number of insertions (added words)
- `N_w` = total number of words in the reference text

Example:

```
Ground truth: "The quick brown fox jumps"
OCR result:   "The quick brovn fox junps"

Error: 2 words ("brown"→"brovn", "jumps"→"junps")
WER = 2/5 = 40%
```

**Why WER?** WER directly reflects how well full-text search will perform. With 10% WER, every tenth search risks failing. For applications like document search, indexing, or text analysis, WER is often the most relevant metric.

| Use case | Acceptable WER |
|---|---|
| Full-text search | < 5% |
| High precision | < 2% |
| Critical documents | < 1% |


### Similarity Score

Unlike CER/WER which measure errors, Similarity Score measures likeness. We use `difflib.SequenceMatcher` which implements the Ratcliff/Obershelp algorithm — it recursively finds the longest contiguous matching subsequences.

$$Similarity = \frac{2M}{T}$$

Where:
- `M` = number of matching characters
- `T` = total number of characters in both strings

Returns a value between 0 (completely different) and 1 (identical).

**Why Similarity Score?** While CER/WER penalize all errors equally, Similarity Score provides a more "human" assessment. A text with few scattered errors gets high similarity, while a text with concentrated errors (e.g., a completely misread paragraph) gets low similarity even if CER is similar. It's also intuitive — "97% similarity" is easier to understand than "3% CER".

### Metrics in Combination

```
Ground truth: "Stockholm City Hall was built in 1923"
OCR output:   "Stokholm  City Hall was bilt in 1923"

CER:        5.4%   → Most characters correct
WER:        28.6%  → Errors spread across multiple words
Similarity: 94.6%  → Overall text is usable
```

This combination reveals patterns that individual metrics miss:

| Pattern | Interpretation |
|---|---|
| High CER + Low WER | Errors concentrated in few words |
| Low CER + High WER | Few errors but spread across many words |
| Low Similarity despite low CER | Structural problems (wrong order, missing sections) |

---

### Implementation

```python
from difflib import SequenceMatcher


def levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def cer(ref: str, hyp: str) -> float:
    return levenshtein(ref, hyp) / len(ref) if ref else 0.0


def wer(ref: str, hyp: str) -> float:
    r, h = ref.split(), hyp.split()
    return levenshtein(r, h) / len(r) if r else 0.0


def similarity(ref: str, hyp: str) -> float:
    return SequenceMatcher(None, ref, hyp).ratio()
```

---

## Quickstart

```bash
git clone https://github.com/your-org/structocr.git
cd structocr
pip install -r requirements.txt
```

**Run a model evaluation:**

```bash
jupyter notebook experiments/model_evaluations/ocr_model_comparison.ipynb
```

**Convert Markdown outputs to JSON:**

```bash
python structocr/processing/json_conversion.py \
    --input data/model_outputs/mistral/ \
    --output data/model_outputs/mistral_json/
```

**Run the hybrid fusion pipeline:**

```bash
python structocr/hybrid/fusion_pipeline.py \
    --models mistral docling llamaparse \
    --input data/benchmark/ \
    --output results/hybrid/
```

---

## Experiments & Notebooks

### Model Testing (`experiments/model_testing/`)

One notebook per model. Each runs the model against the benchmark PDFs and saves raw outputs to `data/model_outputs/`.

### Model Evaluation (`experiments/model_evaluations/`)

[`ocr_model_comparison.ipynb`](experiments/model_evaluations/ocr_model_comparison.ipynb) — Cross-model scoring on CER, WER, and Similarity. Produces ranked comparison tables and visualizations.

### Error Analysis (`experiments/error_analysis/`)

Four notebooks developed to systematically characterize failure modes across OCR models — going beyond aggregate metrics to understand *where* and *why* models fail, and to inform candidate selection for the hybrid pipeline.

| Notebook | Used in hybrid selection | Purpose |
|----------|:------------------------:|---------|
| [`component_segmentation.ipynb`](experiments/error_analysis/component_segmentation.ipynb) | ✅ | Segments documents into structural components (headings, tables, captions, figures) and computes CER/WER per type. Reveals that models rarely fail uniformly — enabling component-level weight assignment in the fusion pipeline. |
| [`error_correlation.ipynb`](experiments/error_analysis/error_correlation.ipynb) | ✅ | Measures whether model errors are independent or correlated. Produces a pairwise error-overlap matrix — models with low mutual correlation are strongest fusion candidates. |
| [`error_profile.ipynb`](experiments/error_analysis/error_profile.ipynb) | — | Builds per-model error signatures: substitution patterns (e.g. `rn → m`, `ä → a`), deletion hotspots, insertion noise. Useful for diagnosing font-specific or encoding failures. |
| [`similarity.ipynb`](experiments/error_analysis/similarity.ipynb) | — | Identifies structurally divergent outputs where CER is acceptable but paragraph order, section boundaries, or list structure are wrong. |

> **Why `component_segmentation` + `error_correlation`?** The hybrid pipeline needs two things from its candidate models: *complementary strengths* and *non-overlapping failures*. Component segmentation answers the first question — which model is best at which part of a document. Error correlation answers the second — if two models consistently fail on the same words or characters, ensembling them adds little value: you get the same error twice. Together they give a principled basis for model selection rather than picking purely on overall benchmark rank

### Ground Truth Analysis (`data/ground_truth/notebooks/`)

[`model_analysis.ipynb`](data/ground_truth/notebooks/model_analysis.ipynb) — Statistical analysis for baseline selection and ground truth validation.

---
## Hybrid Pipeline

`structocr/hybrid/fusion_pipeline.py` implements an async LLM-based fusion pipeline that merges outputs from multiple OCR models into a single high-quality Markdown document.

For each page:
- Sends model outputs to GPT-4.1 (via OpenRouter) for structured fusion
- Skips LLM (fast-path) if outputs are already highly similar
- Validates Markdown structure (headers, tables)
- Falls back to best source if validation fails
- Computes confidence (pairwise Jaccard similarity)
- Outputs: `.md` (fused document) and `.json` (per-page metadata)
- Runs concurrently via MAX_CONCURRENCY

### Data Pipeline

Markdown → JSON

`structocr/processing/json-script.py` converts OCR outputs into structured, page-aligned JSON.

- Parses `.md` files per model
- Splits into pages (`Page_1`, `Page 2`, …)
- Extracts page content
- Stores results in a structured JSON schema: 
```
{
  "model_name": "...",
  "document_name": "...",
  "pages": [
    { "page_number": 1, "content": "..." }
  ]
}
```
Saved to:
```
datasets/<model_name>/*_document.json
```

### Flow
```
Markdown (.md per model)
        ↓
json-script.py
        ↓
Structured JSON
        ↓
fusion_pipeline.py
        ↓
Fused Markdown + JSON
```

### Why it matters

The fusion pipeline depends on page-aligned JSON to:
- Compare models consistently
- Merge content at page level
- Compute confidence scores
Without this step, fusion is not possible.

Usage
```
python structocr/processing/json_conversion.py <input_folder> <document_name>
```
---

## Results

Aggregated results and visualizations are saved to `results/` after running the evaluation notebooks.

Per-model JSON metrics are also embedded in `data/model_outputs/<model>/` alongside each model's raw Markdown output.

### Model Comparison

Full benchmark across all 27 evaluated models. Lower CER/WER is better; higher Similarity is better.

<img width="1782" height="1261" alt="wer_and_cer_across_all_ocrmodels" src="https://github.com/user-attachments/assets/3baca0cd-ebc6-4467-b3c2-074ead39e8b9" />
<img width="1190" height="790" alt="similarity_score_across_all_ocrmodels" src="https://github.com/user-attachments/assets/4485d717-e382-428e-8851-a134489b9573" />



| Model | CER ↓ | WER ↓ | Similarity ↑ |
|---|---|---|---|
| **llamaindex** | **6.29%** | **6.71%** | **90.04%** |
| chandra | 12.34% | 12.68% | 19.59% |
| hunyuan | 12.62% | 13.00% | 74.90% |
| docling | 21.28% | 30.46% | 28.24% |
| deepseek_ocr2 | 23.11% | 33.41% | 69.93% |
| deepseek_ocr | 25.70% | 34.09% | 20.53% |
| lightonocr | 26.46% | 27.26% | 44.55% |
| sonnet4 | 37.74% | 43.86% | 41.01% |
| trocr | 43.27% | 64.20% | 29.57% |
| latex | 48.22% | 55.89% | 27.14% |
| mistral | 55.02% | 66.84% | 23.89% |
| qwen25 | 58.85% | 62.31% | 9.00% |
| easyocr | 61.61% | 75.92% | 16.41% |
| llamaparse | 63.77% | 75.90% | 16.13% |
| gemini2.5 | 63.95% | 77.22% | 15.51% |
| pdfplumber | 63.97% | 77.22% | 15.52% |
| haiku | 64.30% | 76.67% | 9.15% |
| nemotron_ocr | 67.97% | 92.89% | 3.44% |
| paddle_ocr | 68.22% | 82.88% | 12.04% |
| doctr | 69.61% | 90.76% | 8.09% |
| tesseract | 71.75% | 81.98% | 9.42% |
| florence2 | 77.40% | 98.30% | 0.34% |
| surya | 77.63% | 93.54% | 8.13% |
| GLM_ocr | 81.89% | 91.85% | 24.47% |
| Qianfan_ocr | 86.29% | 89.12% | 2.56% |
| landingai | 733.73% | 210.96% | 4.43% |

> **Note:** `landingai`'s CER exceeds 100% due to hallucinated content significantly longer than the reference — a sign of generative drift rather than pure extraction failure.

### Fused Output Evaluation

This evaluation examines four groups of merged OCR models, each constructed from a distinct combination
of components selected for their complementary strengths and low error correlation.
The hybrid fusion approach aims to produce outputs that closely resemble the source document,
leveraging inter-model reinforcement to mitigate individual weaknesses.


<img width="800" height="442" alt="79103041-aa2f-46a9-a621-4562d174a6b0" src="https://github.com/user-attachments/assets/aeed1353-c6be-4945-ad03-781c907a9536" />
<img width="800" height="478" alt="0d7680f0-5642-48d7-8028-2002c53c4d72" src="https://github.com/user-attachments/assets/c953843b-2251-40dc-a711-8d440e0b1cf0" />

<img width="800" height="455" alt="3b6bc661-5140-4172-b112-e2fedc314c81" src="https://github.com/user-attachments/assets/a4499356-2842-4eef-aa17-fd7a5c2c521c" />


## Model Evaluation Results

| Group | Models/Combination                     | CER % | WER % | Similarity % |
|-------|----------------------------------------|------:|------:|-------------:|
| G1    | LlamaIndex, Hunyuan, Surya             | 15.90 | 18.04 |        76.63 |
| G2    | Hunyuan, Chandra, LlamaIndex           |  5.65 |  6.11 |        92.25 |
| G3    | Docling, LlamaIndex, Hunyuan           |  5.38 |  6.75 |        88.11 |
| G4    | LlamaIndex, Hunyuan, DeepSeek          |  5.22 |  6.97 |        85.60 |
| G5    | Docling, Tesseract, EasyOCR            | 25.91 | 31.71 |        71.74 |
| G6    | DeepSeekOCR2, Sonnet4, Docling         |  8.52 |  8.05 |        78.67 |
| G7    | Docling, DeepSeek, Hunyuan             | 11.63 | 11.70 |        77.23 |
| G8    | Chandra, Qwen2.5, Sonnet4             |  9.20 |  9.47 |        77.40 |
| G9    | DeepSeekOCR2, LightOnOCR, Mistral     | 44.08 | 50.82 |        33.48 |
| G10   | GLM, Mistral, Hunyuan                  | 48.61 | 57.66 |        27.81 |
| G11   | Mistral, DeepSeek, Sonnet4             | 43.72 | 50.09 |        32.63 |
| G12   | Docling, Hunyuan, Chandra              | 11.32 | 11.32 |        76.00 |
| G13   | Chandra, LightOnOCR, Surya             | 30.00 | 33.22 |        44.76 |
| G14   | GLM, Doctr, EasyOCR                    | 60.56 | 77.63 |        70.37 |
| G15   | Qianfan, Chandra, PaddleOCR           | 21.38 | 23.70 |        81.48 |
| G16   | Gemini2.5, LlamaParse, PDFPlumber     | 35.60 | 34.66 |        48.89 |

Lower CER/WER = Better | Higher Similarity = Better
> **Best overall:** G2 achieves the highest similarity (92.25%) with a very low CER (5.65%) and WER (6.11%).

> **Lowest CER:** G4 (5.22%) using LlamaIndex, Hunyuan, DeepSeek, though with slightly lower similarity (85.62%) compared to G2.

> **Worst performing:** G10 (48.61% CER, 57.67% WER, 27.78% similarity) — the weakest group overall.



