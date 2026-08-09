import os
import re
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class WebScraper:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config['target']['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        self.visited_urls = set()
        self.downloaded_images = []
        
    def sanitize_filename(self, url):
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename or '.' not in filename:
            filename = f"image_{url_hash}.jpg"
        return filename
    
    def is_valid_image_url(self, url):
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
        parsed = urlparse(url)
        return any(parsed.path.lower().endswith(ext) for ext in valid_extensions)
    
    def extract_image_urls(self, html_content, base_url):
        soup = BeautifulSoup(html_content, 'lxml')
        image_urls = set()
        
        for img in soup.find_all('img', src=True):
            img_url = urljoin(base_url, img['src'])
            if self.is_valid_image_url(img_url):
                image_urls.add(img_url)
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if self.is_valid_image_url(href):
                image_urls.add(urljoin(base_url, href))
        
        for meta in soup.find_all('meta', attrs={'content': True}):
            content = meta.get('content', '')
            if self.is_valid_image_url(content):
                image_urls.add(urljoin(base_url, content))
        
        return list(image_urls)
    
    def extract_page_links(self, html_content, base_url):
        soup = BeautifulSoup(html_content, 'lxml')
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            if full_url.startswith(self.config['target']['base_url']):
                if full_url not in self.visited_urls:
                    links.add(full_url)
        
        return list(links)
    
    def download_image(self, url, save_dir):
        try:
            filename = self.sanitize_filename(url)
            filepath = Path(save_dir) / filename
            
            if filepath.exists():
                self.logger.info(f"Image already exists: {filename}")
                return str(filepath)
            
            response = self.session.get(url, timeout=self.config['system']['timeout_seconds'])
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type or len(response.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.logger.success(f"Downloaded: {filename} ({len(response.content)} bytes)")
                return str(filepath)
            else:
                self.logger.warning(f"Invalid image content: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {str(e)}")
            return None
    
    def scrape_pages(self, max_pages=None):
        if max_pages is None:
            max_pages = self.config['target']['max_pages']
        
        base_url = self.config['target']['base_url']
        pages_scraped = 0
        all_image_urls = set()
        urls_to_visit = [base_url]
        
        self.logger.info(f"Initiating reconnaissance on {base_url}")
        self.logger.info(f"Target: {max_pages} pages")
        
        while urls_to_visit and pages_scraped < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            try:
                self.logger.info(f"Scanning page {pages_scraped + 1}/{max_pages}: {current_url}")
                
                response = self.session.get(current_url, timeout=self.config['system']['timeout_seconds'])
                response.raise_for_status()
                
                self.visited_urls.add(current_url)
                pages_scraped += 1
                
                image_urls = self.extract_image_urls(response.text, current_url)
                all_image_urls.update(image_urls)
                
                new_links = self.extract_page_links(response.text, current_url)
                urls_to_visit.extend(new_links)
                
                self.logger.info(f"Found {len(image_urls)} images on page")
                
                time.sleep(self.config['target']['download_delay_ms'] / 1000)
                
            except Exception as e:
                self.logger.error(f"Error scraping {current_url}: {str(e)}")
                continue
        
        self.logger.success(f"Reconnaissance complete. Scraped {pages_scraped} pages, found {len(all_image_urls)} unique images")
        
        return list(all_image_urls)[:self.config['target']['max_images']]
    
    def download_images(self, image_urls, save_dir=None, project_root=None):
        if save_dir is None:
            root = Path(project_root) if project_root else Path(__file__).parent.parent
            save_dir = root / "data" / "images"
        
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        downloaded = []
        max_threads = self.config['system']['max_threads']
        
        self.logger.info(f"Initiating image acquisition: {len(image_urls)} targets")
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_url = {
                executor.submit(self.download_image, url, save_dir): url 
                for url in image_urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        downloaded.append({
                            'url': url,
                            'path': result,
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    self.logger.error(f"Download failed for {url}: {str(e)}")
        
        self.logger.success(f"Acquired {len(downloaded)}/{len(image_urls)} images")
        
        manifest_path = Path(save_dir) / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(downloaded, f, indent=2)
        
        return downloaded
