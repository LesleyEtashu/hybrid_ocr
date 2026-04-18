# Ground Truth – PDF Extraction  
**FlexQube Annual Report 2022**

## Overview

This folder contains the **verified ground truth** for PDF extraction of the document **FlexQube Annual Report 2022**.

Ground truth was created to serve as a **stable, traceable, and reproducible reference** for:

- Evaluation of PDF extraction models
- Benchmarking of LLM-based document pipelines
- Regression testing of future models
- Qualitative analysis of OCR and extraction errors

---

## Key Principle

> **Ground truth is a controlled artifact, not a model output.**

The ground truth is **not** the result of a single model, but was produced through a **controlled and methodical process** combining:

1. Multiple independent model outputs  
2. Statistical analysis for baseline selection  
3. LLM-based difference analysis  
4. **Manual double-review against the original PDF**

**All steps affecting the content of the ground truth are documented and traceable.**

---
## Folder Structure 

```text
ground_truth/
├── README.md                           
├── CHANGELOG.md                        # Version history and changes
├── dataset                             # ground_truth in json och Markdown format
├── notebooks/                          
│   └── model_analysis.ipynb            # Statistical analysis and baseline selection
│
└── llm_analysis/                       # LLM-assisted difference analysis
  └──run_llm_analysis_llamaindex_baseline.py

   
```

### Ground Truth Location
The ground truth is stored in:
```
dataset/
```
This directory contains the final validated outputs in structured formats (e.g. .md, .json).
---

## How Ground Truth Was Created

### **Step 1 – Raw Model Outputs**

The same PDF was extracted using **four independent AI-based pipelines:**

| Model | Characters | Characteristics |
|-------|------------|-----------------|
| **Claude Sonnet 4** | 174,325 | Most compact, highest quality |
| **LlamaIndex** | 203,789 | Most words, HTML cleaned |
| **Docling** | 244,056 | Most characters, extra noise |
| **Mistral Large 3** | 219,113 | Medium, some OCR errors |

**Key principles:**
- All model outputs were saved **unmodified** in `data/model_outputs/.md/`
- These files are **never manually edited**
- Used as input for all further analysis
- Serve as revision and reproducibility documentation

> **No model is initially considered "correct".**

---

### **Step 2 – Model Analysis and Baseline Selection** 

To avoid subjective assumptions, a **statistical comparison** was performed between all model outputs.

**The analysis is documented in:**
```
notebooks/model_analysis.ipynb
```

**The analysis:**
- Calculated pairwise similarity measures between models
- Quantified the degree of agreement (consensus)
- Identified which model deviated least overall

**Results:**

| Model | Average Consensus |
|-------|-------------------|
| **LlamaIndex** 🥇 | **58.4%** (highest) |
| DeepSeek-ocr | 54.7% |
| Hunyuan | 39.3% |
| Docling | 38.7%  |

**LlamaIndex showed the highest average consensus (58.4%)** and was therefore selected as the **baseline** for further analysis.

> The baseline selection is thus **data-driven, transparent, and reproducible.**

---

### **Step 3 – LLM-based Difference Analysis** (`llm_analysis/`)

An LLM was used **only as an analysis tool, not as a source of truth.**

**The script:**
```
llm_analysis/llm_analysis_llamaindex.py
```

**The LLM's task was to:**
1. Compare all model outputs against the baseline
2. Identify explicit differences
3. Suggest possible corrections
4. Provide reasoning and confidence level

**Important to note:**
- ❌ No changes are applied automatically
- ❌ All suggestions are treated as hypotheses
- ❌ LLM output is never ground truth itself
---

### **Step 4 – Manual Double-Review** 

**All suggested corrections were manually verified against the original PDF.**

**The review process consisted of:**
1. First manual verification against PDF
2. Second review to confirm the decision
3. If any uncertainty, the suggestion was rejected

**Review results:**

| Metric | Count |
|--------|-------|
| Suggested corrections | 9 |
| **Approved corrections** | **1** ✅ |
| Rejected corrections | 8  |


> **LlamaIndex baseline was already 89% perfect (8/9 suggestions unnecessary).**

---

### **Step 5 – Ground Truth** 
The finished ground truth was saved as:
```
dataset/ground_truth.md
```

**After this step, ground truth is considered:**
- Locked
- Verified
- Ready for use

---

## Changelog and Traceability

All decisions and changes are documented in:
```
CHANGELOG.md
```

**Changelog serves as an audit log** and makes it possible to track:
- When the ground truth was established
- Which steps were performed
- How many corrections were applied
- That manual double-review was performed

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Multi-model** | Multiple models used to reduce model bias |
| **Data-driven baseline** | Baseline selected through analysis, not assumptions |
| **LLM as tool** | LLM used for analysis, not as ground truth |
| **Manual verification** | All changes verified manually against PDF |
| **Double-review** | Double-review is mandatory |
| **Conservative approach** | Only verified changes are included |
| **Full traceability** | All decisions are documented |

---

## Limitations

- Ground truth applies only to **this document** (FlexQube Annual Report 2022)
- Layout fidelity is not evaluated (focus on text content)
- The method reduces but **does not eliminate all errors**
- The result depends on the quality of the original PDF

---

## Status

| Aspect | Status |
|--------|--------|
| **Ground truth** | ✅ Complete |
| **Verification** | ✅ Manual double-review performed |
| **Applied corrections** | 1 (of 9 suggested) |
| **Baseline** | LlamaIndex (58.4% consensus) |
| **Final file** | `dataset/ground_truth.md` |

---

## Usage

This ground truth is ready to be used for:

### **Benchmarking:**
```python
# Compare new model against ground truth
from pathlib import Path
import difflib

ground_truth = Path("dataset/ground_truth.md").read_text()
new_model_output = Path("new_model_output.md").read_text()

similarity = difflib.SequenceMatcher(None, ground_truth, new_model_output).ratio()
print(f"Accuracy: {similarity:.2%}")
```

### **Model Evaluation:**
```python
# Run complete evaluation
jupyter notebook model_evaluation.ipynb
```

---

## Related Files

| File | Description |
|------|-------------|
| `CHANGELOG.md` | Version history |
| `README.md` | Detailed process description |
| `model_analysis.ipynb` | Statistical analysis and baseline selection |

---

## References

- **Original PDF:** FlexQube Annual Report 2022
- **Baseline model:** LlamaIndex
- **Verification method:** Manual double-review against PDF
- **Number of reviews:** 2 (per correction)
- **LLM for analysis:** Claude Sonnet 4 (via Anthropic API)

---
**Created:** December 17-18, 2025  
**Version:** 1.0  
**Status:** Verified and locked

