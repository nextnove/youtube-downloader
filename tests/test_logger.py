import unittest
import os
import tempfile
import shutil
from logger import AppLogger
import logging

class TestLogger(unittest.TestCase):
    """AppLogger 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행"""
        # 임시 로그 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.logger = AppLogger(log_dir=self.temp_dir, log_level=logging.DEBUG)
    
    def tearDown(self):
        """각 테스트 후에 실행"""
        # 로거 핸들러 닫기 (Windows 파일 잠금 해제)
        if hasattr(self, 'logger'):
            for handler in self.logger.logger.handlers[:]:
                handler.close()
                self.logger.logger.removeHandler(handler)
        
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # Windows에서 파일이 잠겨있을 수 있음
                import time
                time.sleep(0.1)
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass  # 테스트 환경에서는 무시
    
    def test_log_directory_creation(self):
        """로그 디렉토리 생성 테스트"""
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_log_file_creation(self):
        """로그 파일 생성 테스트"""
        self.logger.info("테스트 메시지")
        
        # 로그 파일이 생성되었는지 확인
        log_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.log')]
        self.assertEqual(len(log_files), 1)
    
    def test_log_levels(self):
        """다양한 로그 레벨 테스트"""
        self.logger.debug("디버그 메시지")
        self.logger.info("정보 메시지")
        self.logger.warning("경고 메시지")
        self.logger.error("에러 메시지")
        self.logger.critical("치명적 에러 메시지")
        
        # 로그 파일에 기록되었는지 확인
        recent_logs = self.logger.get_recent_logs()
        self.assertGreater(len(recent_logs), 0)
    
    def test_log_download_start(self):
        """다운로드 시작 로그 테스트"""
        url = "https://youtube.com/watch?v=test"
        self.logger.log_download_start(url, 'video', quality='720p', subtitle_langs=['ko'])
        
        recent_logs = self.logger.get_recent_logs()
        log_content = ''.join(recent_logs)
        self.assertIn(url, log_content)
        self.assertIn('video', log_content)
    
    def test_log_download_success(self):
        """다운로드 성공 로그 테스트"""
        url = "https://youtube.com/watch?v=test"
        self.logger.log_download_success(url, 'video')
        
        recent_logs = self.logger.get_recent_logs()
        log_content = ''.join(recent_logs)
        self.assertIn('성공', log_content)
        self.assertIn(url, log_content)
    
    def test_log_download_failure(self):
        """다운로드 실패 로그 테스트"""
        url = "https://youtube.com/watch?v=test"
        error = "테스트 에러"
        self.logger.log_download_failure(url, 'video', error)
        
        recent_logs = self.logger.get_recent_logs()
        log_content = ''.join(recent_logs)
        self.assertIn('실패', log_content)
        self.assertIn(error, log_content)
    
    def test_get_recent_logs(self):
        """최근 로그 가져오기 테스트"""
        # 여러 로그 메시지 작성
        for i in range(10):
            self.logger.info(f"테스트 메시지 {i}")
        
        # 최근 5개만 가져오기
        recent_logs = self.logger.get_recent_logs(lines=5)
        self.assertEqual(len(recent_logs), 5)
    
    def test_log_config_change(self):
        """설정 변경 로그 테스트"""
        self.logger.log_config_change('download_path', 'downloads', '/custom/path')
        
        recent_logs = self.logger.get_recent_logs()
        log_content = ''.join(recent_logs)
        self.assertIn('설정 변경', log_content)
        self.assertIn('download_path', log_content)

if __name__ == '__main__':
    unittest.main()
