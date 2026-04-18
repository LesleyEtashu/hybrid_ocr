import re
import os
import asyncio
import json
import unicodedata
from typing import List, Dict, Optional
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-4.1"
TEMPERATURE = 0.0  

MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", 5))  # Max parallel API calls
DATASETS_DIR = Path("datasets")


MODEL_FILES = {
    "chandra": DATASETS_DIR / "chandra" / "chandra_output_document.json",
    "llamaindex": DATASETS_DIR / "llamaindex_c" / "llamaindex_output_c_document.json",
    "hunyuan": DATASETS_DIR / "hunyuan" / "hunyuan_output_document.json",
}

_page_cache: Dict[str, Dict[int, str]] = {}  # In-memory cache: model → {page_num → content}
_model_meta: Dict[str, Dict] = {}            # Per-model metadata (e.g. document_name)

OUTPUT_DIR = Path("datasets/fused")

SYSTEM_PROMPT = """
You are a deterministic document reconstruction system designed to resolve OCR conflicts and produce structurally valid Markdown.

Merge three OCR-derived Markdown representations of the SAME PAGE into one final,
structurally correct, semantically coherent, and technically accurate Markdown page.

INPUT

You will receive a JSON object containing the OCR outputs of three models for the same page.

Input format:
{
  "page_number": int,
  "model_a": "...",
  "model_b": "...",
  "model_c": "..."
}

Strict rules:
- Output ONLY the final reconstructed Markdown page.
- No comments. No metadata. No JSON. No explanations.
- Do not correct grammar, spelling, or wording unless necessary to produce valid Markdown syntax.

SOURCE MODELS

Model A (chandra): strongest for header hierarchy and table structure.
Model B (llamaindex): primary semantic reference for prose and standalone numeric content.
Model C (hunyuan): strongest for graph interpretation.

ROBUSTNESS RULES

- Do not introduce any words, numbers, or symbols that do not exist in at least one source model.
- Prefer copying exact text spans from source models. Do not paraphrase or rewrite text.
- Ignore any model output that is empty or whitespace-only.
- Never merge partial tokens across models. Do not create hybrid words from multiple sources.
- Remove exact or near-exact duplicate lines while preserving original order.
- Prefer longer contiguous text spans that appear verbatim in a single source model.
- Tables that contain long sentences, multiple dates, or narrative event descriptions
  must be converted into sectioned lists instead of Markdown tables.
- Quarterly or time-based data (Q1, Q2, months, etc.)
  must be rendered as Markdown sections (### Q1, ### Q2, etc.)
  with bullet lists instead of table cells.

INCLUSION POLICY

Precision takes priority over completeness. These rules override any completeness bias.

- If a section exists in multiple models, prefer consensus unless one model provides more complete or structurally valid content.
- If a section exists in only one model, include it ONLY if it forms a structurally valid Markdown block and does not conflict with higher-priority models.
- Exclude content that contains obvious OCR corruption such as broken tokens, repeated characters, isolated characters, or unreadable fragments.
- Do not omit sections that pass the above criteria.
- Do not add content just to increase length or coverage.
- Do not prefer longer outputs over shorter ones; more text often means more OCR noise.

ARBITRATION LOGIC

The following defaults apply unless OVERRIDE RULES apply.

1. Structural Backbone
- Use Model B as the structural backbone if it contains content.
- If Model B is empty, use Model A as backbone.
- Preserve the section order as it appears in the backbone model. Do not reorder sections.

2. Headers
- Prefer Model A header formatting only when it aligns with the backbone structure.

3. Tables
- Select the most complete table from a single source model, preferring Model A. Do not merge rows or columns across models.
- Use Model B to detect the presence and boundaries of tables.
- Always prefer the most complete and structurally valid table.

4. Numerical Data
- Prefer Model B for numeric values.
- If values differ across models, select the value exactly as it appears in a single source model, prioritizing Model B, then Model A, then Model C. Do not modify or infer numeric values.

5. Graphs and Diagrams
- Only use Model C if it contains clear textual labels or values not present in other models.

6. Text-Level Conflicts
- Prefer Model B for prose clarity.

7. Tie-breaking
- When multiple valid candidates exist, select the one that appears earliest in the backbone model.

8. Temporal Structure Detection
   - Detect chronological markers (months, quarters, dates).
   - Group them into sections using headers (e.g., ### Q1).

OVERRIDE RULES

- If one model provides more complete, structured, or internally consistent content, prefer it over majority agreement. A single model may be correct even if the others agree.

FINAL VALIDATION

Ensure:
- Valid Markdown header hierarchy
- No broken or incomplete tables
- No duplicated lines or OCR artifacts
- No orphan list markers
- No incomplete Markdown structures
- If a structure is partially broken, prefer selecting a valid version from another model rather than omitting it entirely.
- Only omit when no valid version exists in any model.

Output ONLY the reconstructed Markdown page.
"""


