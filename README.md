<p align="center">
  <img src="https://img.shields.io/badge/ANOMALY%20SCANNER-HIRISE%20RECON-ff4d00?style=flat-square&labelColor=0a0e1a" alt="anomaly" />
</p>

# MILITARY ANOMALY SCANNER :: HIRISE RECON

**Automated reconnaissance and anomaly detection system for HiRISE planetary imagery, powered by local Ollama vision-language models.**

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-%3E%3D3.8-ffc430?style=flat-square&logo=python&logoColor=ffc430&labelColor=0a0e1a" alt="python"/>
  <img src="https://img.shields.io/badge/CV-OPENCV%204.8-00E5FF?style=flat-square&logo=opencv&logoColor=00E5FF&labelColor=0a0e1a" alt="opencv"/>
  <img src="https://img.shields.io/badge/LLM-OLLAMA%20LOCAL-3dd5ff?style=flat-square&logo=ollama&logoColor=3dd5ff&labelColor=0a0e1a" alt="ollama"/>
  <img src="https://img.shields.io/badge/CLASSES-10%20ANOMALY-B8FF1E?style=flat-square&labelColor=0a0e1a" alt="classes"/>
  <a href="LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-ff3b3b?style=flat-square&labelColor=0a0e1a" alt="license"/></a>
</p>

<pre>
IDENT ......... SCANNER-01
CLASS ......... PLANETARY RECON / ANOMALY DETECTION
STATUS ........ ONLINE / ACTIVE
TARGET ........ HIRISE MARS SURFACE IMAGERY
PIPELINE ...... SCRAPE → ENHANCE → DETECT → CLASSIFY → REPORT
LINK .......... /military-anomaly-scanner
</pre>

---

## // 01 :: SIGNAL

**Military Anomaly Scanner** is a multi-phase pipeline that scrapes publicly available HiRISE PDS (Planetary Data System) Mars surface imagery, enhances it with classical computer vision, and analyzes it through locally-hosted Ollama vision-language models to detect and classify anomalies.

Every detection is classified by category and threat level, with pre-analysis geometric pattern detection feeding into the LLM prompt for more focused analysis. Results are exported as structured JSON reports with human-readable executive summaries.

---

\n---\n\n## Screenshots\n\n| Preview | Description |\n|---------|-------------|\n| ![screenshot](docs/screenshots/screenshot.png) | Main interface |\n| ![screenshot](docs/screenshots/demo.gif) | Demo |\n\n*Screenshots coming soon — placeholders auto-generated. Replace docs/screenshots/ with real captures.*\n\n## Features

### Multi-phase scan pipeline

1. **Reconnaissance** — BFS web crawler discovers image URLs across HiRISE PDS pages
2. **Image Acquisition** — Multi-threaded bulk download with content-type validation and manifest generation
3. **Image Processing** — CLAHE contrast enhancement, NL-means denoising, Canny edge detection, Hough line/circle detection, and contour-based geometric shape recognition
4. **Anomaly Detection** — Vision-language LLM analysis with geometric pattern hints, classifying findings across 10 anomaly categories
5. **Report Generation** — JSON reports and formatted executive summaries with threat aggregation and recommendations

### Computer vision preprocessing

- LAB色彩空间 CLAHE 自适应对比度增强
- Fast NL-means 颜色去噪
- Canny 边缘检测 + 形态学膨胀/腐蚀
- Hough 直线检测 + 轮廓多边形近似 + Hough 圆检测
- Geometric pattern results are injected into the LLM prompt as pre-analysis hints

### 10-class anomaly classification

| Category | Description |
|---|---|
| Structural Anomalies | Unusual formations, geometric patterns |
| Artificial Constructs | Buildings, roads, infrastructure |
| Potential Craft/Vehicles | Aircraft, ground vehicles |
| Biological Signatures | Vegetation, life indicators |
| Water/Ice Deposits | Liquid water, ice formations |
| Geological Anomalies | Unusual terrain, mineral deposits |
| Geometric Patterns | Straight lines, right angles |
| Shadow Anomalies | Hidden structures |
| Surface Discontinuities | Terrain changes |
| Thermal Anomalies | Hot/cold spots |

### Threat levels

`NONE` · `LOW` · `MEDIUM` · `HIGH` · `CRITICAL`

---

## Quick start

