#!/usr/bin/env python3
"""
MILITARY ANOMALY SCANNER - TOP SECRET//SCI
Automated reconnaissance and anomaly detection system
Using Ollama local LLM models for intelligent analysis
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.scraper import WebScraper
from core.ollama_scanner import OllamaAnalyzer
from core.image_processor import ImageProcessor
from core import MilitaryLogger

class MilitaryAnomalyScanner:
    def __init__(self, config_path="config/settings.json"):
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        
        self.logger = MilitaryLogger(log_dir=str(self.base_dir / "logs"))
        
        self.scraper = WebScraper(self.config, self.logger)
        self.scanner = OllamaAnalyzer(self.config, self.logger)
        self.processor = ImageProcessor(self.config, self.logger)
        
        self.results = {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'start_time': None,
            'end_time': None,
            'pages_scraped': 0,
            'images_downloaded': 0,
            'images_analyzed': 0,
            'anomalies_detected': 0,
            'high_priority_anomalies': 0,
            'analysis_results': [],
            'summary': {}
        }
    
    def _load_config(self, config_path):
        config_file = self.base_dir / config_path
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def preflight_check(self):
        self.logger.info("Initiating preflight checks...")
        
        if not self.scanner.check_connection():
            self.logger.error("Ollama service not available")
            self.logger.info("Please ensure Ollama is running: ollama serve")
            return False
        
        available_models = self.scanner.get_available_models()
        self.logger.info(f"Available Ollama models: {available_models}")
        
        required_models = [
            self.config['ollama']['model_vision'],
            self.config['ollama']['model_text']
        ]
        
        for model in required_models:
            model_name = model.split(':')[0]
            if not any(model_name in m for m in available_models):
                self.logger.warning(f"Model {model} not found in Ollama")
        
        self.logger.success("Preflight checks complete")
        return True
    
    def execute_scan(self, custom_pages=None, custom_images=None):
        start_time = datetime.now()
        self.results['start_time'] = start_time.isoformat()
        
        self.logger.info("=" * 60)
        self.logger.info("MILITARY ANOMALY SCANNER - MISSION START")
        self.logger.info(f"Session ID: {self.results['session_id']}")
        self.logger.info("=" * 60)
        
        if not self.preflight_check():
            self.logger.error("Preflight failed. Aborting mission.")
            return None
        
        max_pages = custom_pages or self.config['target']['max_pages']
        max_images = custom_images or self.config['target']['max_images']
        
        self.logger.info(f"Phase 1: RECONNAISSANCE - Target: {max_pages} pages, {max_images} images")
        image_urls = self.scraper.scrape_pages(max_pages)
        self.results['pages_scraped'] = len(self.scraper.visited_urls)
        
        self.logger.info("Phase 2: IMAGE ACQUISITION")
        downloaded = self.scraper.download_images(image_urls)
        self.results['images_downloaded'] = len(downloaded)
        
        self.logger.info("Phase 3: IMAGE PROCESSING")
        image_paths = [d['path'] for d in downloaded if d.get('path')]
        processed = self.processor.batch_process(image_paths)
        
        self.logger.info("Phase 4: ANOMALY DETECTION")
        enhanced_images = [p['enhanced'] for p in processed if p.get('enhanced')]
        analysis_results = self.scanner.batch_analyze(enhanced_images, processed_data=processed)
        self.results['analysis_results'] = analysis_results
        self.results['images_analyzed'] = len(analysis_results)
        
        self.logger.info("Phase 5: REPORT GENERATION")
        summary = self.scanner.generate_summary_report(analysis_results)
        self.results['summary'] = summary
        self.results['anomalies_detected'] = summary['total_anomalies_detected']
        
        for result in analysis_results:
            for anomaly in result.get('anomalies_found', []):
                if anomaly.get('confidence', 0) >= self.config['scanning']['confidence_threshold']:
                    if anomaly.get('threat_level', '').upper() in ['HIGH', 'CRITICAL']:
                        self.results['high_priority_anomalies'] += 1
        
        self._create_annotated_images(analysis_results)
        self._save_report()
        
        end_time = datetime.now()
        self.results['end_time'] = end_time.isoformat()
        duration = (end_time - start_time).total_seconds()
        
        self.logger.info("=" * 60)
        self.logger.info("MISSION COMPLETE")
        self.logger.info(f"Duration: {duration:.1f} seconds")
        self.logger.info(f"Pages Scraped: {self.results['pages_scraped']}")
        self.logger.info(f"Images Downloaded: {self.results['images_downloaded']}")
        self.logger.info(f"Images Analyzed: {self.results['images_analyzed']}")
        self.logger.info(f"Anomalies Detected: {self.results['anomalies_detected']}")
        self.logger.info(f"High Priority: {self.results['high_priority_anomalies']}")
        self.logger.info(f"Overall Threat: {summary.get('overall_threat_assessment', 'UNKNOWN')}")
        self.logger.info("=" * 60)
        
        return self.results
    
    def _create_annotated_images(self, analysis_results):
        for result in analysis_results:
            if result.get('anomalies_found'):
                image_path = result.get('image_path')
                if image_path and os.path.exists(image_path):
                    self.processor.create_annotated_copy(
                        image_path,
                        result['anomalies_found']
                    )
    
    def _save_report(self):
        report_dir = self.base_dir / "data" / "reports"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"report_{self.results['session_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        self.logger.success(f"Report saved: {report_file}")
        
        executive_summary = self._generate_executive_summary()
        summary_file = report_dir / f"executive_summary_{self.results['session_id']}.txt"
        with open(summary_file, 'w') as f:
            f.write(executive_summary)
        
        self.logger.success(f"Executive summary saved: {summary_file}")
    
    def _generate_executive_summary(self):
        summary = self.results.get('summary', {})
        
        report = f"""
{'='*60}
MILITARY ANOMALY SCANNER - EXECUTIVE SUMMARY
{'='*60}
Classification: TOP SECRET//SCI
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {self.results['session_id']}

