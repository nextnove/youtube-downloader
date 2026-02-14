import re
from urllib.parse import urlparse, parse_qs
from logger import get_logger

class SecurityValidator:
    """보안 검증 클래스"""
    
    # YouTube URL 패턴
    YOUTUBE_PATTERNS = [
        r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(www\.)?youtube\.com/shorts/[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
        r'^https?://(www\.)?youtube\.com/v/[\w-]+',
    ]
    
    # 허용된 도메인
    ALLOWED_DOMAINS = [
        'youtube.com',
        'www.youtube.com',
        'youtu.be',
        'm.youtube.com'
    ]
    
    def __init__(self):
        self.logger = get_logger()
    
    def validate_youtube_url(self, url):
        """
        YouTube URL 유효성 검증
        
        Args:
            url (str): 검증할 URL
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not url or not isinstance(url, str):
            return False, "URL이 비어있거나 올바르지 않습니다."
        
        url = url.strip()
        
        # 기본 URL 형식 검증
        try:
            parsed = urlparse(url)
        except Exception as e:
            self.logger.warning(f"URL 파싱 실패: {url}, 에러: {e}")
            return False, "올바르지 않은 URL 형식입니다."
        
        # 프로토콜 검증 (http 또는 https만 허용)
        if parsed.scheme not in ['http', 'https']:
            self.logger.warning(f"허용되지 않은 프로토콜: {parsed.scheme}")
            return False, "http 또는 https 프로토콜만 허용됩니다."
        
        # 도메인 검증
        if parsed.netloc not in self.ALLOWED_DOMAINS:
            self.logger.warning(f"허용되지 않은 도메인: {parsed.netloc}")
            return False, f"YouTube URL만 허용됩니다. (입력된 도메인: {parsed.netloc})"
        
        # YouTube URL 패턴 검증
        is_valid_pattern = any(re.match(pattern, url) for pattern in self.YOUTUBE_PATTERNS)
        
        if not is_valid_pattern:
            self.logger.warning(f"YouTube URL 패턴 불일치: {url}")
            return False, "올바른 YouTube 비디오 URL이 아닙니다."
        
        # 비디오 ID 추출 시도
        video_id = self.extract_video_id(url)
        if not video_id:
            self.logger.warning(f"비디오 ID 추출 실패: {url}")
            return False, "비디오 ID를 찾을 수 없습니다."
        
        self.logger.info(f"URL 검증 성공: {url} (비디오 ID: {video_id})")
        return True, ""
    
    def extract_video_id(self, url):
        """
        YouTube URL에서 비디오 ID 추출
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: 비디오 ID 또는 None
        """
        try:
            parsed = urlparse(url)
            
            # youtube.com/watch?v=VIDEO_ID
            if 'youtube.com' in parsed.netloc and parsed.path == '/watch':
                query_params = parse_qs(parsed.query)
                return query_params.get('v', [None])[0]
            
            # youtu.be/VIDEO_ID
            elif 'youtu.be' in parsed.netloc:
                return parsed.path.lstrip('/')
            
            # youtube.com/shorts/VIDEO_ID
            elif 'youtube.com' in parsed.netloc and '/shorts/' in parsed.path:
                return parsed.path.split('/shorts/')[-1].split('/')[0]
            
            # youtube.com/embed/VIDEO_ID
            elif 'youtube.com' in parsed.netloc and '/embed/' in parsed.path:
                return parsed.path.split('/embed/')[-1].split('/')[0]
            
            # youtube.com/v/VIDEO_ID
            elif 'youtube.com' in parsed.netloc and '/v/' in parsed.path:
                return parsed.path.split('/v/')[-1].split('/')[0]
            
        except Exception as e:
            self.logger.error(f"비디오 ID 추출 중 오류: {e}")
        
        return None
    
    def sanitize_filename(self, filename):
        """
        파일명에서 위험한 문자 제거
        
        Args:
            filename (str): 원본 파일명
            
        Returns:
            str: 안전한 파일명
        """
        # Windows/Linux에서 허용되지 않는 문자 제거
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        safe_filename = re.sub(dangerous_chars, '_', filename)
        
        # 파일명 길이 제한 (255자) - 확장자 보존
        if len(safe_filename) > 255:
            # 확장자 분리
            import os
            name, ext = os.path.splitext(safe_filename)
            # 확장자를 제외한 이름 부분만 자르기
            max_name_length = 255 - len(ext)
            safe_filename = name[:max_name_length] + ext
        
        return safe_filename
    
    def validate_download_path(self, path):
        """
        다운로드 경로 검증
        
        Args:
            path (str): 검증할 경로
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not path or not isinstance(path, str):
            return False, "경로가 비어있거나 올바르지 않습니다."
        
        path = path.strip()
        
        # 상대 경로 공격 방지 (../ 패턴)
        if '..' in path:
            self.logger.warning(f"경로 순회 공격 시도 감지: {path}")
            return False, "상위 디렉토리 접근은 허용되지 않습니다."
        
        # 절대 경로인 경우 시스템 디렉토리 접근 방지
        import os
        if os.path.isabs(path):
            # 현재 OS에 따라 검증
            if os.name == 'nt':  # Windows
                # Windows 시스템 디렉토리
                dangerous_paths_win = ['C:\\Windows', 'C:\\Program Files', 'C:\\System32']
                for dangerous in dangerous_paths_win:
                    if path.lower().startswith(dangerous.lower()):
                        self.logger.warning(f"시스템 디렉토리 접근 시도: {path}")
                        return False, "시스템 디렉토리에는 저장할 수 없습니다."
            else:  # Unix-like (Linux, macOS)
                # Linux/Mac 시스템 디렉토리
                dangerous_paths_unix = ['/bin', '/sbin', '/usr/bin', '/usr/sbin', '/etc', '/sys', '/proc']
                for dangerous in dangerous_paths_unix:
                    if path.startswith(dangerous):
                        self.logger.warning(f"시스템 디렉토리 접근 시도: {path}")
                        return False, "시스템 디렉토리에는 저장할 수 없습니다."
        
        return True, ""
    
    def check_cookies_file_security(self, cookies_file):
        """
        쿠키 파일 보안 검증
        
        Args:
            cookies_file (str): 쿠키 파일 경로
            
        Returns:
            tuple: (is_valid, warning_message)
        """
        import os
        
        if not cookies_file or not os.path.exists(cookies_file):
            return True, ""
        
        warnings = []
        
        # 파일 권한 확인 (Unix 계열)
        if hasattr(os, 'stat'):
            try:
                import stat
                file_stat = os.stat(cookies_file)
                mode = file_stat.st_mode
                
                # 다른 사용자가 읽을 수 있는지 확인
                if mode & stat.S_IROTH:
                    warnings.append("⚠️  쿠키 파일이 다른 사용자에게 읽기 가능합니다.")
                    self.logger.warning(f"쿠키 파일 권한 취약: {cookies_file}")
                
                # 그룹이 읽을 수 있는지 확인
                if mode & stat.S_IRGRP:
                    warnings.append("⚠️  쿠키 파일이 그룹에게 읽기 가능합니다.")
            except Exception as e:
                self.logger.error(f"파일 권한 확인 실패: {e}")
        
        # 파일 크기 확인 (비정상적으로 큰 파일)
        try:
            file_size = os.path.getsize(cookies_file)
            if file_size > 10 * 1024 * 1024:  # 10MB 이상
                warnings.append("⚠️  쿠키 파일 크기가 비정상적으로 큽니다.")
                self.logger.warning(f"쿠키 파일 크기 이상: {file_size} bytes")
        except Exception as e:
            self.logger.error(f"파일 크기 확인 실패: {e}")
        
        if warnings:
            return False, "\n".join(warnings)
        
        return True, ""

# 전역 검증기 인스턴스
_validator_instance = None

def get_validator():
    """전역 검증기 인스턴스 가져오기"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SecurityValidator()
    return _validator_instance
