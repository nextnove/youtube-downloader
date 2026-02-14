import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from downloader import YouTubeDownloader

class TestYouTubeDownloader(unittest.TestCase):
    """YouTubeDownloader 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행"""
        # 임시 다운로드 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = YouTubeDownloader(download_path=self.temp_dir)
    
    def tearDown(self):
        """각 테스트 후에 실행"""
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertEqual(self.downloader.download_path, self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_download_path_creation(self):
        """다운로드 경로 자동 생성 테스트"""
        new_path = os.path.join(self.temp_dir, 'new_downloads')
        downloader = YouTubeDownloader(download_path=new_path)
        self.assertTrue(os.path.exists(new_path))
    
    def test_find_available_subtitle_languages(self):
        """자막 언어 찾기 테스트 (모킹)"""
        mock_info = {
            'subtitles': {'ko': [], 'en': []},
            'automatic_captions': {'ja': [], 'zh': []}
        }
        
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_info
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            found_langs, subs, auto_subs = self.downloader._find_available_subtitle_languages(
                'https://youtube.com/watch?v=test',
                ['ko', 'en']
            )
            
            self.assertIn('ko', found_langs)
            self.assertIn('en', found_langs)
            self.assertEqual(len(subs), 2)
    
    def test_get_base_ydl_opts(self):
        """기본 yt-dlp 옵션 테스트"""
        opts = self.downloader._get_base_ydl_opts()
        
        self.assertIn('outtmpl', opts)
        self.assertIn(self.temp_dir, opts['outtmpl'])
    
    def test_cookies_file_detection(self):
        """쿠키 파일 감지 테스트"""
        # 임시 쿠키 파일 생성
        cookie_file = os.path.join(self.temp_dir, 'cookies.txt')
        with open(cookie_file, 'w') as f:
            f.write('# Test cookies')
        
        downloader = YouTubeDownloader(
            download_path=self.temp_dir,
            cookies_file=cookie_file
        )
        
        self.assertEqual(downloader.cookies_file, cookie_file)
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info(self, mock_ydl):
        """비디오 정보 가져오기 테스트"""
        mock_info = {
            'title': '테스트 비디오',
            'duration': 120,
            'uploader': '테스트 업로더',
            'view_count': 1000
        }
        
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = mock_info
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        info = self.downloader.get_video_info('https://youtube.com/watch?v=test')
        
        self.assertEqual(info['title'], '테스트 비디오')
        self.assertEqual(info['duration'], 120)
        self.assertEqual(info['uploader'], '테스트 업로더')
        self.assertEqual(info['view_count'], 1000)
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_available_subtitles(self, mock_ydl):
        """사용 가능한 자막 목록 가져오기 테스트"""
        mock_info = {
            'subtitles': {'ko': [], 'en': []},
            'automatic_captions': {'ja': [], 'zh': []}
        }
        
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = mock_info
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        subs_info = self.downloader.get_available_subtitles('https://youtube.com/watch?v=test')
        
        self.assertIn('ko', subs_info['manual_subtitles'])
        self.assertIn('en', subs_info['manual_subtitles'])
        self.assertIn('ja', subs_info['auto_subtitles'])
        self.assertIn('zh', subs_info['auto_subtitles'])

class TestYouTubeDownloaderIntegration(unittest.TestCase):
    """통합 테스트 (실제 다운로드는 하지 않음)"""
    
    def setUp(self):
        """각 테스트 전에 실행"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = YouTubeDownloader(download_path=self.temp_dir)
    
    def tearDown(self):
        """각 테스트 후에 실행"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_ydl):
        """비디오 다운로드 성공 시나리오"""
        mock_instance = MagicMock()
        mock_instance.download.return_value = None
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = self.downloader.download_video('https://youtube.com/watch?v=test', 'best')
        self.assertTrue(result)
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_video_failure(self, mock_ydl):
        """비디오 다운로드 실패 시나리오"""
        mock_instance = MagicMock()
        mock_instance.download.side_effect = Exception("다운로드 실패")
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = self.downloader.download_video('https://youtube.com/watch?v=test', 'best')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
