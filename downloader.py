import yt_dlp
import os
import sys
from logger import get_logger
from security import get_validator
import os
import sys
from logger import get_logger
import os
import sys

class YouTubeDownloader:
    def __init__(self, download_path="downloads", cookies_file=None):
        self.download_path = download_path
        self.cookies_file = cookies_file or self._find_cookies()
        self.logger = get_logger()
        self.validator = get_validator()

        # 다운로드 폴더가 없으면 생성
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            self.logger.info(f"다운로드 폴더 생성: {download_path}")

        if self.cookies_file and os.path.exists(self.cookies_file):
            print(f"쿠키 파일 발견: {self.cookies_file}")
            self.logger.info(f"쿠키 파일 사용: {self.cookies_file}")

            # 쿠키 파일 보안 검증
            is_secure, warning = self.validator.check_cookies_file_security(self.cookies_file)
            if not is_secure:
                # 이모지 제거 (Windows 콘솔 호환성)
                warning_clean = warning.replace('⚠️', '[경고]')
                print(warning_clean)
                self.logger.warning(f"쿠키 파일 보안 경고: {warning}")


    
    def _find_cookies(self):
        """쿠키 파일 자동 검색"""
        possible_locations = [
            'cookies.txt',
            os.path.join(os.path.dirname(__file__), 'cookies.txt'),
            os.path.expanduser('~/cookies.txt'),
        ]
        
        for location in possible_locations:
            if os.path.exists(location):
                return location
        return None
    
    def _get_base_ydl_opts(self):
        """기본 yt-dlp 옵션"""
        opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
        }

        # PyInstaller 대응 FFmpeg 경로 처리
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        if os.name == 'nt':
            ffmpeg_name = "ffmpeg.exe"
        else:
            ffmpeg_name = "ffmpeg"

        ffmpeg_path = os.path.join(base_path, ffmpeg_name)

        if os.path.exists(ffmpeg_path):
            opts['ffmpeg_location'] = ffmpeg_path
        
        # Node.js 경로 자동 감지 및 설정
        import shutil
        node_path = shutil.which('node')
        if node_path:
            # Node.js를 찾았으면 명시적으로 지정
            opts['extractor_args'] = {'youtube': {'player_client': ['android']}}
        
        # 쿠키 파일이 있으면 추가
        if self.cookies_file and os.path.exists(self.cookies_file):
            opts['cookiefile'] = self.cookies_file
        
        return opts
    def set_progress_callback(self, callback):
        """
        진행률 콜백 함수 설정

        Args:
            callback: 진행률 정보를 받을 콜백 함수
                     callback(progress_dict) 형태
        """
        self.progress_callback = callback

    def set_cancel_flag(self, cancel_flag):
        """
        취소 플래그 설정

        Args:
            cancel_flag: threading.Event 객체
        """
        self.cancel_flag = cancel_flag

    def _progress_hook(self, d):
        """yt-dlp 진행률 훅"""
        if hasattr(self, 'cancel_flag') and self.cancel_flag and self.cancel_flag.is_set():
            raise Exception("사용자가 다운로드를 취소했습니다.")

        if hasattr(self, 'progress_callback') and self.progress_callback:
            self.progress_callback(d)

    
    def download_video(self, url, quality='best'):
        """
        YouTube 비디오를 다운로드합니다.

        Args:
            url (str): YouTube 비디오 URL
            quality (str): 비디오 품질 ('best', 'worst', '720p', '480p' 등)
        """
        # 품질 설정을 더 유연한 포맷으로 변환
        format_map = {
            'best': 'bv*+ba/b',  # 가장 호환성 좋은 포맷
            'worst': 'worst',
            '720p': 'bv*[height<=720]+ba/b[height<=720]',
            '480p': 'bv*[height<=480]+ba/b[height<=480]',
            '360p': 'bv*[height<=360]+ba/b[height<=360]',
        }

        ydl_opts = self._get_base_ydl_opts()
        ydl_opts['format'] = format_map.get(quality, format_map['best'])

        # 진행률 훅 추가
        if hasattr(self, 'progress_callback') and self.progress_callback:
            ydl_opts['progress_hooks'] = [self._progress_hook]

        try:
            self.logger.log_download_start(url, 'video', quality=quality)
            print(f"다운로드 시작: {url}")
            print(f"사용 포맷: {format_map.get(quality, format_map['best'])}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            print("다운로드 완료!")
            self.logger.log_download_success(url, 'video')
            return True
        except Exception as e:
            error_msg = str(e)
            if "취소" in error_msg:
                print("다운로드가 취소되었습니다.")
                self.logger.info(f"다운로드 취소 - URL: {url}")
            else:
                print(f"다운로드 오류: {error_msg}")
                self.logger.log_download_failure(url, 'video', error_msg)
                import traceback
                traceback.print_exc()
            return False


    
    def get_video_info(self, url):
        """비디오 정보를 가져옵니다."""
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts['quiet'] = True
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'N/A'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'N/A'),
                    'view_count': info.get('view_count', 0)
                }
        except Exception as e:
            print(f"정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    def _find_available_subtitle_languages(self, url, requested_langs):
        """
        요청한 언어 중 사용 가능한 자막 언어를 찾습니다.

        Args:
            url (str): YouTube 비디오 URL
            requested_langs (list): 요청한 언어 코드 리스트

        Returns:
            tuple: (found_langs, available_subs, available_auto_subs)
        """
        info_opts = self._get_base_ydl_opts()
        info_opts['quiet'] = True

        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            available_subs = info.get('subtitles', {})
            available_auto_subs = info.get('automatic_captions', {})

            print(f"사용 가능한 수동 자막: {list(available_subs.keys())}")
            print(f"사용 가능한 자동 자막: {list(available_auto_subs.keys())[:10]}")

            # 요청한 언어가 있는지 확인
            found_langs = []
            for lang in requested_langs:
                if lang in available_subs or lang in available_auto_subs:
                    found_langs.append(lang)

            # 요청한 언어가 없으면 대체 언어 찾기
            if not found_langs:
                print(f"⚠️  경고: 요청한 언어 {requested_langs} 중 사용 가능한 자막이 없습니다.")

                all_available = list(set(list(available_subs.keys()) + list(available_auto_subs.keys())))
                if all_available:
                    print(f"사용 가능한 언어: {all_available[:10]}")

                    # 언어 변형 자동 감지
                    suggested_langs = []
                    for req_lang in requested_langs:
                        variants = [l for l in all_available if l.startswith(req_lang)]
                        if variants:
                            suggested_langs.extend(variants[:1])
                            print(f"💡 {req_lang} 대체: {variants}")

                    if suggested_langs:
                        print(f"대체 언어로 다운로드 시도: {suggested_langs}")
                        found_langs = suggested_langs

            return found_langs, available_subs, available_auto_subs

    def _download_subtitle_by_language(self, url, lang):
        """
        특정 언어의 자막을 다운로드합니다.

        Args:
            url (str): YouTube 비디오 URL
            lang (str): 언어 코드

        Returns:
            bool: 성공 여부
        """
        sub_opts = self._get_base_ydl_opts()
        sub_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'skip_download': True,
            'subtitlesformat': 'srt',
            'sleep_interval': 3,
            'max_sleep_interval': 5,
            'sleep_interval_subtitles': 3,
        })

        try:
            with yt_dlp.YoutubeDL(sub_opts) as ydl:
                ydl.download([url])
                print(f"✅ '{lang}' 자막 다운로드 완료!")
                return True
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'Too Many Requests' in error_msg:
                print(f"⚠️  '{lang}' 자막: 요청 제한에 걸림 (건너뜀)")
            else:
                print(f"⚠️  '{lang}' 자막 다운로드 실패: {error_msg}")
            return False

    
    def download_subtitles(self, url, languages=['ko', 'en']):
        """
        YouTube 비디오의 자막을 다운로드합니다.

        Args:
            url (str): YouTube 비디오 URL
            languages (list): 다운로드할 언어 코드 리스트
        """
        try:
            self.logger.log_download_start(url, 'subtitles', subtitle_langs=languages)
            print(f"자막 다운로드 시작: {url}")
            print(f"요청 언어: {languages}")

            # 사용 가능한 자막 언어 찾기
            found_langs, _, _ = self._find_available_subtitle_languages(url, languages)

            if not found_langs:
                print("❌ 이 영상에는 요청한 언어의 자막이 없습니다.")
                self.logger.warning(f"자막 없음 - URL: {url}, 요청 언어: {languages}")
                return False

            print(f"다운로드할 언어: {found_langs}")

            # 언어별로 순차 다운로드 (429 오류 방지)
            success_count = 0
            for lang in found_langs:
                print(f"\n'{lang}' 자막 다운로드 중...")

                if self._download_subtitle_by_language(url, lang):
                    success_count += 1

                    # 다음 언어 다운로드 전 대기
                    if lang != found_langs[-1]:
                        import time
                        print("다음 자막까지 3초 대기...")
                        time.sleep(3)

            if success_count > 0:
                print(f"\n✅ 총 {success_count}/{len(found_langs)}개 언어 다운로드 완료!")
                self.logger.log_download_success(url, f'subtitles ({success_count}/{len(found_langs)})')
                return True
            else:
                print("\n❌ 자막 다운로드 실패")
                self.logger.log_download_failure(url, 'subtitles', '모든 언어 다운로드 실패')
                return False

        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            if '429' in error_msg or 'Too Many Requests' in error_msg:
                print("\n⚠️  YouTube가 너무 많은 요청을 감지했습니다.")
                print("해결 방법:")
                print("1. 잠시 후에 다시 시도하세요")
                print("2. 한 번에 하나의 언어만 다운로드하세요 (예: ko만)")
                print("3. 여러 영상을 연속으로 다운로드하지 마세요")
            print(f"yt-dlp 자막 다운로드 오류: {error_msg}")
            self.logger.log_download_failure(url, 'subtitles', error_msg)
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"예상치 못한 자막 다운로드 오류: {str(e)}")
            self.logger.log_download_failure(url, 'subtitles', str(e))
            import traceback
            traceback.print_exc()
            return False


    
    def get_available_subtitles(self, url):
        """사용 가능한 자막 언어 목록을 가져옵니다."""
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'quiet': True,
            'no_warnings': True,
        })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("자막 정보 추출 중...")
                info = ydl.extract_info(url, download=False)
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                print(f"수동 자막: {len(subtitles)}개")
                print(f"자동 자막: {len(automatic_captions)}개")
                
                return {
                    'manual_subtitles': list(subtitles.keys()),
                    'auto_subtitles': list(automatic_captions.keys())
                }
        except yt_dlp.DownloadError as e:
            print(f"yt-dlp 다운로드 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"예상치 못한 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def download_video_with_subtitles(self, url, quality='best', subtitle_langs=['ko', 'en']):
        """
        비디오와 자막을 함께 다운로드합니다.

        Args:
            url (str): YouTube 비디오 URL
            quality (str): 비디오 품질
            subtitle_langs (list): 자막 언어 코드 리스트
        """
        # 품질 설정을 더 유연한 포맷으로 변환
        format_map = {
            'best': 'bv*+ba/b',
            'worst': 'worst',
            '720p': 'bv*[height<=720]+ba/b[height<=720]',
            '480p': 'bv*[height<=480]+ba/b[height<=480]',
            '360p': 'bv*[height<=360]+ba/b[height<=360]',
        }

        # 1단계: 비디오만 다운로드
        print(f"1단계: 비디오 다운로드")
        video_opts = self._get_base_ydl_opts()
        video_opts.update({
            'format': format_map.get(quality, format_map['best']),
        })

        try:
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                print(f"비디오 다운로드 시작: {url}")
                print(f"사용 포맷: {format_map.get(quality, format_map['best'])}")
                ydl.download([url])
                print("✅ 비디오 다운로드 완료!")
        except Exception as e:
            print(f"❌ 비디오 다운로드 실패: {str(e)}")
            return False

        # 2단계: 자막 다운로드
        print(f"\n2단계: 자막 다운로드")
        print(f"요청 자막 언어: {subtitle_langs}")

        try:
            # 사용 가능한 자막 언어 찾기
            found_langs, _, _ = self._find_available_subtitle_languages(url, subtitle_langs)

            if not found_langs:
                print("⚠️  사용 가능한 자막이 없습니다.")
                print("비디오만 다운로드되었습니다.")
                return True  # 비디오는 성공했으므로 True

            # 언어별로 순차 다운로드
            success_count = 0
            for lang in found_langs:
                print(f"'{lang}' 자막 다운로드 중...")

                if self._download_subtitle_by_language(url, lang):
                    success_count += 1

                    # 다음 언어 전 대기
                    if lang != found_langs[-1]:
                        import time
                        print("3초 대기...")
                        time.sleep(3)

            print(f"\n✅ 완료! 비디오 + {success_count}/{len(found_langs)}개 언어 자막")
            return True

        except Exception as e:
            print(f"⚠️  자막 다운로드 중 오류: {str(e)}")
            print("비디오는 성공적으로 다운로드되었습니다.")
            return True  # 비디오는 성공


def main():
    """간단한 CLI 테스트"""
    downloader = YouTubeDownloader()
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python downloader.py <YouTube_URL>                    # 비디오 다운로드")
        print("  python downloader.py <YouTube_URL> --subs-only       # 자막만 다운로드")
        print("  python downloader.py <YouTube_URL> --with-subs       # 비디오+자막 다운로드")
        print("  python downloader.py <YouTube_URL> --check-subs      # 사용가능한 자막 확인")
        return
    
    url = sys.argv[1]
    
    # 자막 정보 확인
    if len(sys.argv) > 2 and sys.argv[2] == '--check-subs':
        subs_info = downloader.get_available_subtitles(url)
        if subs_info:
            print("\n사용 가능한 자막:")
            print(f"수동 자막: {', '.join(subs_info['manual_subtitles']) if subs_info['manual_subtitles'] else '없음'}")
            print(f"자동 자막: {', '.join(subs_info['auto_subtitles']) if subs_info['auto_subtitles'] else '없음'}")
        return
    
    # 비디오 정보 출력
    info = downloader.get_video_info(url)
    if info:
        print(f"\n제목: {info['title']}")
        print(f"업로더: {info['uploader']}")
        print(f"재생 시간: {info['duration']}초")
        print(f"조회수: {info['view_count']:,}")
        print()
    
    # 다운로드 모드 결정
    if len(sys.argv) > 2:
        if sys.argv[2] == '--subs-only':
            # 자막만 다운로드
            print("자막만 다운로드합니다...")
            downloader.download_subtitles(url)
        elif sys.argv[2] == '--with-subs':
            # 비디오+자막 다운로드
            print("비디오와 자막을 함께 다운로드합니다...")
            downloader.download_video_with_subtitles(url)
        else:
            # 기본 비디오 다운로드
            downloader.download_video(url)
    else:
        # 기본 비디오 다운로드
        downloader.download_video(url)

if __name__ == "__main__":
    main()