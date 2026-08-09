#!/usr/bin/env python3
"""
Ollama Model Manager - Download and manage models for anomaly scanning
"""

import os
import sys
import json
import requests
from pathlib import Path

class OllamaModelManager:
    def __init__(self, host="http://localhost:11434"):
        self.host = host
        
    def check_connection(self):
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except:
            return False
    
    def list_models(self):
        try:
            response = requests.get(f"{self.host}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            return models
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def pull_model(self, model_name):
        print(f"Pulling model: {model_name}...")
        try:
            response = requests.post(
                f"{self.host}/api/pull",
                json={"name": model_name},
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    status = json.loads(line)
                    if 'status' in status:
                        print(f"\r{status['status']}", end='', flush=True)
            print(f"\nModel {model_name} pulled successfully")
            return True
        except Exception as e:
            print(f"\nError pulling model: {e}")
            return False
    
    def get_recommended_models(self):
        return {
            "vision": [
                {"name": "llava:latest", "description": "Multimodal vision model (Recommended)"},
                {"name": "bakllava:latest", "description": "Alternative vision model"},
                {"name": "moondream:latest", "description": "Lightweight vision model"}
            ],
            "text": [
                {"name": "llama2:latest", "description": "General purpose text model"},
                {"name": "mistral:latest", "description": "Fast and efficient"},
                {"name": "codellama:latest", "description": "Code-focused model"}
            ]
        }
    
    def setup_required_models(self):
        if not self.check_connection():
            print("ERROR: Ollama not running. Start with: ollama serve")
            return False
        
        print("Checking required models...")
        available = [m['name'] for m in self.list_models()]
        
        required = ["llava:latest", "llama2:latest"]
        
        missing = []
        for model in required:
            model_base = model.split(':')[0]
            if not any(model_base in m for m in available):
                missing.append(model)
        
        if not missing:
            print("All required models available!")
            return True
        
        print(f"Missing models: {missing}")
        response = input("Download missing models? (y/n): ")
        
        if response.lower() == 'y':
            for model in missing:
                self.pull_model(model)
            return True
        else:
            print("Warning: Some models missing. Scanner may not work correctly.")
            return False

def main():
    manager = OllamaModelManager()
    
    if not manager.check_connection():
        print("ERROR: Cannot connect to Ollama")
        print("Please start Ollama: ollama serve")
        sys.exit(1)
    
    print("="*50)
    print("OLLAMA MODEL MANAGER")
    print("="*50)
    
    while True:
        print("\n1. List available models")
        print("2. Pull a model")
        print("3. Show recommended models")
        print("4. Setup required models")
        print("5. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == '1':
            models = manager.list_models()
            if models:
                print("\nAvailable models:")
                for m in models:
                    print(f"  - {m['name']}")
            else:
                print("No models found")
        
        elif choice == '2':
            model_name = input("Enter model name (e.g., llava:latest): ")
            manager.pull_model(model_name)
        
        elif choice == '3':
            recommended = manager.get_recommended_models()
            print("\nRecommended models for anomaly scanning:")
            for category, models in recommended.items():
                print(f"\n{category.upper()} models:")
                for m in models:
                    print(f"  - {m['name']}: {m['description']}")
        
        elif choice == '4':
            manager.setup_required_models()
        
        elif choice == '5':
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
