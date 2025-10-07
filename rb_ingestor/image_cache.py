# rb_ingestor/image_cache.py
"""
Sistema de cache para imagens buscadas.
Armazena URLs e metadados para evitar buscas repetidas.
"""

import os
import json
import hashlib
import time
from typing import Optional, Dict, Any
from pathlib import Path

class ImageCache:
    """Sistema de cache para imagens com persistência em arquivo."""
    
    def __init__(self, cache_file: str = "image_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache_data = self._load_cache()
        self.max_age = 7 * 24 * 3600  # 7 dias em segundos
    
    def _load_cache(self) -> Dict[str, Any]:
        """Carrega cache do arquivo."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Salva cache no arquivo."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def _generate_key(self, title: str, category: str = "") -> str:
        """Gera chave única para o cache."""
        content = f"{title}_{category}".lower()
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, title: str, category: str = "") -> Optional[str]:
        """Recupera URL da imagem do cache."""
        key = self._generate_key(title, category)
        
        if key in self.cache_data:
            entry = self.cache_data[key]
            
            # Verificar se não expirou
            if time.time() - entry['timestamp'] < self.max_age:
                return entry['url']
            else:
                # Remover entrada expirada
                del self.cache_data[key]
                self._save_cache()
        
        return None
    
    def set(self, title: str, url: str, category: str = "", metadata: Dict = None):
        """Armazena URL da imagem no cache."""
        key = self._generate_key(title, category)
        
        self.cache_data[key] = {
            'url': url,
            'timestamp': time.time(),
            'title': title[:100],  # Limitar tamanho
            'category': category,
            'metadata': metadata or {}
        }
        
        self._save_cache()
    
    def clear_expired(self):
        """Remove entradas expiradas do cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache_data.items():
            if current_time - entry['timestamp'] > self.max_age:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache_data[key]
        
        if expired_keys:
            self._save_cache()
            print(f"Removidas {len(expired_keys)} entradas expiradas do cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        current_time = time.time()
        total_entries = len(self.cache_data)
        expired_entries = 0
        
        for entry in self.cache_data.values():
            if current_time - entry['timestamp'] > self.max_age:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'cache_file': str(self.cache_file),
            'max_age_days': self.max_age / (24 * 3600)
        }


# Instância global do cache
image_cache = ImageCache()
