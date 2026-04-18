# Models Evaluated

Full reference for all 27 OCR models benchmarked in this project. Models are listed in order of benchmark performance (CER ascending).

| Model | Type | Notes |
|---|---|---|
| llamaindex | API | LlamaIndex-native pipeline; top performer across all three metrics |
| chandra | Open source | Strong character-level accuracy; low similarity score suggests structural issues |
| hunyuan | Open source | Tencent multimodal model; solid CER with good similarity retention |
| docling | Open source | IBM layout-aware parser; struggles with complex table structures |
| deepseek_ocr2 | Open source | Second-generation DeepSeek OCR; improved over v1, good similarity score |
| deepseek_ocr | Open source | First-generation DeepSeek OCR; lower similarity despite moderate CER |
| lightonocr | Open source | Lightweight API model; balanced CER/WER with moderate similarity |
| sonnet4 | API | Claude Sonnet 4; general-purpose LLM used for extraction, not purpose-built OCR |
| trocr | Open source | Microsoft Transformer-based OCR; strong on printed text, weaker on layout |
| latex | Open source | LaTeX-oriented extraction pipeline; poor on non-LaTeX documents |
| mistral | API | Base Mistral model; significantly weaker than mistralLarge3 on this benchmark |
| qwen25 | Open source | Alibaba Qwen 2.5; high error rate and very low similarity |
| easyocr | Open source | Lightweight multilingual OCR; broad language support but low accuracy here |
| llamaparse | API | LlamaIndex PDF parser (not to be confused with the llamaindex pipeline) |
| gemini2.5 | API | Google Gemini 2.5; surprisingly poor on structured document extraction |
| pdfplumber | Open source | Text-layer extraction only; identical WER to gemini2.5, no visual understanding |
| haiku | API | Claude Haiku; fast and cheap but not competitive for OCR quality |
| nemotron_ocr | Open source | NVIDIA Nemotron; very high WER, near-zero similarity |
| paddle_ocr | Open source | Baidu PaddleOCR; strong multilingual support but low accuracy on this dataset |
| doctr | Open source | Mindee docTR; Transformer-based, poor results on complex layouts |
| tesseract | Open source | Classic open-source OCR; well-established baseline, outperformed by most modern models |
| florence2 | Open source | Microsoft Florence 2; near-zero similarity, not suited for document OCR |
| surya | Open source | Layout-aware open-source model; poor accuracy on this benchmark |
| GLM_ocr | Open source | Zhipu GLM; high error rate, moderate similarity |
| Qianfan_ocr | Open source | Baidu Qianfan; very high CER and near-zero similarity |
| landingai | API | LandingAI; CER exceeds 700% due to severe hallucination — generative drift rather than extraction failure |
