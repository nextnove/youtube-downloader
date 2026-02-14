import json
import os
from pathlib import Path

class Config:
    """애플리케이션 설정 관리 클래스"""
    
    DEFAULT_CONFIG = {
        'download_path': 'downloads',
        'default_quality': 'best',
        'default_subtitle_lang': 'ko',
        'default_download_mode': 'video_only',
        'recent_urls': [],
        'max_recent_urls': 10
    }
    
    def __init__(self, config_file='config.json'):
        """
        설정 관리자 초기화
        
        Args:
            config_file (str): 설정 파일 경로
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """설정 파일을 로드합니다. 없으면 기본값을 사용합니다."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 기본값과 병합 (새로운 설정 항목 추가 대응)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"설정 파일 로드 실패: {e}")
                print("기본 설정을 사용합니다.")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """현재 설정을 파일에 저장합니다."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"설정 파일 저장 실패: {e}")
            return False
    
    def get(self, key, default=None):
        """설정 값을 가져옵니다."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """설정 값을 변경하고 저장합니다."""
        self.config[key] = value
        self.save_config()
    
    def add_recent_url(self, url):
        """최근 사용한 URL을 추가합니다."""
        recent_urls = self.config.get('recent_urls', [])
        
        # 이미 있으면 제거 (맨 앞으로 이동하기 위해)
        if url in recent_urls:
            recent_urls.remove(url)
        
        # 맨 앞에 추가
        recent_urls.insert(0, url)
        
        # 최대 개수 제한
        max_recent = self.config.get('max_recent_urls', 10)
        recent_urls = recent_urls[:max_recent]
        
        self.config['recent_urls'] = recent_urls
        self.save_config()
    
    def get_recent_urls(self):
        """최근 사용한 URL 목록을 가져옵니다."""
        return self.config.get('recent_urls', [])
    
    def reset_to_defaults(self):
        """설정을 기본값으로 초기화합니다."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
