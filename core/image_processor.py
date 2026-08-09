import os
import json
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import hashlib

class ImageProcessor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.min_resolution = config['scanning']['min_image_resolution']
    
    def validate_image(self, image_path):
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    self.logger.warning(f"Image below minimum resolution: {image_path}")
                    return False
                return True
        except Exception as e:
            self.logger.error(f"Invalid image {image_path}: {str(e)}")
            return False
    
    def get_image_info(self, image_path):
        try:
            with Image.open(image_path) as img:
                info = {
                    'path': str(image_path),
                    'filename': os.path.basename(image_path),
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'megapixels': round((img.size[0] * img.size[1]) / 1000000, 2),
                    'file_size_bytes': os.path.getsize(image_path),
                    'hash': self._calculate_hash(image_path)
                }
                return info
        except Exception as e:
            self.logger.error(f"Failed to get image info: {str(e)}")
            return None
    
    def _calculate_hash(self, image_path):
        hash_md5 = hashlib.md5()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def enhance_for_analysis(self, image_path, output_path=None):
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return None
            
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
            
            if output_path is None:
                output_path = Path(image_path).parent / f"enhanced_{Path(image_path).name}"
            
            cv2.imwrite(str(output_path), denoised)
            self.logger.success(f"Enhanced image saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Enhancement failed: {str(e)}")
            return None
    
    def detect_edges(self, image_path, output_path=None):
        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            
            edges = cv2.Canny(img, 50, 150)
            
            kernel = np.ones((3,3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            edges = cv2.erode(edges, kernel, iterations=1)
            
            if output_path is None:
                output_path = Path(image_path).parent / f"edges_{Path(image_path).name}"
            
            cv2.imwrite(str(output_path), edges)
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Edge detection failed: {str(e)}")
            return None
    
    def detect_geometric_patterns(self, image_path):
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            patterns = []
            
            if lines is not None:
                patterns.append({
                    'type': 'lines_detected',
                    'count': len(lines),
                    'description': f'Detected {len(lines)} linear structures'
                })
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            geometric_shapes = 0
            for contour in contours:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
                
                if len(approx) >= 4 and len(approx) <= 6:
                    area = cv2.contourArea(contour)
                    if area > 500:
                        geometric_shapes += 1
            
            if geometric_shapes > 0:
                patterns.append({
                    'type': 'geometric_shapes',
                    'count': geometric_shapes,
                    'description': f'Detected {geometric_shapes} potential geometric patterns'
                })
            
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                       param1=50, param2=30, minRadius=20, maxRadius=100)
            
            if circles is not None:
                patterns.append({
                    'type': 'circular_structures',
                    'count': len(circles[0]),
                    'description': f'Detected {len(circles[0])} circular formations'
                })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {str(e)}")
            return []
    
    def create_annotated_copy(self, image_path, anomalies, output_path=None):
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 16)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                small_font = font
            
            threat_colors = {
                'NONE': 'green',
                'LOW': 'yellow',
                'MEDIUM': 'orange',
                'HIGH': 'red',
                'CRITICAL': 'magenta'
            }
            
            y_offset = 10
            for anomaly in anomalies[:5]:
                threat = anomaly.get('threat_level', 'NONE')
                color = threat_colors.get(threat, 'white')
                
                draw.text((10, y_offset), f"THREAT: {threat}", fill=color, font=font)
                draw.text((10, y_offset + 20), f"Category: {anomaly.get('category', 'Unknown')}", fill='white', font=small_font)
                draw.text((10, y_offset + 35), f"Confidence: {anomaly.get('confidence', 0):.1%}", fill='white', font=small_font)
                y_offset += 60
            
            if output_path is None:
                output_path = Path(image_path).parent / f"annotated_{Path(image_path).name}"
            
            img.save(output_path)
            self.logger.success(f"Annotated copy created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Annotation failed: {str(e)}")
            return None
    
    def batch_process(self, image_paths, output_dir=None, project_root=None):
        if output_dir is None:
            root = Path(project_root) if project_root else Path(__file__).parent.parent
            output_dir = root / "data" / "processed"
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        processed = []
        total = len(image_paths)
        
        self.logger.info(f"Processing {total} images")
        
        for i, image_path in enumerate(image_paths, 1):
            self.logger.info(f"Processing {i}/{total}: {os.path.basename(image_path)}")
            
            if not self.validate_image(image_path):
                continue
            
            info = self.get_image_info(image_path)
            if info is None:
                continue
            
            enhanced_path = self.enhance_for_analysis(
                image_path, 
                Path(output_dir) / f"enhanced_{info['filename']}"
            )
            
            edges_path = self.detect_edges(
                image_path,
                Path(output_dir) / f"edges_{info['filename']}"
            )
            
            patterns = self.detect_geometric_patterns(image_path)
            
            processed.append({
                'original': str(image_path),
                'info': info,
                'enhanced': enhanced_path,
                'edges': edges_path,
                'patterns': patterns
            })
        
        self.logger.success(f"Batch processing complete: {len(processed)}/{total} images")
        return processed
