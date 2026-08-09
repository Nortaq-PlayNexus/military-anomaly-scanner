import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

class OllamaAnalyzer:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.host = config['ollama']['host']
        self.model_vision = config['ollama']['model_vision']
        self.model_text = config['ollama']['model_text']
        
    def check_connection(self):
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            self.logger.success(f"Ollama connected. Available models: {len(models)}")
            return True
        except Exception as e:
            self.logger.error(f"Ollama connection failed: {str(e)}")
            return False
    
    def get_available_models(self):
        try:
            response = requests.get(f"{self.host}/api/tags")
            response.raise_for_status()
            return [m['name'] for m in response.json().get('models', [])]
        except Exception as e:
            self.logger.error(f"Failed to fetch models: {str(e)}")
            return []
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path, categories=None, geometric_patterns=None):
        if categories is None:
            categories = self.config['scanning']['anomaly_categories']
        
        try:
            image_base64 = self.encode_image(image_path)
            
            pattern_context = ""
            if geometric_patterns:
                pattern_details = []
                for p in geometric_patterns:
                    pattern_details.append(f"- {p.get('type')}: {p.get('description')}")
                pattern_context = (
                    "\n\nPRE-ANALYSIS GEOMETRIC DETECTION RESULTS:\n"
                    + "\n".join(pattern_details)
                    + "\nUse these as hints to focus your analysis on regions "
                    "where linear, geometric, or circular structures were detected."
                )
            
            prompt = f"""Analyze this image for anomalies in a military reconnaissance context.

Focus on detecting and classifying:
1. STRUCTURAL ANOMALIES: Unusual formations, geometric patterns, artificial-looking structures
2. ARTIFICIAL CONSTRUCTS: Buildings, roads, vehicles, equipment, infrastructure
3. POTENTIAL CRAFT/VEHICLES: Aircraft, spacecraft, ground vehicles, watercraft
4. BIOLOGICAL SIGNATURES: Vegetation patterns, potential organisms, life indicators
5. WATER/ICE DEPOSITS: Liquid water, ice formations, moisture patterns
6. GEOLOGICAL ANOMALIES: Unusual terrain, mineral deposits, volcanic features
7. GEOMETRIC PATTERNS: Straight lines, right angles, regular shapes (indicating artificial origin)
8. SHADOW ANOMALIES: Unusual shadows indicating hidden structures
9. SURFACE DISCONTINUITIES: abrupt changes in terrain or composition
10. THERMAL ANOMALIES: Hot or cold spots indicating activity

For each anomaly detected, provide:
- Category (from list above)
- Confidence level (0.0-1.0)
- Location description (relative position in image)
- Assessment (brief analysis)
- Threat level (NONE/LOW/MEDIUM/HIGH/CRITICAL)

Respond in JSON format:
{{
  "analysis_id": "unique_id",
  "image_path": "path",
  "anomalies_found": [
    {{
      "category": "category_name",
      "confidence": 0.85,
      "location": "description",
      "assessment": "brief_analysis",
      "threat_level": "LEVEL"
    }}
  ],
  "overall_assessment": "summary",
  "recommendation": "action_needed"
}}{pattern_context}"""
            
            payload = {
                "model": self.model_vision,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": self.config['ollama']['temperature'],
                    "num_predict": self.config['ollama']['max_tokens']
                }
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '')
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    analysis = json.loads(response_text[json_start:json_end])
                else:
                    analysis = {
                        "analysis_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
                        "image_path": str(image_path),
                        "anomalies_found": [],
                        "overall_assessment": response_text,
                        "recommendation": "MANUAL_REVIEW"
                    }
            except json.JSONDecodeError:
                analysis = {
                    "analysis_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
                    "image_path": str(image_path),
                    "anomalies_found": [],
                    "overall_assessment": response_text,
                    "recommendation": "MANUAL_REVIEW"
                }
            
            analysis['image_path'] = str(image_path)
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['model_used'] = self.model_vision
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {image_path}: {str(e)}")
            return {
                "analysis_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
                "image_path": str(image_path),
                "anomalies_found": [],
                "overall_assessment": f"Analysis error: {str(e)}",
                "recommendation": "RETRY",
                "error": str(e)
            }
    
    def batch_analyze(self, image_paths, batch_size=None, processed_data=None):
        if batch_size is None:
            batch_size = self.config['scanning']['analysis_batch_size']
        
        results = []
        total = len(image_paths)
        
        self.logger.info(f"Initiating batch analysis: {total} targets")
        
        patterns_map = {}
        if processed_data:
            for item in processed_data:
                enhanced = item.get('enhanced')
                if enhanced:
                    patterns_map[enhanced] = item.get('patterns', [])
        
        for i in range(0, total, batch_size):
            batch = image_paths[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches}")
            
            for image_path in batch:
                patterns = patterns_map.get(image_path, [])
                result = self.analyze_image(image_path, geometric_patterns=patterns)
                results.append(result)
                
                if result.get('anomalies_found'):
                    high_confidence = [
                        a for a in result['anomalies_found'] 
                        if a.get('confidence', 0) >= self.config['scanning']['confidence_threshold']
                    ]
                    if high_confidence:
                        self.logger.warning(f"HIGH CONFIDENCE ANOMALIES: {image_path}")
                        for anomaly in high_confidence:
                            self.logger.warning(f"  - {anomaly.get('category')}: {anomaly.get('assessment')}")
        
        self.logger.success(f"Batch analysis complete: {total} images processed")
        return results
    
    def generate_summary_report(self, analysis_results):
        summary = {
            "report_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "total_images_analyzed": len(analysis_results),
            "total_anomalies_detected": 0,
            "anomalies_by_category": {},
            "anomalies_by_threat_level": {
                "NONE": 0,
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0,
                "CRITICAL": 0
            },
            "high_priority_findings": [],
            "overall_threat_assessment": "UNKNOWN",
            "recommendations": []
        }
        
        for result in analysis_results:
            for anomaly in result.get('anomalies_found', []):
                summary['total_anomalies_detected'] += 1
                
                category = anomaly.get('category', 'unknown')
                summary['anomalies_by_category'][category] = summary['anomalies_by_category'].get(category, 0) + 1
                
                threat = anomaly.get('threat_level', 'NONE').upper()
                if threat in summary['anomalies_by_threat_level']:
                    summary['anomalies_by_threat_level'][threat] += 1
                
                if anomaly.get('confidence', 0) >= self.config['scanning']['confidence_threshold']:
                    if threat in ['HIGH', 'CRITICAL']:
                        summary['high_priority_findings'].append({
                            'image': result.get('image_path'),
                            'anomaly': anomaly
                        })
        
        critical = summary['anomalies_by_threat_level']['CRITICAL']
        high = summary['anomalies_by_threat_level']['HIGH']
        medium = summary['anomalies_by_threat_level']['MEDIUM']
        
        if critical > 0:
            summary['overall_threat_assessment'] = 'CRITICAL'
        elif high > 0:
            summary['overall_threat_assessment'] = 'HIGH'
        elif medium > 0:
            summary['overall_threat_assessment'] = 'MEDIUM'
        elif summary['total_anomalies_detected'] > 0:
            summary['overall_threat_assessment'] = 'LOW'
        else:
            summary['overall_threat_assessment'] = 'MINIMAL'
        
        if summary['overall_threat_assessment'] in ['CRITICAL', 'HIGH']:
            summary['recommendations'].append("IMMEDIATE MANUAL REVIEW REQUIRED")
            summary['recommendations'].append("ESCALATE TO COMMAND STRUCTURE")
        
        if summary['anomalies_by_category'].get('potential_craft_vehicles', 0) > 0:
            summary['recommendations'].append("DETAILED CRAFT ANALYSIS RECOMMENDED")
        
        if summary['anomalies_by_category'].get('biological_signatures', 0) > 0:
            summary['recommendations'].append("BIOLOGICAL SURVEY TEAM DEPLOYMENT CONSIDERED")
        
        if summary['anomalies_by_category'].get('water_ice_deposits', 0) > 0:
            summary['recommendations'].append("WATER RESOURCE MAPPING PRIORITIZED")
        
        return summary
