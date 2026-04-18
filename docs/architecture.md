# Architecture
OCR Benchmark Framework for Document-to-Markdown Conversion

## 1. System Overview

The OCR Benchmark Framework is a multi-layer framework for evaluating and reconstructing
complex PDF documents using multiple OCR engines and a hybrid reasoning layer.

The system consists of five layers:

1. Model Inference Layer
2. Structuring Layer
3. Evaluation Layer
4. Diversity Analysis Layer
5. Hybrid Reasoning Layer

## 2. High-Level Pipeline
```
PDF
↓
Multiple OCR Models
↓
Markdown Outputs
↓
Metric Evaluation + Diversity Analysis
↓
Page-Level JSON Structuring
↓
Hybrid Arbitration (LLM)
↓
Validated Markdown Output
```

## 3. Layer Descriptions

### 3.1 Model Inference Layer
Each OCR model is executed independently using standardized pipelines.
Outputs are normalized to Markdown format.

### 3.2 Structuring Layer
Markdown outputs are converted into page-level structured JSON:
- page_id
- text_blocks
- confidence (if available)

### 3.3 Evaluation Layer
Each model output is compared against ground truth using:
- Text similarity metrics
- Structural similarity metrics
- Layout preservation measures

### 3.4 Diversity Analysis Layer
Cross-model error behavior is analyzed using:
- Error correlation matrices
- Component segmentation
- Similarity analysis
- Error profile clustering

### 3.5 Hybrid Reasoning Layer
An LLM-based arbitration engine compares model outputs page-by-page
and reconstructs the most structurally valid Markdown representation.

## 4. Design Principles

- Deterministic processing where possible
- Page-level modular reasoning
- Structural validity prioritization
- Reproducibility
- Model-agnostic architecture
