import hashlib
from pathlib import Path
from urllib.parse import urlparse, urljoin


class FileUtils:
    @staticmethod
    def ensure_directories(base_path, directories):
        for dir_name in directories:
            dir_path = Path(base_path) / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_hash(filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def sanitize_filename(filename, max_length=100):
        name = Path(filename).stem
        name = ''.join(c for c in name if c.isalnum() or c in '._- ')
        return name[:max_length]

    @staticmethod
    def get_unique_filename(directory, filename):
        filepath = Path(directory) / filename
        if not filepath.exists():
            return str(filepath)

        stem = filepath.stem
        suffix = filepath.suffix
        counter = 1

        while filepath.exists():
            filepath = Path(directory) / f"{stem}_{counter}{suffix}"
            counter += 1

        return str(filepath)


class URLUtils:
    @staticmethod
    def is_valid_url(url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def is_image_url(url):
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']
        parsed = urlparse(url)
        return any(parsed.path.lower().endswith(ext) for ext in valid_extensions)

    @staticmethod
    def extract_domain(url):
        parsed = urlparse(url)
        return parsed.netloc

    @staticmethod
    def normalize_url(url, base_url):
        return urljoin(base_url, url)
