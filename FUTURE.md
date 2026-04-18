
# FUTURE WORK

This document outlines potential improvements and extensions for the OCR project that are currently out of scope but important for scalability, maintainability, and production readiness.

---

## 1. Unified OCR Model Interface

Currently, OCR models are handled with model-specific input/output logic, primarily within notebooks. This leads to duplicated code, inconsistent behavior, and makes the system difficult to scale and maintain.

A unified abstraction layer should be introduced to standardize how all OCR models are used:

```python
from abc import ABC, abstractmethod
from PIL import Image


class OCRModel(ABC):
    """Common interface for all OCR models."""

    @abstractmethod
    def process_page(self, image: Image.Image) -> str:
        """Run OCR on a single image and return extracted text."""
        ...

    @abstractmethod
    def process_pdf(self, path: str) -> dict:
        """Process a full PDF and return structured output."""
        ...

    def save_output(self, result: dict, path: str) -> None:
        """Save OCR output to disk (JSON)."""
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
```

All OCR models (e.g., Tesseract, EasyOCR, Surya) should implement this interface. Any model-specific behavior (e.g., preprocessing, padding, or formatting quirks) should be encapsulated within the implementation and not exposed to the rest of the system.

This abstraction enables:

- A consistent API across all models
- Easier model comparison and benchmarking
- Cleaner integration into pipelines and downstream systems
This also enables building a consistent OCR pipeline where preprocessing, inference, and postprocessing are clearly separated.
  
## Standardized Preprocessing and Postprocessing

Some models previously required custom preprocessing or postprocessing steps. While most of this has been removed, inconsistencies may still exist.

Future improvements:

- Define a shared preprocessing pipeline (e.g., resizing, normalization)
- Avoid model-specific logic inside notebooks
  
---
## 2. Transition from Notebooks to Modular Code

Notebooks were useful for experimentation, but they are not ideal for maintainable systems.

Future improvements:

- Move core logic into reusable Python modules
- Keep notebooks only for experimentation and visualization
- Improve testability and reproducibility

## 3. Automated Model Retrieval and Component-Based Model Selection

A key future improvement is to automate the handling, evaluation, and selection of multiple OCR models instead of manually testing them in notebooks.

Proposed direction:

- Automatically retrieve OCR models from Hugging Face
- Standardize loading and inference via the `OCRModel` interface
- Evaluate all models using a shared benchmarking pipeline

Beyond global evaluation, the system should support **component-based evaluation**, where model performance is measured on specific document elements, such as:

- Headings
- Paragraphs
- Tables
- Handwritten text

Goal:

- Identify the best-performing model for each component type
- Create a mapping between component → optimal model

Example:

```json
{
  "table": "model_a",
  "handwritten": "model_b",
  "paragraph": "model_c"
}
