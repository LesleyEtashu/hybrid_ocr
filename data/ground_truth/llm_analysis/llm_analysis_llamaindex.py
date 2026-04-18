"""
LLM analysis with LlamaIndex as baseline
Compares the other 3 models against LlamaIndex
Run: python run_llm_analysis_llamaindex_baseline.py
"""

import json
import os
import sys
from pathlib import Path
from anthropic import Anthropic

def main():
    print("=" * 70)
    print(" LLM-BASED GROUND TRUTH ANALYSIS")
    print(" BASELINE: LlamaIndex")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print(" ERROR: ANTHROPIC_API_KEY not set!")
        print("\nSet it with:")
        print('   PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-api03-..."')
        print('   Bash: export ANTHROPIC_API_KEY="sk-ant-api03-..."')
        sys.exit(1)
    
    print("API key found")
    
    # Load all files
    current_dir = Path(".")
    
    files = {
        "LlamaIndex": current_dir / "llamaindex_output_c.md",
        "Docling": current_dir / "docling_output.md",
        "DeepSeekOCR2": current_dir / "deepseekocr2_output.md",
        "Hunyuan": current_dir / "hunyuan_output.md",
    }
    
    texts = {}
    for name, path in files.items():
        if path.exists():
            texts[name] = path.read_text(encoding='utf-8')
            print(f" {name}: {len(texts[name]):,} characters")
        else:
            print(f"Missing: {path}")
            sys.exit(1)
    
    print(f"\n All 4 files loaded")
    
    # Select LlamaIndex as baseline
    baseline_name = "LlamaIndex"
    baseline_text = texts[baseline_name]
    
    print(f" Using {baseline_name} as baseline\n")
    
    # Build prompt for LLM
    print(" Building prompt for Claude API...")
    
    prompt = f"""You are an expert at analyzing PDF extractions and creating ground truth.

I have run the same PDF (FlexQube Annual Report 2022) through 4 different AI models and got slightly different results.

LlamaIndex is used as baseline.

Your task is to analyze the differences and suggest corrections to the baseline.

## MODEL OUTPUTS:

### LlamaIndex (Baseline):
{baseline_text[:20000]}

### Docling:
{texts['Docling'][:20000]}

### DeepSeekOCR2:
{texts['DeepSeekOCR2'][:20000]}

### Hunyuan:
{texts['Hunyuan'][:20000]}

## TASK:

Analyze the differences between models and create a list of correction suggestions for the baseline (LlamaIndex).

For each difference:
1. Identify exactly what differs
2. Analyze which version is most likely correct
3. If multiple models have the same version that differs from baseline, consider if baseline should be corrected
4. Focus on:
   - **Numbers and key figures** (e.g., MSEK, percentages) - these must be exact
   - **Technical terms** (e.g., AGV, AMR, eQart) - spelling is important
   - **OCR errors** (e.g., 0/O, 1/l, 5/S)
   - **Swedish characters** (å, ä, ö)
   - **Spacing and formatting**

## OUTPUT FORMAT (JSON):

{{
  "corrections": [
    {{
      "location": "Section/paragraph description",
      "baseline": "Text from LlamaIndex baseline",
      "suggested": "Suggested correct version",
      "supporting_models": ["Docling", "DeepSeekOCR2"],
      "reasoning": "Why this correction is suggested (e.g., '3 of 4 models have this version')",
      "confidence": 0.95,
      "needs_manual_review": false
    }}
  ],
  "summary": "Overall summary of the analysis and recommendations"
}}

## IMPORTANT:

- Suggest ONLY corrections where you are fairly confident (confidence ≥ 0.5)
- If baseline appears correct despite differences, do NOT include a correction
- Use "needs_manual_review": true for uncertain cases
- If 3 of 4 models have the same version, it's a strong indication of what is correct
- Be especially careful with:
  - Rounding of numbers (e.g., -22.0 vs -21.964)
  - Minor formatting differences that don't affect content

Return ONLY JSON, no other text."""

    # Call Claude API
    print("Calling Claude API (this takes a few minutes)...\n")
    
    try:
        client = Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON
        if response_text.strip().startswith('```'):
            lines = response_text.strip().split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        result = json.loads(response_text)
        
        # Save results
        output_file = Path("ground_truth_suggestions_llamaindex.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Analysis complete! Saved to: {output_file}")
        
        # Show summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        corrections = result.get('corrections', [])
        high_conf = [c for c in corrections if c.get('confidence', 0) >= 0.8]
        low_conf = [c for c in corrections if c.get('confidence', 0) < 0.8]
        needs_review = [c for c in corrections if c.get('needs_manual_review', False)]
        
        print(f"\nTotal corrections: {len(corrections)}")
        print(f"High confidence (≥0.8): {len(high_conf)}")
        print(f"Low confidence (<0.8): {len(low_conf)}")
        print(f"Needs manual review: {len(needs_review)}")
        
        print(f"\nLLM Summary:")
        print(f"   {result.get('summary', 'N/A')}")
        
        # Next steps
        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print(f"""
1. Open {output_file} and review corrections
2. For each correction with needs_manual_review=true:
   - Open the PDF
   - Verify against original
   - Decide whether to accept the suggestion
3. Apply approved corrections to baseline
4. Save as final_ground_truth.md

""")
        
        # Examples
        if corrections:
            print("=" * 70)
            print("EXAMPLES OF CORRECTIONS THAT NEED REVIEW:")
            print("=" * 70)
            
            examples = [c for c in corrections if c.get('needs_manual_review', False) or c.get('confidence', 1) < 0.8]
            
            for i, corr in enumerate(examples[:3], 1):
                print(f"\n#{i}: {corr.get('location', 'Unknown')}")
                baseline_val = corr.get('baseline', '')
                suggested = corr.get('suggested', '')
                print(f"   Baseline:   {baseline_val[:100]}...")
                print(f"   Suggested:  {suggested[:100]}...")
                print(f"   Confidence: {corr.get('confidence', 0):.0%}")
                print(f"   Reasoning:  {corr.get('reasoning', 'N/A')[:100]}...")
        
        print("\n Run complete!\n")
        
    except json.JSONDecodeError as e:
        print(f"\n ERROR: Could not parse JSON from LLM")
        print(f"   {e}")
        print(f"\nRaw response:\n{response_text[:500]}...")
        sys.exit(1)
    except Exception as e:
        print(f"\n ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
