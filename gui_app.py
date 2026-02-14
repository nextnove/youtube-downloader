import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from downloader import YouTubeDownloader
from config import Config
from security import get_validator
from history import get_history
from tkinter import ttk, filedialog, messagebox
import threading
import os
from downloader import YouTubeDownloader
from config import Config
from security import get_validator
from tkinter import ttk, filedialog, messagebox
import threading
import os
from downloader import YouTubeDownloader
from config import Config
from tkinter import ttk, filedialog, messagebox
import threading
import os
from downloader import YouTubeDownloader

class YouTubeDownloaderGUI:
    def __init__(self, root):
            self.root = root
            self.root.title("YouTube 다운로더")
            self.root.geometry("700x600")

            self.config = Config()

            # 다운로드 경로를 사용자 문서 폴더로 설정
            default_download_path = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube")
            self.downloader = YouTubeDownloader(download_path=default_download_path)

            self.validator = get_validator()
            self.history = get_history()
            self.setup_ui()
            self.load_settings()



    def format_error_message(self, error):
        """에러를 사용자 친화적인 메시지로 변환"""
        error_str = str(error).lower()

        # 일반적인 에러 패턴 매칭
        if '429' in error_str or 'too many requests' in error_str:
            return (
                "⚠️ YouTube가 너무 많은 요청을 감지했습니다.\n\n"
                "해결 방법:\n"
                "• 10-15분 후에 다시 시도하세요\n"
                "• 한 번에 하나의 영상만 다운로드하세요\n"
                "• 여러 영상 다운로드 시 충분한 간격을 두세요"
            )
        elif 'private video' in error_str or 'video unavailable' in error_str:
            return (
                "❌ 영상을 사용할 수 없습니다.\n\n"
                "가능한 원인:\n"
                "• 비공개 또는 삭제된 영상\n"
                "• 지역 제한이 있는 영상\n"
                "• 잘못된 URL"
            )
        elif 'url' in error_str and ('invalid' in error_str or 'not' in error_str):
            return (
                "❌ 올바르지 않은 URL입니다.\n\n"
                "확인사항:\n"
                "• YouTube URL이 맞는지 확인하세요\n"
                "• 전체 URL을 복사했는지 확인하세요"
            )
        elif 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
            return (
                "❌ 네트워크 연결 오류가 발생했습니다.\n\n"
                "해결 방법:\n"
                "• 인터넷 연결을 확인하세요\n"
                "• 잠시 후 다시 시도하세요\n"
                "• 방화벽 설정을 확인하세요"
            )
        elif 'no space' in error_str or 'disk full' in error_str:
            return (
                "❌ 저장 공간이 부족합니다.\n\n"
                "해결 방법:\n"
                "• 디스크 공간을 확보하세요\n"
                "• 다른 저장 위치를 선택하세요"
            )
        elif 'permission' in error_str or 'access denied' in error_str:
            return (
                "❌ 파일 저장 권한이 없습니다.\n\n"
                "해결 방법:\n"
                "• 다른 저장 위치를 선택하세요\n"
                "• 관리자 권한으로 실행하세요"
            )
        elif 'subtitle' in error_str or 'caption' in error_str:
            return (
                "⚠️ 자막을 다운로드할 수 없습니다.\n\n"
                "가능한 원인:\n"
                "• 해당 언어의 자막이 없습니다\n"
                "• '자막 확인' 버튼으로 사용 가능한 언어를 확인하세요"
            )
        else:
            # 알 수 없는 에러는 간단한 메시지만 표시
            return f"❌ 오류가 발생했습니다: {str(error)[:100]}"
    def load_settings(self):
        """저장된 설정을 불러와 UI에 적용합니다."""
        # 다운로드 경로
        download_path = self.config.get('download_path', 'downloads')
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, download_path)

        # 기본 품질
        default_quality = self.config.get('default_quality', 'best')
        self.quality_combo.set(default_quality)

        # 기본 자막 언어
        default_lang = self.config.get('default_subtitle_lang', 'ko')
        self.subtitle_lang_combo.set(default_lang)

        # 기본 다운로드 모드
        default_mode = self.config.get('default_download_mode', 'video_only')
        self.download_mode.set(default_mode)

    def save_current_settings(self):
        """현재 UI 설정을 저장합니다."""
        self.config.set('download_path', self.path_entry.get().strip())
        self.config.set('default_quality', self.quality_combo.get())
        self.config.set('default_subtitle_lang', self.subtitle_lang_combo.get())
        self.config.set('default_download_mode', self.download_mode.get())
    def save_settings_clicked(self):
        """설정 저장 버튼 클릭 시 호출"""
        self.save_current_settings()
        messagebox.showinfo("설정 저장", "현재 설정이 저장되었습니다.\n다음 실행 시 자동으로 적용됩니다.")
    def validate_url(self, url):
        """URL 유효성 검증"""
        is_valid, error_msg = self.validator.validate_youtube_url(url)
        if not is_valid:
            messagebox.showerror("URL 오류", error_msg)
            self.log_message(f"❌ URL 검증 실패: {error_msg}")
        return is_valid

    def validate_path(self, path):
        """다운로드 경로 유효성 검증"""
        is_valid, error_msg = self.validator.validate_download_path(path)
        if not is_valid:
            messagebox.showerror("경로 오류", error_msg)
            self.log_message(f"❌ 경로 검증 실패: {error_msg}")
        return is_valid
    def update_progress(self, d):
        """다운로드 진행률 업데이트"""
        if d['status'] == 'downloading':
            # 다운로드 중
            if 'total_bytes' in d or 'total_bytes_estimate' in d:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)

                if total > 0:
                    percent = (downloaded / total) * 100
                    self.progress_bar['value'] = percent

                    # 속도와 남은 시간 표시
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)

                    if speed:
                        speed_mb = speed / (1024 * 1024)
                        status_text = f"{percent:.1f}% - {speed_mb:.2f} MB/s"
                        if eta:
                            status_text += f" - 남은 시간: {eta}초"
                    else:
                        status_text = f"{percent:.1f}%"

                    self.progress_label.config(text=status_text)
            else:
                self.progress_label.config(text="다운로드 중...")

        elif d['status'] == 'finished':
            # 다운로드 완료
            self.progress_bar['value'] = 100
            self.progress_label.config(text="처리 중...")

        self.root.update_idletasks()

    def reset_progress(self):
        """진행률 초기화"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="대기 중")

    def cancel_download(self):
        """다운로드 취소"""
        if hasattr(self, 'cancel_flag') and self.cancel_flag:
            self.cancel_flag.set()
            self.log_message("⚠️ 다운로드 취소 요청...")
            self.cancel_button.config(state='disabled')
    def show_history(self):
        """다운로드 히스토리 창 표시"""
        history_window = tk.Toplevel(self.root)
        history_window.title("다운로드 히스토리")
        history_window.geometry("800x500")

        # 프레임
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 통계 표시
        stats = self.history.get_statistics()
        stats_text = (
            f"총 다운로드: {stats['total']}개 | "
            f"성공: {stats['success']}개 | "
            f"실패: {stats['failed']}개 | "
            f"취소: {stats['cancelled']}개 | "
            f"총 용량: {stats['total_size_mb']:.2f} MB"
        )
        ttk.Label(main_frame, text=stats_text).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # 트리뷰 (테이블)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 트리뷰 생성
        columns = ('시간', '제목', '모드', '품질', '상태')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)

        # 컬럼 설정
        tree.heading('시간', text='시간')
        tree.heading('제목', text='제목')
        tree.heading('모드', text='모드')
        tree.heading('품질', text='품질')
        tree.heading('상태', text='상태')

        tree.column('시간', width=150)
        tree.column('제목', width=300)
        tree.column('모드', width=100)
        tree.column('품질', width=80)
        tree.column('상태', width=80)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 데이터 로드
        for record in self.history.get_all_downloads():
            timestamp = record.get('timestamp', '')
            if timestamp:
                # ISO 형식을 읽기 쉬운 형식으로 변환
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass

            title = record.get('title', 'N/A')
            if len(title) > 40:
                title = title[:37] + '...'

            mode = record.get('mode', 'N/A')
            quality = record.get('quality', 'N/A') or 'N/A'
            status = record.get('status', 'N/A')

            # 상태에 따라 아이콘 추가
            status_icons = {
                'success': '✅',
                'failed': '❌',
                'cancelled': '⚠️'
            }
            status_display = f"{status_icons.get(status, '')} {status}"

            tree.insert('', tk.END, values=(timestamp, title, mode, quality, status_display))

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        def clear_history():
            if messagebox.askyesno("확인", "모든 히스토리를 삭제하시겠습니까?"):
                self.history.clear_history()
                history_window.destroy()
                messagebox.showinfo("완료", "히스토리가 삭제되었습니다.")

        ttk.Button(button_frame, text="히스토리 삭제", command=clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="닫기", command=history_window.destroy).pack(side=tk.LEFT, padx=5)

        # 그리드 가중치
        history_window.columnconfigure(0, weight=1)
        history_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)






    
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL 입력
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_entry = ttk.Combobox(main_frame, width=77)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 최근 URL 목록 로드
        recent_urls = self.config.get_recent_urls()
        if recent_urls:
            self.url_entry['values'] = recent_urls
        
        # 다운로드 경로
        ttk.Label(main_frame, text="다운로드 경로:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.path_entry = ttk.Entry(path_frame, width=60)
        self.path_entry.insert(0, "downloads")
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(path_frame, text="찾아보기", command=self.browse_path).grid(row=0, column=1, padx=(5, 0))
        
        # 다운로드 모드 선택
        ttk.Label(main_frame, text="다운로드 모드:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.download_mode = tk.StringVar(value="video_only")
        
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="비디오만", variable=self.download_mode, 
                       value="video_only").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="자막만", variable=self.download_mode, 
                       value="subs_only").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(mode_frame, text="비디오+자막", variable=self.download_mode, 
                       value="video_subs").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        # 자막 언어 설정
        subtitle_frame = ttk.Frame(main_frame)
        subtitle_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(subtitle_frame, text="자막 언어:").grid(row=0, column=0, sticky=tk.W)
        self.subtitle_lang_combo = ttk.Combobox(
            subtitle_frame, 
            values=['ko', 'en', 'ja', 'zh-Hans', 'zh-Hant', 'es', 'fr', 'de', 'ru', 'pt', 'it'], 
            width=15
        )
        self.subtitle_lang_combo.set('ko')
        self.subtitle_lang_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        ttk.Label(subtitle_frame, text="(한 번에 하나만 다운로드)").grid(row=0, column=2, padx=(10, 0), sticky=tk.W)
        
        # 품질 선택
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(quality_frame, text="비디오 품질:").grid(row=0, column=0, sticky=tk.W)
        self.quality_combo = ttk.Combobox(quality_frame, values=['best', 'worst', '720p', '480p', '360p'], width=15)
        self.quality_combo.set('best')
        self.quality_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(15, 0))
        
        self.info_button = ttk.Button(button_frame, text="정보 가져오기", command=self.get_info)
        self.info_button.grid(row=0, column=0, padx=(0, 10))
        
        self.check_subs_button = ttk.Button(button_frame, text="자막 확인", command=self.check_subtitles)
        self.check_subs_button.grid(row=0, column=1, padx=(0, 10))
        
        self.download_button = ttk.Button(button_frame, text="다운로드", command=self.download_video)
        self.download_button.grid(row=0, column=2, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="취소", command=self.cancel_download, state='disabled')
        self.cancel_button.grid(row=0, column=3, padx=(0, 10))
        
        self.settings_button = ttk.Button(button_frame, text="설정 저장", command=self.save_settings_clicked)
        self.settings_button.grid(row=0, column=4, padx=(0, 10))
        
        self.history_button = ttk.Button(button_frame, text="히스토리", command=self.show_history)
        self.history_button.grid(row=0, column=5)
        
        # 진행률 표시
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="대기 중")
        self.progress_label.grid(row=0, column=1, sticky=tk.W)
        
        progress_frame.columnconfigure(0, weight=1)
        
        # 정보 표시 영역
        ttk.Label(main_frame, text="로그:").grid(row=10, column=0, sticky=tk.W, pady=(15, 5))
        ttk.Label(main_frame, text="로그:").grid(row=9, column=0, sticky=tk.W, pady=(15, 5))
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.info_text = tk.Text(text_frame, height=10, width=80, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(11, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        path_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
    
    def browse_path(self):
        """다운로드 경로 선택"""
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
    
    def disable_buttons(self):
        """모든 버튼 비활성화"""
        self.info_button.config(state='disabled')
        self.check_subs_button.config(state='disabled')
        self.download_button.config(state='disabled')
        self.settings_button.config(state='disabled')
        self.cancel_button.config(state='normal')  # 취소 버튼만 활성화

    
    def enable_buttons(self):
        """모든 버튼 활성화"""
        self.info_button.config(state='normal')
        self.check_subs_button.config(state='normal')
        self.download_button.config(state='normal')
        self.settings_button.config(state='normal')
        self.cancel_button.config(state='disabled')  # 취소 버튼 비활성화

    
    def log_message(self, message):
        """로그 메시지를 텍스트 영역에 추가"""
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END)
        self.root.update()
    
    def check_subtitles(self):
        """사용 가능한 자막 확인"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력해주세요.")
            return

        # URL 검증
        if not self.validate_url(url):
            return

        self.info_text.delete(1.0, tk.END)
        self.log_message("자막 정보를 확인하는 중...")
        self.disable_buttons()  # 버튼 비활성화

        def check_subs_thread():
            try:
                subs_info = self.downloader.get_available_subtitles(url)
                if subs_info:
                    manual_subs = subs_info.get('manual_subtitles', [])
                    auto_subs = subs_info.get('auto_subtitles', [])

                    self.log_message("=== 사용 가능한 자막 ===")
                    self.log_message(f"수동 자막: {', '.join(manual_subs) if manual_subs else '없음'}")
                    self.log_message(f"자동 자막: {', '.join(auto_subs[:10]) if auto_subs else '없음'}")
                    if len(auto_subs) > 10:
                        self.log_message(f"... 외 {len(auto_subs) - 10}개 더")

                    self.log_message("\n추천 언어 코드:")
                    self.log_message("한국어: ko, 영어: en, 일본어: ja")
                    self.log_message("중국어: zh, 스페인어: es, 프랑스어: fr")
                else:
                    self.log_message("자막 정보를 가져올 수 없습니다.")
            except Exception as e:
                error_msg = self.format_error_message(e)
                self.log_message(error_msg)
            finally:
                self.enable_buttons()  # 완료 후 버튼 활성화

        threading.Thread(target=check_subs_thread, daemon=True).start()

    
    def get_info(self):
        """비디오 정보 가져오기"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력해주세요.")
            return

        # URL 검증
        if not self.validate_url(url):
            return

        self.info_text.delete(1.0, tk.END)
        self.log_message("비디오 정보를 가져오는 중...")
        self.disable_buttons()  # 버튼 비활성화

        def get_info_thread():
            try:
                info = self.downloader.get_video_info(url)
                if info:
                    self.log_message("=== 비디오 정보 ===")
                    self.log_message(f"제목: {info['title']}")
                    self.log_message(f"업로더: {info['uploader']}")
                    self.log_message(f"재생 시간: {info['duration']}초")
                    self.log_message(f"조회수: {info['view_count']:,}회")
                else:
                    self.log_message("비디오 정보를 가져올 수 없습니다.")
            except Exception as e:
                error_msg = self.format_error_message(e)
                self.log_message(error_msg)
            finally:
                self.enable_buttons()  # 완료 후 버튼 활성화

        threading.Thread(target=get_info_thread, daemon=True).start()

    
    def download_video(self):
        """비디오/자막 다운로드"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("경고", "YouTube URL을 입력해주세요.")
            return
        
        # URL 검증
        if not self.validate_url(url):
            return
        
        download_path = self.path_entry.get().strip()
        if not download_path:
            download_path = "downloads"
        
        # 경로 검증
        if not self.validate_path(download_path):
            return
        
        quality = self.quality_combo.get()
        mode = self.download_mode.get()
        
        # 자막 언어 (단일 선택)
        subtitle_lang = self.subtitle_lang_combo.get().strip()
        if not subtitle_lang:
            subtitle_lang = 'ko'  # 기본값
        subtitle_langs = [subtitle_lang]  # 리스트로 변환 (기존 코드 호환)
        
        # 다운로드 경로 설정
        self.downloader.download_path = download_path
        
        # 취소 플래그 초기화
        import threading
        self.cancel_flag = threading.Event()
        self.downloader.set_cancel_flag(self.cancel_flag)
        
        # 진행률 콜백 설정
        self.downloader.set_progress_callback(self.update_progress)
        
        # 진행률 초기화
        self.reset_progress()
        
        # 다운로드 시작 메시지
        mode_messages = {
            'video_only': "비디오 다운로드를 시작합니다...",
            'subs_only': f"자막 다운로드를 시작합니다... (언어: {subtitle_lang})",
            'video_subs': f"비디오+자막 다운로드를 시작합니다... (언어: {subtitle_lang})"
        }
        
        self.info_text.delete(1.0, tk.END)
        self.log_message(mode_messages.get(mode, "다운로드를 시작합니다..."))
        self.disable_buttons()  # 버튼 비활성화
        
        def download_thread():
            try:
                success = False
                video_title = "Unknown"
                
                # 비디오 정보 가져오기 (제목 기록용)
                try:
                    info = self.downloader.get_video_info(url)
                    if info:
                        video_title = info.get('title', 'Unknown')
                except:
                    pass
                
                if mode == 'video_only':
                    success = self.downloader.download_video(url, quality)
                elif mode == 'subs_only':
                    self.log_message(f"요청된 자막 언어: {subtitle_langs}")
                    success = self.downloader.download_subtitles(url, subtitle_langs)
                elif mode == 'video_subs':
                    self.log_message(f"요청된 자막 언어: {subtitle_langs}")
                    success = self.downloader.download_video_with_subtitles(url, quality, subtitle_langs)
                
                # 히스토리에 기록
                if self.cancel_flag.is_set():
                    self.log_message("❌ 다운로드가 취소되었습니다.")
                    self.reset_progress()
                    self.history.add_download(
                        url=url,
                        title=video_title,
                        mode=mode,
                        quality=quality if mode != 'subs_only' else None,
                        subtitle_langs=subtitle_langs if mode != 'video_only' else None,
                        status='cancelled'
                    )
                elif success:
                    self.log_message("✅ 다운로드 완료!")
                    self.progress_label.config(text="완료!")
                    # URL을 최근 목록에 추가
                    self.config.add_recent_url(url)
                    # 히스토리에 기록
                    self.history.add_download(
                        url=url,
                        title=video_title,
                        mode=mode,
                        quality=quality if mode != 'subs_only' else None,
                        subtitle_langs=subtitle_langs if mode != 'video_only' else None,
                        file_path=download_path,
                        status='success'
                    )
                    
                    # 다운로드 완료 메시지 (폴더 열기 옵션)
                    result = messagebox.askyesno(
                        "다운로드 완료", 
                        f"다운로드가 완료되었습니다!\n\n저장 경로:\n{download_path}\n\n폴더를 여시겠습니까?"
                    )
                    if result:
                        self.open_download_folder(download_path)
                else:
                    self.log_message("❌ 다운로드 실패")
                    self.reset_progress()
                    # 히스토리에 기록
                    self.history.add_download(
                        url=url,
                        title=video_title,
                        mode=mode,
                        quality=quality if mode != 'subs_only' else None,
                        subtitle_langs=subtitle_langs if mode != 'video_only' else None,
                        status='failed'
                    )
                    messagebox.showerror("오류", "다운로드에 실패했습니다.")
            except Exception as e:
                error_msg = self.format_error_message(e)
                self.log_message(error_msg)
                self.reset_progress()
                messagebox.showerror("오류", error_msg)
            finally:
                self.enable_buttons()  # 완료 후 버튼 활성화
        
        threading.Thread(target=download_thread, daemon=True).start()

    def check_ffmpeg(self):
        """FFmpeg 설치 여부 확인 및 안내"""
        import subprocess
        import platform
        
        try:
            # ffmpeg 명령어 실행 시도
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True,
                         timeout=5)
            # FFmpeg 설치됨
            return True
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # FFmpeg 미설치 - 안내 메시지 표시
            self.show_ffmpeg_install_guide()
            return False
    
    def show_ffmpeg_install_guide(self):
        """FFmpeg 설치 안내 창 표시"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            install_guide = (
                "FFmpeg가 설치되어 있지 않습니다.\n\n"
                "FFmpeg는 고화질 영상 다운로드와 자막 병합에 필요합니다.\n"
                "설치하지 않아도 프로그램은 작동하지만, 일부 기능이 제한됩니다.\n\n"
                "【 Windows 설치 방법 】\n\n"
                "1. Chocolatey 사용 (권장):\n"
                "   • PowerShell(관리자)에서 실행:\n"
                "   • choco install ffmpeg\n\n"
                "2. 수동 설치:\n"
                "   • https://github.com/BtbN/FFmpeg-Builds/releases\n"
                "   • ffmpeg-master-latest-win64-gpl.zip 다운로드\n"
                "   • 압축 해제 후 bin 폴더를 PATH에 추가\n\n"
                "3. Scoop 사용:\n"
                "   • scoop install ffmpeg"
            )
        elif system == "Darwin":  # macOS
            install_guide = (
                "FFmpeg가 설치되어 있지 않습니다.\n\n"
                "FFmpeg는 고화질 영상 다운로드와 자막 병합에 필요합니다.\n"
                "설치하지 않아도 프로그램은 작동하지만, 일부 기능이 제한됩니다.\n\n"
                "【 macOS 설치 방법 】\n\n"
                "터미널에서 실행:\n"
                "brew install ffmpeg"
            )
        else:  # Linux
            install_guide = (
                "FFmpeg가 설치되어 있지 않습니다.\n\n"
                "FFmpeg는 고화질 영상 다운로드와 자막 병합에 필요합니다.\n"
                "설치하지 않아도 프로그램은 작동하지만, 일부 기능이 제한됩니다.\n\n"
                "【 Linux 설치 방법 】\n\n"
                "Ubuntu/Debian:\n"
                "sudo apt update && sudo apt install ffmpeg\n\n"
                "Fedora:\n"
                "sudo dnf install ffmpeg\n\n"
                "Arch Linux:\n"
                "sudo pacman -S ffmpeg"
            )
        
        messagebox.showinfo("FFmpeg 설치 안내", install_guide)

    def open_download_folder(self, path):
            """다운로드 폴더 열기"""
            import subprocess
            import platform

            try:
                folder_path = os.path.dirname(path) if os.path.isfile(path) else path

                system = platform.system()
                if system == "Windows":
                    os.startfile(folder_path)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", folder_path])
                else:  # Linux
                    subprocess.run(["xdg-open", folder_path])
            except Exception as e:
                messagebox.showerror("오류", f"폴더를 열 수 없습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()