#!/usr/bin/env python3
"""
MILITARY ANOMALY SCANNER
Automated Reconnaissance and Anomaly Detection System
Classification: TOP SECRET//SCI

OVERVIEW:
This system performs automated reconnaissance on the HiRISE PDS database,
downloading and analyzing images for anomalies using local Ollama LLM models.

CAPABILITIES:
- Web scraping and image acquisition
- Image preprocessing and enhancement
- AI-powered anomaly detection using Ollama
- Geometric pattern detection
- Threat level assessment
- Automated report generation

REQUIREMENTS:
- Python 3.8+
- Ollama running locally (http://localhost:11434)
- Required models: llava, llama2, mistral

INSTALLATION:
1. Install Python dependencies:
   pip install -r requirements.txt

2. Install Ollama:
   https://ollama.ai

3. Pull required models:
   ollama pull llava
   ollama pull llama2
   ollama pull mistral

4. Run model manager:
   python model_manager.py

QUICK START:
- Run launch.bat (Windows) for interactive menu
- Or use command line:
  python main.py --pages 10 --images 50

SCAN MODES:
- Full Scan: 50 pages, 200 images
- Quick Scan: 10 pages, 50 images
- Custom Scan: User-defined parameters
- Local Analysis: Analyze existing images

ANOMALY CATEGORIES:
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

THREAT LEVELS:
- NONE: No anomaly detected
- LOW: Minor anomaly, likely natural
- MEDIUM: Notable anomaly, requires review
- HIGH: Significant anomaly, potential concern
- CRITICAL: Major anomaly, immediate attention

OUTPUT:
- JSON detailed report: data/reports/report_*.json
- Executive summary: data/reports/executive_summary_*.txt
- Enhanced images: data/processed/
- Annotated images: data/processed/annotated_*
- Logs: logs/

DIRECTORY STRUCTURE:
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
├── analyze_local.py
├── model_manager.py
└── requirements.txt

CLASSIFICATION: TOP SECRET//SCI
"""

import sys
from pathlib import Path

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      ███╗   ███╗██╗███╗   ██╗██████╗ ███████╗██████╗         ║
║      ████╗ ████║██║████╗  ██║██╔══██╗██╔════╝██╔══██╗        ║
║      ██╔████╔██║██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝        ║
║      ██║╚██╔╝██║██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗        ║
║      ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝███████╗██║  ██║        ║
║      ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝        ║
║                                                               ║
║      ███████╗ █████╗  ██████╗ ██╗   ██╗████████╗             ║
║      ██╔════╝██╔══██╗██╔════╝ ██║   ██║╚══██╔══╝             ║
║      ███████╗███████║██║  ███╗██║   ██║   ██║                ║
║      ╚════██║██╔══██║██║   ██║██║   ██║   ██║                ║
║      ███████║██║  ██║╚██████╔╝╚██████╔╝   ██║                ║
║      ╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝                ║
║                                                               ║
║      ANOMALY DETECTION SYSTEM - LOCAL LLM POWERED            ║
║      Classification: TOP SECRET//SCI                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_dependencies():
    missing = []
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing.append("beautifulsoup4")
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    if missing:
        print(f"\n[ERROR] Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_ollama():
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
        print(f"[OK] Ollama connected ({len(models)} models available)")
        return True
    except:
        print("[ERROR] Ollama not running")
        print("Start with: ollama serve")
        return False

if __name__ == "__main__":
    print_banner()
    
    print("\n[System Check]")
    
    if not check_dependencies():
        sys.exit(1)
    print("[OK] Python dependencies")
    
    if not check_ollama():
        print("\nWould you like to continue anyway? (y/n): ")
        if input().lower() != 'y':
            sys.exit(1)
    
    print("\n" + "="*60)
    print("System ready. Use launch.bat or main.py to start scanning.")
    print("="*60)
