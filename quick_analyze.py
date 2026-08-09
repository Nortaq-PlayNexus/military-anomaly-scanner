#!/usr/bin/env python3
"""
Quick Analysis - Analyze a single image or small batch
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.ollama_scanner import OllamaAnalyzer
from core.image_processor import ImageProcessor
from core import MilitaryLogger

def analyze_single_image(image_path, config_path="config/settings.json"):
    base_dir = Path(__file__).parent
    config_file = base_dir / config_path
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    logger = MilitaryLogger()
    scanner = OllamaAnalyzer(config, logger)
    processor = ImageProcessor(config, logger)
    
    if not scanner.check_connection():
        logger.error("Ollama not available")
        return None
    
    image_path = Path(image_path)
    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        return None
    
    logger.info(f"Analyzing: {image_path}")
    
    enhanced = processor.enhance_for_analysis(image_path)
    if enhanced:
        result = scanner.analyze_image(enhanced)
    else:
        result = scanner.analyze_image(str(image_path))
    
    print("\n" + "="*60)
    print("ANALYSIS RESULT")
    print("="*60)
    print(f"Image: {image_path.name}")
    print(f"Anomalies Found: {len(result.get('anomalies_found', []))}")
    
    for i, anomaly in enumerate(result.get('anomalies_found', []), 1):
        print(f"\nAnomaly {i}:")
        print(f"  Category: {anomaly.get('category')}")
        print(f"  Confidence: {anomaly.get('confidence', 0):.1%}")
        print(f"  Threat Level: {anomaly.get('threat_level')}")
        print(f"  Assessment: {anomaly.get('assessment')}")
    
    print(f"\nOverall Assessment: {result.get('overall_assessment', 'N/A')}")
    print(f"Recommendation: {result.get('recommendation', 'N/A')}")
    print("="*60)
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Image Analysis')
    parser.add_argument('image', type=str, help='Path to image file')
    parser.add_argument('--config', type=str, default='config/settings.json')
    
    args = parser.parse_args()
    
    result = analyze_single_image(args.image, args.config)
    
    if result:
        output_file = Path("data") / "reports" / f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\nReport saved: {output_file}")

if __name__ == "__main__":
    main()
