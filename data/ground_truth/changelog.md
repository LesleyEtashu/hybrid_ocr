# CHANGELOG – Ground Truth (Audit Log)

This changelog documents all decisions, verifications, and changes applied
during the construction of the ground truth for PDF extraction.
It serves as an audit trail, not a software development log.

---

## 2025-12-17 – Ground Truth Established

### Completed

- **PDF Extraction**
  - Extracted *FlexQube Årsredovisning 2022* using four independent AI-based pipelines:
    - DeepSeek-ocr2: 213,761 characters (most compact output)
    - LlamaIndex: 204,704 characters
    - Hunyuan: 196,419 characters (highest noise level)
    - Docling: 222,246 characters (medium verbosity)

- **Baseline Selection & Statistical Analysis** (`model_analysis.ipynb`)
  - Computed pairwise similarity matrix across all four model outputs
  - LlamaIndex achieved highest overall consensus (58.4%)
  - Docling showed lowest consensus (38.7%), indicating more unique structure
  - LlamaIndex selected as baseline for ground truth construction

- **LLM-Assisted Difference Analysis** (`llm_analysis_llamaindex.py`)
  - Compared all four model outputs against the baseline
  - Claude Sonnet 4 API used strictly for difference detection and reasoning
  - LLM identified 9 potential correction candidates

- **Manual Double Verification**
  - All 9 suggested corrections were manually verified against the original PDF
  - Second review performed to confirm decisions
  - Result:
    - 1 correction verified and approved
    - 8 corrections rejected (baseline confirmed correct)

- **Ground Truth Creation**
  - Base: LlamaIndex output (204,704 characters)
  - Applied: 1 manually verified correction
  - Output finalized and locked for evaluation and benchmarking

---

### Scripts Developed

- `llm_analysis_llamaindex.py` – LLM-based difference detection
- `model_analysis.ipynb` – Baseline selection and statistical comparison

---

### Key Findings

- LlamaIndex was the most suitable baseline due to highest cross-model consensus
- LLM-assisted analysis significantly reduced manual comparison effort
- Manual verification was critical: only 1 of 9 LLM suggestions was correct
- Hybrid workflow (statistics + LLM + manual verification) proved robust and efficient

---

### Metrics

- Total models compared: 4
- LLM suggestions generated: 9
- Manual verifications performed: 9
- Corrections applied: 1
- Verified correction rate: ~11%
- Estimated time saved vs full manual comparison: ~70%

---

### Process Workflow

1. PDF extraction using four independent models (30–60 min)
2. Statistical analysis for baseline selection (10 min)
3. LLM-assisted difference detection (5–10 min)
4. Manual double verification against original PDF (30–60 min)
5. Apply verified correction and finalize ground truth (5 min)

**Total elapsed time:** ~2–3 hours  
**Result:** Verified ground truth ready for benchmarking and model evaluation

---

## Future Work

- [ ] Evaluate additional PDF extraction models
- [ ] Extend methodology to multiple documents
- [ ] Investigate OCR confidence–based verification support
- [ ] Compare against fully human-annotated ground truth
- [ ] Publish methodology and results

---

**Status:** Complete – Ground truth established and verified  
**Models Used:** DeepSeek-ocr-2, LlamaIndex, Docling, Hunyuan  
**Ground Truth Base:** LlamaIndex + 1 verified manual correction
