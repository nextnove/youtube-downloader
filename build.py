# build.py - PyInstaller 빌드 스크립트
import PyInstaller.__main__
import sys
import os

def check_ffmpeg():
    """FFmpeg 바이너리 존재 확인"""
    ffmpeg_dir = 'ffmpeg'
    ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg')
    
    if not os.path.exists(ffmpeg_exe):
        print(f"⚠️  경고: FFmpeg 바이너리를 찾을 수 없습니다: {ffmpeg_exe}")
        print(f"   FFmpeg 없이 빌드하면 일부 기능(고화질 다운로드, 자막 병합)이 작동하지 않습니다.")
        return False
    
    file_size = os.path.getsize(ffmpeg_exe) / (1024 * 1024)  # MB
    print(f"✅ FFmpeg 발견: {ffmpeg_exe} ({file_size:.1f} MB)")
    return True

def build():
    """PyInstaller로 실행 파일 빌드"""
    
    # FFmpeg 확인
    has_ffmpeg = check_ffmpeg()
    
    # 빌드 옵션
    options = [
        'main.py',                          # 진입점
        '--name=YouTube-Downloader',        # 실행 파일 이름
        '--onefile',                        # 단일 파일로 빌드
        '--windowed',                       # GUI 모드 (콘솔 창 숨김)
        '--icon=NONE',                      # 아이콘 (없으면 NONE)
        '--add-data=downloader.py;.',       # 추가 파일
        '--add-data=gui_app.py;.',          # 추가 파일
        '--hidden-import=yt_dlp',           # 숨겨진 import
        '--hidden-import=tkinter',          # tkinter
        '--collect-all=yt_dlp',             # yt-dlp 전체 수집
        '--noconfirm',                      # 확인 없이 덮어쓰기
    ]
    
    # FFmpeg 바이너리 포함 (있는 경우)
    if has_ffmpeg:
        if sys.platform == 'win32':
            options.append('--add-binary=ffmpeg/ffmpeg.exe;.')
        else:
            options.append('--add-binary=ffmpeg/ffmpeg;.')
        print("📦 FFmpeg를 실행 파일에 포함합니다...")
    
    print("\n🚀 PyInstaller 빌드 시작...")
    print(f"옵션: {' '.join(options)}")
    
    PyInstaller.__main__.run(options)
    
    print("\n✅ 빌드 완료!")
    print(f"실행 파일 위치: dist/YouTube-Downloader{'.exe' if sys.platform == 'win32' else ''}")
    
    if has_ffmpeg:
        print("✅ FFmpeg가 포함되어 있습니다. 사용자는 별도 설치가 필요 없습니다.")
    else:
        print("⚠️  FFmpeg가 포함되지 않았습니다. 사용자가 별도로 설치해야 합니다.")

if __name__ == "__main__":
    build()
