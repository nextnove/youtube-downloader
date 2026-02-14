import logging
import os
from datetime import datetime
from pathlib import Path

class AppLogger:
    """애플리케이션 로깅 시스템"""
    
    def __init__(self, log_dir='logs', log_level=logging.INFO):
        """
        로거 초기화
        
        Args:
            log_dir (str): 로그 파일 저장 디렉토리
            log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = log_dir
        self.log_level = log_level
        
        # 로그 디렉토리 생성
        Path(log_dir).mkdir(exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger('YouTubeDownloader')
        self.logger.setLevel(log_level)
        
        # 기존 핸들러 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 파일 핸들러 설정 (날짜별 로그 파일)
        log_filename = f"youtube_downloader_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """디버그 레벨 로그"""
        self.logger.debug(message)
    
    def info(self, message):
        """정보 레벨 로그"""
        self.logger.info(message)
    
    def warning(self, message):
        """경고 레벨 로그"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """에러 레벨 로그"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """치명적 에러 레벨 로그"""
        self.logger.critical(message, exc_info=exc_info)
    
    def log_download_start(self, url, mode, quality=None, subtitle_langs=None):
        """다운로드 시작 로그"""
        self.info(f"다운로드 시작 - URL: {url}, 모드: {mode}, 품질: {quality}, 자막: {subtitle_langs}")
    
    def log_download_success(self, url, mode):
        """다운로드 성공 로그"""
        self.info(f"다운로드 성공 - URL: {url}, 모드: {mode}")
    
    def log_download_failure(self, url, mode, error):
        """다운로드 실패 로그"""
        self.error(f"다운로드 실패 - URL: {url}, 모드: {mode}, 에러: {error}", exc_info=True)
    
    def log_config_change(self, key, old_value, new_value):
        """설정 변경 로그"""
        self.info(f"설정 변경 - {key}: {old_value} -> {new_value}")
    
    def get_recent_logs(self, lines=50):
        """최근 로그 라인 가져오기"""
        log_filename = f"youtube_downloader_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = os.path.join(self.log_dir, log_filename)
        
        if not os.path.exists(log_filepath):
            return []
        
        try:
            with open(log_filepath, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            self.error(f"로그 파일 읽기 실패: {e}")
            return []

# 전역 로거 인스턴스
_logger_instance = None

def get_logger():
    """전역 로거 인스턴스 가져오기"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AppLogger()
    return _logger_instance
