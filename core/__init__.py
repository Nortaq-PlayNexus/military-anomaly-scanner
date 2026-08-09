import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

class MilitaryLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        log_file = self.log_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("MILITARY_SCANNER")
    
    def info(self, msg):
        self.logger.info(f"[INTEL] {msg}")
    
    def warning(self, msg):
        self.logger.warning(f"[ALERT] {msg}")
    
    def error(self, msg):
        self.logger.error(f"[CRITICAL] {msg}")
    
    def success(self, msg):
        self.logger.info(f"[SUCCESS] {msg}")
