import unittest
import os
import json
import tempfile
from config import Config

class TestConfig(unittest.TestCase):
    """Config 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행"""
        # 임시 설정 파일 생성
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        # 빈 JSON 객체 작성 (파싱 에러 방지)
        self.temp_file.write('{}')
        self.temp_file.close()
        self.config = Config(config_file=self.temp_file.name)
    
    def tearDown(self):
        """각 테스트 후에 실행"""
        # 임시 파일 삭제
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_default_config(self):
        """기본 설정값 테스트"""
        self.assertEqual(self.config.get('download_path'), 'downloads')
        self.assertEqual(self.config.get('default_quality'), 'best')
        self.assertEqual(self.config.get('default_subtitle_lang'), 'ko')
        self.assertEqual(self.config.get('default_download_mode'), 'video_only')
    
    def test_set_and_get(self):
        """설정 저장 및 불러오기 테스트"""
        self.config.set('download_path', '/custom/path')
        self.assertEqual(self.config.get('download_path'), '/custom/path')
        
        # 파일에서 다시 로드
        new_config = Config(config_file=self.temp_file.name)
        self.assertEqual(new_config.get('download_path'), '/custom/path')
    
    def test_add_recent_url(self):
        """최근 URL 추가 테스트"""
        url1 = "https://youtube.com/watch?v=test1"
        url2 = "https://youtube.com/watch?v=test2"
        
        self.config.add_recent_url(url1)
        self.config.add_recent_url(url2)
        
        recent_urls = self.config.get_recent_urls()
        self.assertEqual(len(recent_urls), 2)
        self.assertEqual(recent_urls[0], url2)  # 최신이 맨 앞
        self.assertEqual(recent_urls[1], url1)
    
    def test_recent_url_deduplication(self):
        """중복 URL 제거 테스트"""
        url = "https://youtube.com/watch?v=test"
        
        # 같은 URL을 두 번 추가
        self.config.add_recent_url(url)
        self.config.add_recent_url(url)
        
        # 중복이 제거되어 1개만 있어야 함
        recent_urls = self.config.get_recent_urls()
        url_count = recent_urls.count(url)
        self.assertEqual(url_count, 1, f"URL이 {url_count}번 나타남, 1번이어야 함")
    
    def test_recent_url_max_limit(self):
        """최근 URL 최대 개수 제한 테스트"""
        # 11개 URL 추가 (최대 10개)
        for i in range(11):
            self.config.add_recent_url(f"https://youtube.com/watch?v=test{i}")
        
        recent_urls = self.config.get_recent_urls()
        self.assertEqual(len(recent_urls), 10)
        # 가장 오래된 것(test0)은 제거되어야 함
        self.assertNotIn("https://youtube.com/watch?v=test0", recent_urls)
    
    def test_reset_to_defaults(self):
        """기본값 초기화 테스트"""
        self.config.set('download_path', '/custom/path')
        self.config.reset_to_defaults()
        
        self.assertEqual(self.config.get('download_path'), 'downloads')
    
    def test_save_and_load(self):
        """설정 저장 및 로드 테스트"""
        self.config.set('download_path', '/test/path')
        self.config.set('default_quality', '720p')
        
        # 새 인스턴스로 로드
        new_config = Config(config_file=self.temp_file.name)
        self.assertEqual(new_config.get('download_path'), '/test/path')
        self.assertEqual(new_config.get('default_quality'), '720p')

if __name__ == '__main__':
    unittest.main()