**Requirements:** Python 3.8+ and [Ollama](https://ollama.ai) running locally.

```bash
# Install dependencies
pip install -r requirements.txt

# Pull required models
ollama pull llava
ollama pull llama2

# Start Ollama
ollama serve
```

### Run a scan

```bash
# Full scan — 50 pages, 200 images
python main.py --pages 50 --images 200

# Quick scan — 10 pages, 50 images
python main.py --pages 10 --images 50

# Custom scan
python main.py --pages 25 --images 100
```

### Analyze local images

```bash
# Analyze a folder of images
python analyze_local.py --input /path/to/images

# Quick single-image analysis
python quick_analyze.py image.jpg
```

### Windows launcher

```batch
launch.bat
```

Interactive menu with Full Scan, Quick Scan, Custom Scan, and Local Analysis modes. Auto-starts Ollama if not running.

---

## How it works

```
HiRISE PDS (Web)
       │
       ▼
 WebScraper ──── BFS crawl + image URL extraction
       │
       ▼
 ImageDownloader ──── ThreadPoolExecutor bulk download
       │
       ▼
 ImageProcessor ──── CLAHE + denoise + edge detect + geometric patterns
       │
       ▼
 OllamaAnalyzer ──── llava vision model + geometric hints in prompt
       │
       ▼
 ReportGenerator ──── JSON report + executive summary
```

---

## Project structure

```
MILITARY_ANOMALY_SCANNER/
├── config/
│   └── settings.json          # All configuration
├── core/
│   ├── __init__.py            # MilitaryLogger
│   ├── scraper.py             # WebScraper — crawl + download
│   ├── ollama_scanner.py      # OllamaAnalyzer — LLM vision analysis
│   └── image_processor.py     # ImageProcessor — CV pipeline
├── data/
│   ├── images/                # Downloaded images (runtime)
│   ├── processed/             # Enhanced images (runtime)
│   └── reports/               # JSON + text reports (runtime)
├── logs/                      # Session logs (runtime)
├── utils/
│   ├── __init__.py
│   └── helpers.py             # FileUtils, URLUtils
├── main.py                    # Full pipeline orchestrator
├── analyze_local.py           # Local image analysis entry point
├── quick_analyze.py           # Single-image analysis
├── model_manager.py           # Interactive Ollama model setup
├── test_system.py             # Component smoke tests
├── launch.bat                 # Windows interactive launcher
├── install.bat                # Windows dependency installer
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT
└── README.md
```

---

## Configuration

Edit `config/settings.json`:

```json
{
  "system": {
    "max_threads": 8,
    "retry_attempts": 3,
    "timeout_seconds": 30
  },
  "target": {
    "base_url": "https://hirise-pds.lpl.arizona.edu/",
    "max_pages": 50,
    "max_images": 200,
    "download_delay_ms": 500
  },
  "ollama": {
    "host": "http://localhost:11434",
    "model_vision": "llava:latest",
    "model_text": "llama2:latest",
    "temperature": 0.3,
    "max_tokens": 4096
  },
  "scanning": {
    "confidence_threshold": 0.7,
    "min_image_resolution": [256, 256],
    "analysis_batch_size": 10
  }
}
```

---

## Output

### Reports

| File | Description |
|---|---|
| `data/reports/report_*.json` | Full structured JSON report with all anomalies, threat levels, and metadata |
| `data/reports/executive_summary_*.txt` | Human-readable summary with statistics, threat breakdown, and recommendations |

### Processed images

| Pattern | Description |
|---|---|
| `data/processed/enhanced_*` | CLAHE-enhanced + denoised images |
| `data/processed/edges_*` | Canny edge detection output |
| `data/processed/annotated_*` | Original images with threat-level overlays |

---

## System verification

```bash
python test_system.py
```

Checks Python dependencies, config integrity, core module imports, and Ollama connectivity.

---

## Model management

```bash
python model_manager.py
```

Interactive CLI to list, pull, and set up Ollama models. Recommends `llava` for vision analysis and `llama2` for text.

---

## Requirements

- Python 3.8+
- Ollama running locally (port 11434)
- `llava` model for vision analysis
- `llama2` model for text reasoning
- 8GB+ RAM recommended
- GPU recommended for faster LLM inference

---

## License

[MIT](LICENSE) — PlayNexus