MISSION STATISTICS:
- Pages Reconnoitered: {self.results['pages_scraped']}
- Images Acquired: {self.results['images_downloaded']}
- Images Analyzed: {self.results['images_analyzed']}
- Total Anomalies: {self.results['anomalies_detected']}
- High Priority Findings: {self.results['high_priority_anomalies']}

THREAT ASSESSMENT: {summary.get('overall_threat_assessment', 'UNKNOWN')}

ANOMALY BREAKDOWN:
"""
        
        for category, count in summary.get('anomalies_by_category', {}).items():
            report += f"- {category}: {count}\n"
        
        report += "\nTHREAT LEVEL DISTRIBUTION:\n"
        for level, count in summary.get('anomalies_by_threat_level', {}).items():
            report += f"- {level}: {count}\n"
        
        if summary.get('high_priority_findings'):
            report += "\nHIGH PRIORITY FINDINGS:\n"
            for finding in summary['high_priority_findings']:
                report += f"- {finding['image']}: {finding['anomaly'].get('assessment', 'N/A')}\n"
        
        if summary.get('recommendations'):
            report += "\nRECOMMENDATIONS:\n"
            for rec in summary['recommendations']:
                report += f"- {rec}\n"
        
        report += f"\n{'='*60}\nEND OF REPORT\n{'='*60}\n"
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Military Anomaly Scanner')
    parser.add_argument('--pages', type=int, help='Number of pages to scrape')
    parser.add_argument('--images', type=int, help='Number of images to download')
    parser.add_argument('--config', type=str, default='config/settings.json', help='Config file path')
    
    args = parser.parse_args()
    
    scanner = MilitaryAnomalyScanner(config_path=args.config)
    results = scanner.execute_scan(
        custom_pages=args.pages,
        custom_images=args.images
    )
    
    if results:
        print("\nMission complete. Check data/reports/ for detailed analysis.")
        sys.exit(0)
    else:
        print("\nMission failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
