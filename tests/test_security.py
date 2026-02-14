import unittest
import os
import tempfile
from security import SecurityValidator

class TestSecurityValidator(unittest.TestCase):
    """SecurityValidator 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행"""
        self.validator = SecurityValidator()
    
    def test_valid_youtube_urls(self):
        """유효한 YouTube URL 테스트"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                is_valid, error_msg = self.validator.validate_youtube_url(url)
                self.assertTrue(is_valid, f"URL should be valid: {url}, Error: {error_msg}")
    
    def test_invalid_youtube_urls(self):
        """유효하지 않은 YouTube URL 테스트"""
        invalid_urls = [
            "",  # 빈 문자열
            "not a url",  # URL 형식 아님
            "https://evil.com/watch?v=dQw4w9WgXcQ",  # 다른 도메인
            "ftp://youtube.com/watch?v=dQw4w9WgXcQ",  # 잘못된 프로토콜
            "https://www.youtube.com/",  # 비디오 ID 없음
            "https://www.youtube.com/channel/UCtest",  # 채널 URL
            "javascript:alert('xss')",  # XSS 시도
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                is_valid, error_msg = self.validator.validate_youtube_url(url)
                self.assertFalse(is_valid, f"URL should be invalid: {url}")
                self.assertIsNotNone(error_msg)
    
    def test_extract_video_id(self):
        """비디오 ID 추출 테스트"""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                video_id = self.validator.extract_video_id(url)
                self.assertEqual(video_id, expected_id)
    
    def test_sanitize_filename(self):
        """파일명 정제 테스트"""
        test_cases = [
            ("normal_file.mp4", "normal_file.mp4"),
            ("file<with>bad:chars.mp4", "file_with_bad_chars.mp4"),
            ("file/with\\slashes.mp4", "file_with_slashes.mp4"),
            ("file|with*wildcards?.mp4", "file_with_wildcards_.mp4"),
            ("a" * 300 + ".mp4", "a" * 251 + ".mp4"),  # 길이 제한
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                sanitized = self.validator.sanitize_filename(original)
                self.assertEqual(sanitized, expected)
    
    def test_validate_download_path_safe(self):
        """안전한 다운로드 경로 테스트"""
        safe_paths = [
            "downloads",
            "./downloads",
            "my_videos",
            "/home/user/downloads",
            "C:\\Users\\User\\Downloads",
        ]
        
        for path in safe_paths:
            with self.subTest(path=path):
                is_valid, error_msg = self.validator.validate_download_path(path)
                self.assertTrue(is_valid, f"Path should be valid: {path}, Error: {error_msg}")
    
    def test_validate_download_path_dangerous(self):
        """위험한 다운로드 경로 테스트"""
        import os
        
        dangerous_paths = [
            "../../../etc/passwd",  # 경로 순회 공격
            "downloads/../../../etc",  # 경로 순회 공격
        ]
        
        # OS별 위험 경로 추가
        if os.name == 'nt':  # Windows
            dangerous_paths.extend([
                "C:\\Windows\\System32",
                "C:\\Program Files",
            ])
        else:  # Unix-like
            dangerous_paths.extend([
                "/etc",
                "/usr/bin",
                "/sys",
            ])
        
        for path in dangerous_paths:
            with self.subTest(path=path):
                is_valid, error_msg = self.validator.validate_download_path(path)
                self.assertFalse(is_valid, f"Path should be invalid: {path}")
                self.assertIsNotNone(error_msg)
    
    def test_check_cookies_file_security(self):
        """쿠키 파일 보안 검증 테스트"""
        # 임시 쿠키 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# Netscape HTTP Cookie File\n")
            temp_file = f.name
        
        try:
            # 파일이 존재하면 검증 수행
            is_secure, warning = self.validator.check_cookies_file_security(temp_file)
            # 결과는 시스템에 따라 다를 수 있음
            self.assertIsInstance(is_secure, bool)
            self.assertIsInstance(warning, str)
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_check_cookies_file_nonexistent(self):
        """존재하지 않는 쿠키 파일 테스트"""
        is_secure, warning = self.validator.check_cookies_file_security("nonexistent.txt")
        self.assertTrue(is_secure)
        self.assertEqual(warning, "")
    
    def test_url_validation_with_none(self):
        """None URL 테스트"""
        is_valid, error_msg = self.validator.validate_youtube_url(None)
        self.assertFalse(is_valid)
        self.assertIn("비어있거나", error_msg)
    
    def test_url_validation_with_whitespace(self):
        """공백이 포함된 URL 테스트"""
        url = "  https://www.youtube.com/watch?v=dQw4w9WgXcQ  "
        is_valid, error_msg = self.validator.validate_youtube_url(url)
        self.assertTrue(is_valid)
    
    def test_path_validation_with_none(self):
        """None 경로 테스트"""
        is_valid, error_msg = self.validator.validate_download_path(None)
        self.assertFalse(is_valid)
        self.assertIn("비어있거나", error_msg)
    
    def test_path_validation_with_empty_string(self):
        """빈 문자열 경로 테스트"""
        is_valid, error_msg = self.validator.validate_download_path("")
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()
