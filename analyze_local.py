#!/usr/bin/env python3
"""
Local Image Analyzer - Analyze images already on disk
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

def find_images(directory, extensions=('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
    images = []
    for ext in extensions:
        images.extend(Path(directory).rglob(f'*{ext}'))
    return [str(img) for img in images]

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Local Image Analyzer')
    parser.add_argument('--input', '-i', type=str, required=True, help='Input directory with images')
    parser.add_argument('--output', '-o', type=str, default='data/reports', help='Output directory')
    parser.add_argument('--config', type=str, default='config/settings.json', help='Config file path')
    
    args = parser.parse_args()
    
    config_path = Path(__file__).parent / args.config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    logger = MilitaryLogger()
    scanner = OllamaAnalyzer(config, logger)
    processor = ImageProcessor(config, logger)
    
    if not scanner.check_connection():
        logger.error("Ollama not available. Please start: ollama serve")
        sys.exit(1)
    
    input_dir = Path(args.input)
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)
    
    logger.info(f"Scanning directory: {input_dir}")
    image_paths = find_images(input_dir)
    
    if not image_paths:
        logger.warning("No images found in input directory")
        sys.exit(0)
    
    logger.info(f"Found {len(image_paths)} images")
    
    logger.info("Processing images...")
    project_root = Path(__file__).parent
    processed = processor.batch_process(image_paths, project_root=project_root)
    
    enhanced_images = [p['enhanced'] for p in processed if p.get('enhanced')]
    
    logger.info("Analyzing images for anomalies...")
    analysis_results = scanner.batch_analyze(enhanced_images, processed_data=processed)
    
    summary = scanner.generate_summary_report(analysis_results)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    report_file = output_dir / f"local_analysis_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'session_id': timestamp,
            'input_directory': str(input_dir),
            'total_images': len(image_paths),
            'analysis_results': analysis_results,
            'summary': summary
        }, f, indent=2, default=str)
    
    summary_file = output_dir / f"local_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write(f"LOCAL IMAGE ANALYSIS REPORT\n")
        f.write(f"{'='*50}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Input: {input_dir}\n")
        f.write(f"Images Analyzed: {len(analysis_results)}\n")
        f.write(f"Anomalies Found: {summary['total_anomalies_detected']}\n")
        f.write(f"Threat Level: {summary['overall_threat_assessment']}\n\n")
        
        for category, count in summary.get('anomalies_by_category', {}).items():
            f.write(f"- {category}: {count}\n")
    
    logger.success(f"Analysis complete. Reports saved to: {output_dir}")
    logger.info(f"JSON Report: {report_file}")
    logger.info(f"Text Summary: {summary_file}")

if __name__ == "__main__":
    main()
