# MILITARY ANOMALY SCANNER - DEPLOYMENT SUMMARY

## System Status: ✅ DEPLOYED

**Location:** `C:\Users\natha\Desktop\MILITARY_ANOMALY_SCANNER`

## Components Installed

### Core System
- `main.py` - Main scanner orchestrator (9.1 KB)
- `core/scraper.py` - Web scraper for HiRISE PDS (7.1 KB)
- `core/ollama_scanner.py` - Ollama LLM integration (10.7 KB)
- `core/image_processor.py` - Image analysis & enhancement (9.2 KB)
- `core/__init__.py` - Military logger (1.0 KB)

### Utilities
- `model_manager.py` - Ollama model management (4.7 KB)
- `analyze_local.py` - Local image analysis (3.5 KB)
- `quick_analyze.py` - Single image analysis (2.6 KB)
- `test_system.py` - System verification (3.6 KB)
- `utils/helpers.py` - Utility functions (2.9 KB)

### Launchers
- `launch.bat` - Interactive Windows launcher (1.7 KB)
- `install.bat` - Dependency installer (0.9 KB)

### Configuration
- `config/settings.json` - System configuration (1.2 KB)
- `requirements.txt` - Python dependencies (0.3 KB)

### Documentation
- `README.md` - Full documentation (3.6 KB)
- `README.py` - Python documentation (6.5 KB)

## Directory Structure

```
MILITARY_ANOMALY_SCANNER/
├── config/
│   └── settings.json
├── core/
│   ├── __init__.py
│   ├── scraper.py
│   ├── ollama_scanner.py
│   └── image_processor.py
├── data/
│   ├── images/
│   ├── processed/
│   └── reports/
├── logs/
├── models/
├── utils/
│   └── helpers.py
├── main.py
├── launch.bat
├── install.bat
├── analyze_local.py
├── model_manager.py
├── quick_analyze.py
├── test_system.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### Step 1: Install Python Dependencies
```batch
cd C:\Users\natha\Desktop\MILITARY_ANOMALY_SCANNER
install.bat
```

### Step 2: Install Ollama
1. Download: https://ollama.ai
2. Install and run

### Step 3: Pull Required Models
```bash
ollama pull llava
ollama pull llama2
```

### Step 4: Start Ollama
```bash
ollama serve
```

### Step 5: Run Scanner
```batch
launch.bat
```

## Scan Modes

1. **Full Scan** - 50 pages, 200 images
2. **Quick Scan** - 10 pages, 50 images
3. **Custom Scan** - User-defined parameters
4. **Local Analysis** - Analyze existing images

## Command Line Usage

```bash
# Full scan
python main.py --pages 50 --images 200

# Quick scan
python main.py --pages 10 --images 50

# Custom scan
python main.py --pages 25 --images 100

# Analyze local images
python analyze_local.py --input /path/to/images

# Quick single image analysis
python quick_analyze.py image.jpg

# Model management
python model_manager.py
```

## Anomaly Categories

1. Structural Anomalies
2. Artificial Constructs
3. Potential Craft/Vehicles
4. Biological Signatures
5. Water/Ice Deposits
6. Geological Anomalies
7. Geometric Patterns
8. Shadow Anomalies
9. Surface Discontinuities
10. Thermal Anomalies

## Threat Levels

- NONE → No anomaly detected
- LOW → Minor, likely natural
- MEDIUM → Notable, requires review
- HIGH → Significant, potential concern
- CRITICAL → Major, immediate attention

## Output Location

- **Reports:** `data/reports/`
- **Enhanced Images:** `data/processed/`
- **Logs:** `logs/`

## Requirements

- Python 3.8+
- Ollama (running locally)
- 8GB+ RAM recommended
- GPU recommended for faster analysis

## Classification

**TOP SECRET//SCI**

For authorized use only.