def normalize_markdown(md: str) -> str:
    # Normalizes unicode, line endings, and excessive blank lines
    md = unicodedata.normalize("NFKC", md)
    md = md.replace("\r\n", "\n")
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def clean_artifacts(md: str) -> str:
    # Removes isolated page numbers and non-printable control characters
    md = re.sub(r'(?m)^\s*\d{1,3}\s*$', '', md)
    md = re.sub(r'[\x00-\x08\x0B-\x1F\x7F]', '', md)
    return md.strip()


def similarity(a: str, b: str) -> float:
    # Word-level Jaccard similarity — used for confidence scoring
    tokens_a = set(re.findall(r'\w+', a.lower()))
    tokens_b = set(re.findall(r'\w+', b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def valid_header_hierarchy(md: str) -> bool:
    # Checks that headers never skip more than one level (e.g. h1→h3 is invalid)
    headers = re.findall(r'^(#{1,6})\s+\S', md, flags=re.MULTILINE)
    levels = [len(h) for h in headers]
    for i in range(1, len(levels)):
        if levels[i] - levels[i - 1] > 1:
            return False
    return True


def valid_markdown_tables(md: str) -> bool:
    # Validates that all markdown tables have consistent column counts
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "|" in line:
            if i + 1 >= len(lines):
                i += 1
                continue
            header_line = lines[i].strip()
            separator_line = lines[i + 1].strip()
            separator_pattern = r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$'
            if not re.match(separator_pattern, separator_line):
                i += 1
                continue
            header_cols = [c.strip() for c in header_line.strip("|").split("|")]
            col_count = len(header_cols)
            separator_cols = [c.strip() for c in separator_line.strip("|").split("|")]
            if len(separator_cols) != col_count:
                return False
            i += 2
            while i < len(lines) and "|" in lines[i]:
                row_cols = [c.strip() for c in lines[i].strip("|").split("|")]
                if len(row_cols) != col_count:
                    return False
                i += 1
            continue
        i += 1
    return True


def contains_table(md: str) -> bool:
    return bool(re.search(r"\|.*\|", md))

def discover_pages() -> List[int]:
    """Returns sorted list of page numbers available across all model files."""
    pages = set()
    for model_name, filepath in MODEL_FILES.items():
        if not filepath.exists():
            logger.warning(f"Missing file for model '{model_name}': {filepath}")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        _model_meta[model_name] = {"document_name": data.get("document_name", "")}
        for page in data.get("pages", []):
            pages.add(page["page_number"])
    return sorted(pages)
 
 
def load_page_content(model_name: str, page_num: int) -> Optional[str]:
    """Returns markdown content for a specific page from a model's JSON file."""
    if model_name not in _page_cache:
        filepath = MODEL_FILES[model_name]
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        _page_cache[model_name] = {p["page_number"]: p.get("content", "") for p in data.get("pages", [])}
    return _page_cache[model_name].get(page_num)

# Arbitration engine
class AsyncArbitrationEngine:
    """Sends a page to the LLM and returns fused Markdown. Retries with exponential backoff."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

    async def run(self, payload: Dict, retries: int = 3, backoff: float = 2.0) -> str:
        last_exc = None
        for attempt in range(retries):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=MODEL_NAME,
                        temperature=TEMPERATURE,
                        max_tokens=4000,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": json.dumps(payload)}
                        ]
                    ),
                    timeout=60
                )
                content = response.choices[0].message.content.strip()
                if not content:
                    raise ValueError("Empty LLM response")
                return content
            except Exception as e:
                last_exc = e
                wait = backoff ** attempt
                logger.warning(f"API call failed (attempt {attempt + 1}/{retries}): {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
        raise last_exc


class AsyncMarkdownFusionPipeline:
    """Main pipeline: loads pages from three models, fuses them, and writes output."""

    def __init__(self, api_key: str):
        self.arbitrator = AsyncArbitrationEngine(api_key)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENCY)  # Throttles concurrent API calls

    async def run_with_limit(self, payload: Dict) -> str:
        async with self.semaphore:
            return await self.arbitrator.run(payload)

    async def process_single_page(self, page_num: int) -> Dict:
        """
        Fuses a single page:
        - Otherwise: send to LLM for arbitration
        -  Fallback: pick longest source if LLM fails or produces invalid Markdown
        -  Compute confidence via pairwise Jaccard between source models
        """
        model_a = load_page_content("chandra", page_num)
        model_b = load_page_content("llamaindex", page_num)
        model_c = load_page_content("hunyuan", page_num)

        available = [m for m in [model_a, model_b, model_c] if m]
        if not available:
            return {"page": page_num, "content": "", "confidence": 0.0, "dominant_source": None}

         # Only skip LLM if ALL models are very similar
        def all_similar(a, b, c, threshold=0.9):
            return (
            a and b and c and
            similarity(a, b) > threshold and
            similarity(a, c) > threshold and
            similarity(b, c) > threshold
            )
        # Fast-path: skip LLM call if a source already has a structurally valid table
        skip_llm = False
        fused = None
        for source_name, candidate in [("llamaindex", model_b), ("chandra", model_a)]:
            if (
            candidate
            and contains_table(candidate)
            and valid_markdown_tables(candidate)
            and all_similar(model_a, model_b, model_c)):
                fused = clean_artifacts(candidate)
                skip_llm = True
                logger.info(f"Page {page_num}: skipping LLM, using valid table from '{source_name}'")
                break

        payload = {
            "page_number": page_num,
            "model_a": model_a or "",
            "model_b": model_b or "",
            "model_c": model_c or ""
        }

        if not skip_llm:
            try:
                fused = await self.run_with_limit(payload)
                fused = clean_artifacts(fused)
                # Post-LLM validation — fall back to longest source if structure is broken
                if not valid_header_hierarchy(fused) or not valid_markdown_tables(fused):
                    logger.warning(f"Page {page_num}: invalid markdown from LLM → fallback")
                    fused = clean_artifacts(max(available, key=len))
            except Exception as e:
                logger.error(f"Page {page_num}: LLM arbitration failed, fallback to longest source. {e}")
                fused = clean_artifacts(max(available, key=len))

        # Determine which source model the fused result resembles most
        similarity_scores = {
            "chandra": similarity(fused, model_a) if model_a else 0.0,
            "llamaindex": similarity(fused, model_b) if model_b else 0.0,
            "hunyuan": similarity(fused, model_c) if model_c else 0.0,
        }
        dominant_source = max(similarity_scores, key=similarity_scores.get)

        # Confidence = mean pairwise Jaccard between source models 
        pairwise = []
        if model_a and model_b: pairwise.append(similarity(model_a, model_b))
        if model_a and model_c: pairwise.append(similarity(model_a, model_c))
        if model_b and model_c: pairwise.append(similarity(model_b, model_c))
        confidence = sum(pairwise) / len(pairwise) if pairwise else 0.0

        return {
            "page_number": page_num,
            "content": fused,
            "confidence": round(confidence, 4),
            "dominant_source": dominant_source
        }

    async def process(self) -> Dict:
        """Runs the full pipeline: all pages in parallel, writes JSON + Markdown."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        pages = discover_pages()
        logger.info(f"Discovered {len(pages)} pages. Starting fusion...")

        tasks = [self.process_single_page(page) for page in pages]
        fused_pages = await asyncio.gather(*tasks)  # Process all pages concurrently

        # Aggregate confidence score across the entire document
        confidences = [p["confidence"] for p in fused_pages if p["confidence"] > 0]
        overall_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

        document_name = next(
            (m["document_name"] for m in _model_meta.values() if m.get("document_name")), ""
        )

        final_json = {
            "document_name": document_name,
            "source_models": list(MODEL_FILES.keys()),
            "total_pages": len(pages),
            "overall_confidence": overall_confidence,
            "pages": fused_pages
        }

        # Save structured JSON output
        output_file = OUTPUT_DIR / "fused_document.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        logger.info(f"Fusion complete → {output_file} (overall confidence: {overall_confidence})")

        # Save markdown 
        md_file = OUTPUT_DIR / "fused_document.md"
        with open(md_file, "w", encoding="utf-8") as f:
            for page in fused_pages:
                if page["content"]:
                    f.write(f"---\n# Page {page['page_number']}\n")
                    f.write(page["content"])
                    f.write("\n\n")
        logger.info(f"Markdown export → {md_file}")

        return final_json


async def main():
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY missing from .env")
    pipeline = AsyncMarkdownFusionPipeline(OPENROUTER_API_KEY)
    await pipeline.process()


if __name__ == "__main__":
    asyncio.run(main())
