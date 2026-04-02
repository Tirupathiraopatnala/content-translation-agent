# Content Translation Agent

Translate text in PDFs and images to multiple Indian languages while preserving all images, illustrations, and layout.

**Supported inputs:** Digital PDFs, scanned PDFs, images (PNG/JPG/TIFF/BMP)  
**Supported languages:** Hindi, Tamil, Bengali, Punjabi, Gujarati

## How It Works

```
Input (PDF/image) → Page Images → OCR → Translate → Inpaint (remove text) → Overlay (render translation) → Output
```

The system processes each page as an image through 4 stages:
1. **OCR** — Extract text with bounding box positions
2. **Translate** — Translate extracted text to target language
3. **Inpaint** — Remove original text from image while preserving background
4. **Overlay** — Render translated text at original positions with Indic fonts

## Project Structure

```
notebooks/
  01_input_loading.ipynb          # Load PDF/image → page images
  02_ocr_comparison.ipynb         # Compare: Tesseract, EasyOCR, Google Vision, Azure Vision
  03_translation_comparison.ipynb # Compare: Claude, Google Translate, NLLB, IndicTrans2
  04_inpainting_comparison.ipynb  # Compare: OpenCV TELEA/NS, LaMa, simple fill
  05_text_overlay.ipynb           # Font rendering + text fitting
  06_full_pipeline.ipynb          # End-to-end pipeline with best choices
data/                             # Intermediate outputs shared between notebooks
src/utils.py                      # Shared utility functions
fonts/                            # Noto Sans Indic fonts (downloaded at setup)
scripts/download_fonts.py         # Font download script
```

## Setup

```bash
# Install Python dependencies
pip install pdf2image Pillow opencv-python-headless numpy matplotlib \
    pytesseract easyocr anthropic tqdm pydantic jupyter

# Install system dependencies
sudo apt-get install -y poppler-utils tesseract-ocr

# Download Indic fonts
python scripts/download_fonts.py

# Optional: for cloud APIs
pip install google-cloud-vision google-cloud-translate azure-ai-vision-imageanalysis

# Optional: for local translation models
pip install transformers torch sentencepiece
```

## Usage

### Experimentation (Notebooks)

Run notebooks sequentially — each saves outputs to `data/` for the next:

1. `01_input_loading.ipynb` — Set your input file path, run to convert to images
2. `02_ocr_comparison.ipynb` — Compare OCR engines, pick the best
3. `03_translation_comparison.ipynb` — Compare translators, pick the best
4. `04_inpainting_comparison.ipynb` — Compare inpainting methods, pick the best
5. `05_text_overlay.ipynb` — Test font rendering and text fitting
6. `06_full_pipeline.ipynb` — Run end-to-end with your best choices

### Quick Start (Full Pipeline)

Open `06_full_pipeline.ipynb`, configure:
```python
INPUT_FILE = "samples/your_file.pdf"
TARGET_LANGUAGES = ["hindi", "tamil"]
OCR_ENGINE = "easyocr"
TRANSLATOR_ENGINE = "claude"
INPAINTING_METHOD = "opencv_telea"
```
Run all cells. Output saved to `data/output/pipeline/`.

## Environment Variables

| Variable | Required For |
|---|---|
| `ANTHROPIC_API_KEY` | Claude translation |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Vision / Translate |
| `AZURE_VISION_ENDPOINT` + `AZURE_VISION_KEY` | Azure AI Vision |
