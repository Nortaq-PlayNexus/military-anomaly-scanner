#!/usr/bin/env python3
"""
Quick Test - Verify system components
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    print("Testing imports...")
    try:
        import requests
        print("[OK] requests")
    except:
        print("[FAIL] requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("[OK] beautifulsoup4")
    except:
        print("[FAIL] beautifulsoup4")
        return False
    
    try:
        import cv2
        print("[OK] opencv-python")
    except:
        print("[FAIL] opencv-python")
        return False
    
    try:
        from PIL import Image
        print("[OK] Pillow")
    except:
        print("[FAIL] Pillow")
        return False
    
    try:
        import numpy
        print("[OK] numpy")
    except:
        print("[FAIL] numpy")
        return False
    
    return True

def test_config():
    print("\nTesting configuration...")
    config_path = Path(__file__).parent / "config" / "settings.json"
    
    if not config_path.exists():
        print("[FAIL] Config file not found")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    required_keys = ['system', 'target', 'ollama', 'scanning']
    for key in required_keys:
        if key in config:
            print(f"[OK] {key} section")
        else:
            print(f"[FAIL] Missing {key} section")
            return False
    
    return True

def test_core_modules():
    print("\nTesting core modules...")
    try:
        from core import MilitaryLogger
        print("[OK] MilitaryLogger")
    except Exception as e:
        print(f"[FAIL] MilitaryLogger: {e}")
        return False
    
    try:
        from core.scraper import WebScraper
        print("[OK] WebScraper")
    except Exception as e:
        print(f"[FAIL] WebScraper: {e}")
        return False
    
    try:
        from core.ollama_scanner import OllamaAnalyzer
        print("[OK] OllamaAnalyzer")
    except Exception as e:
        print(f"[FAIL] OllamaAnalyzer: {e}")
        return False
    
    try:
        from core.image_processor import ImageProcessor
        print("[OK] ImageProcessor")
    except Exception as e:
        print(f"[FAIL] ImageProcessor: {e}")
        return False
    
    return True

def test_ollama():
    print("\nTesting Ollama connection...")
    import requests
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
        print(f"[OK] Connected ({len(models)} models)")
        
        if models:
            print("Available models:")
            for m in models:
                print(f"  - {m['name']}")
        
        return True
    except:
        print("[WARNING] Ollama not running")
        print("Start with: ollama serve")
        return False

def main():
    print("="*60)
    print("MILITARY ANOMALY SCANNER - SYSTEM TEST")
    print("="*60)
    
    all_ok = True
    
    all_ok &= test_imports()
    all_ok &= test_config()
    all_ok &= test_core_modules()
    ollama_ok = test_ollama()
    
    print("\n" + "="*60)
    
    if all_ok:
        print("[SUCCESS] All components verified")
    else:
        print("[ERROR] Some components failed")
    
    if not ollama_ok:
        print("\n[WARNING] Ollama not available")
        print("Install: https://ollama.ai")
        print("Start: ollama serve")
    
    print("="*60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
