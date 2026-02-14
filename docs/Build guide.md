# PyInstaller 빌드 가이드

PyInstaller를 사용하여 Windows/Mac/Linux용 실행 파일을 만드는 방법입니다.

## 빌드 환경 준비

### 1. PyInstaller 설치

```bash
# UV 사용
uv add --dev pyinstaller

# 또는 일반 pip
pip install pyinstaller
```

### 2. FFmpeg 준비 (중요!)

실행 파일에 FFmpeg를 포함시키려면 static 빌드된 FFmpeg 바이너리가 필요합니다.

#### Windows

1. [Gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/) 접속
2. 다음 중 하나 다운로드:
   - `ffmpeg-git-essentials.7z` (약 80MB, 권장)
   - `ffmpeg-git-full.7z` (약 120MB, 전체 기능)
3. 7-Zip으로 압축 해제
4. `bin/ffmpeg.exe` 파일 찾기
5. 프로젝트 루트에 `ffmpeg/` 폴더 생성
6. `ffmpeg.exe`를 `ffmpeg/` 폴더에 복사

```cmd
mkdir ffmpeg
copy "압축해제경로\ffmpeg-git-essentials\bin\ffmpeg.exe" ffmpeg\
```

**중요**: Gyan.dev의 빌드는 static 빌드로 DLL 의존성 없이 작동합니다!

#### macOS

```bash
# Homebrew로 설치
brew install ffmpeg

# 바이너리 복사
mkdir ffmpeg
cp $(which ffmpeg) ffmpeg/
```

#### Linux

```bash
# 설치
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora

# 바이너리 복사
mkdir ffmpeg
cp $(which ffmpeg) ffmpeg/
```

## 빌드 방법

### 방법 1: 빌드 스크립트 사용 (권장)

```bash
uv run python build.py
```

또는

```bash
python build.py
```

**빌드 스크립트가 자동으로:**
- FFmpeg 존재 여부 확인
- FFmpeg를 실행 파일에 포함
- 최적화된 옵션으로 빌드

### 방법 2: 직접 PyInstaller 명령 실행

```bash
pyinstaller --onefile --windowed --name YouTube-Downloader \
  --add-binary="ffmpeg/ffmpeg.exe;." \
  --hidden-import=yt_dlp --hidden-import=tkinter \
  --collect-all=yt_dlp \
  main.py
```

## 빌드 결과

빌드가 완료되면 다음 위치에 파일이 생성됩니다:

```
dist/
└── YouTube-Downloader.exe  (Windows, 약 107MB)
    YouTube-Downloader      (Mac/Linux)
```

**파일 크기:**
- FFmpeg 없이: 약 23MB
- FFmpeg 포함: 약 107MB (권장)

## 빌드 옵션 설명

### 기본 옵션

- `--onefile`: 단일 실행 파일로 빌드
- `--windowed`: GUI 모드 (콘솔 창 숨김)
- `--console`: 콘솔 창 표시 (디버깅용)
- `--name`: 실행 파일 이름

### FFmpeg 포함 옵션

- `--add-binary=ffmpeg/ffmpeg.exe;.`: FFmpeg 바이너리 포함 (Windows)
- `--add-binary=ffmpeg/ffmpeg;.`: FFmpeg 바이너리 포함 (Mac/Linux)

### 추가 옵션

- `--icon=icon.ico`: 아이콘 설정
- `--add-data`: 추가 데이터 파일 포함
- `--hidden-import`: 숨겨진 import 명시
- `--collect-all`: 패키지 전체 수집

## 플랫폼별 빌드

### Windows

```bash
# FFmpeg 포함 (권장)
pyinstaller --onefile --windowed \
  --add-binary="ffmpeg/ffmpeg.exe;." \
  --name YouTube-Downloader main.py

# 디버깅용 (콘솔 표시)
pyinstaller --onefile --console \
  --add-binary="ffmpeg/ffmpeg.exe;." \
  --name YouTube-Downloader main.py
```

### macOS

```bash
# .app 번들 생성
pyinstaller --onefile --windowed \
  --add-binary="ffmpeg/ffmpeg;." \
  --name YouTube-Downloader main.py

# 결과: dist/YouTube-Downloader.app
```

### Linux

```bash
pyinstaller --onefile --windowed \
  --add-binary="ffmpeg/ffmpeg;." \
  --name YouTube-Downloader main.py

# 실행 권한 부여
chmod +x dist/YouTube-Downloader
```

## 아이콘 추가 (선택사항)

### 1. 아이콘 파일 준비

- Windows: `.ico` 파일
- macOS: `.icns` 파일
- Linux: `.png` 파일

### 2. 빌드 시 아이콘 지정

```bash
pyinstaller --onefile --windowed --icon=icon.ico \
  --add-binary="ffmpeg/ffmpeg.exe;." \
  --name YouTube-Downloader main.py
```

## 문제 해결

### FFmpeg 관련 오류

#### "ffmpeg.exe not found" 빌드 오류

**원인**: `ffmpeg/` 폴더에 FFmpeg가 없음

**해결**:
1. FFmpeg 다운로드 (위의 "FFmpeg 준비" 섹션 참조)
2. `ffmpeg/ffmpeg.exe` 파일 확인
3. 다시 빌드

#### 실행 시 "avcodec-62.dll not found" 오류

**원인**: Dynamic 빌드 버전 사용 (DLL 의존성 있음)

**해결**:
1. [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/)에서 static 빌드 다운로드
   - `ffmpeg-git-essentials.7z` 권장
2. `bin/ffmpeg.exe` 파일만 복사 (DLL 불필요)
3. 다시 빌드

### "Failed to execute script" 오류

**원인**: 누락된 의존성

**해결**:
```bash
# hidden imports 추가
--hidden-import=yt_dlp --hidden-import=tkinter --collect-all=yt_dlp
```

### tkinter 관련 오류

**해결**:
```bash
--hidden-import=tkinter --hidden-import=tkinter.ttk
```

### 실행 파일이 너무 큼

**정상**: FFmpeg 포함 시 약 107MB는 정상입니다.
- FFmpeg: 약 85MB
- Python + yt-dlp: 약 22MB

**줄이려면**:
- FFmpeg 제외 (사용자가 직접 설치)
- UPX 압축 사용 (권장하지 않음 - 안티바이러스 오진 가능)

## 테스트

빌드 후 반드시 테스트하세요:

### 기본 테스트

```bash
# Windows
dist\YouTube-Downloader.exe

# Mac/Linux
./dist/YouTube-Downloader
```

### FFmpeg 포함 확인

1. 프로그램 실행
2. YouTube URL 입력
3. 고화질 비디오 다운로드 시도
4. 자막 병합 기능 테스트

## 배포

### Windows

1. `dist/YouTube-Downloader.exe` 배포
2. 파일 크기: 약 107MB
3. 사용자는 다운로드 후 바로 실행 가능
4. 별도 설치 불필요

**주의**: Windows Defender가 차단할 수 있음
- 사용자에게 "추가 정보" → "실행" 안내

### macOS

1. `dist/YouTube-Downloader.app` 배포
2. 선택사항: DMG 파일 생성
3. 코드 서명 권장 (Gatekeeper 우회)

### Linux

1. `dist/YouTube-Downloader` 배포
2. 실행 권한 설정 안내: `chmod +x YouTube-Downloader`

## 자동 빌드 스크립트

### build.py 구조

```python
def check_ffmpeg():
    """FFmpeg 존재 확인"""
    # ffmpeg/ 폴더에서 바이너리 찾기
    # 파일 크기 표시
    
def build():
    """빌드 실행"""
    # FFmpeg 확인
    # PyInstaller 옵션 설정
    # FFmpeg 포함 옵션 추가
    # 빌드 실행
```

### 실행

```bash
python build.py
```

**출력 예시:**
```
✅ FFmpeg 발견: ffmpeg\ffmpeg.exe (211.8 MB)
📦 FFmpeg를 실행 파일에 포함합니다...

🚀 PyInstaller 빌드 시작...
...
✅ 빌드 완료!
실행 파일 위치: dist/YouTube-Downloader.exe
✅ FFmpeg가 포함되어 있습니다. 사용자는 별도 설치가 필요 없습니다.
```

## 주의사항

### 1. 크로스 플랫폼 빌드 불가

- Windows용 → Windows에서 빌드
- macOS용 → macOS에서 빌드
- Linux용 → Linux에서 빌드

각 OS별로 별도 빌드 필요!

### 2. FFmpeg 라이선스

FFmpeg는 GPL 라이선스입니다.
- 배포 시 라이선스 준수 필요
- 소스 코드 공개 의무 (GPL)

### 3. 안티바이러스 오진

PyInstaller 실행 파일이 오진될 수 있음
- 해결: 코드 서명 (유료)
- 또는 사용자에게 예외 추가 안내

### 4. 파일 크기

- FFmpeg 포함: 약 107MB
- 사용자 편의성 vs 파일 크기 트레이드오프
- 권장: FFmpeg 포함 (사용자 경험 향상)

## 개발 vs 배포

### 개발 시

```bash
# 콘솔 모드로 빌드 (디버깅 편함)
python build.py
# build.py에서 --console 옵션 추가
```

### 배포 시

```bash
# GUI 모드로 빌드 (깔끔함)
python build.py
# 기본 설정: --windowed (콘솔 창 없음)
```

## FFmpeg 없이 빌드

사용자가 FFmpeg를 직접 설치하도록 하려면:

1. `build.py`에서 `--add-binary` 옵션 제거
2. 또는 `ffmpeg/` 폴더 삭제
3. 빌드 실행

**결과:**
- 파일 크기: 약 23MB
- 사용자는 FFmpeg 별도 설치 필요
- 일부 기능 제한 (고화질 다운로드, 자막 병합)

## 추가 리소스

- [PyInstaller 공식 문서](https://pyinstaller.org/)
- [FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases)
- [FFmpeg 공식 사이트](https://ffmpeg.org/)

## 빌드 체크리스트

빌드 전 확인사항:

- [ ] Python 3.9 이상 설치
- [ ] PyInstaller 설치 (`uv add --dev pyinstaller`)
- [ ] FFmpeg 바이너리 준비 (`ffmpeg/ffmpeg.exe`)
- [ ] 모든 테스트 통과 (`python run_tests.py`)
- [ ] 의존성 확인 (`python check_dependencies.py`)

빌드 후 확인사항:

- [ ] 실행 파일 생성 확인 (`dist/YouTube-Downloader.exe`)
- [ ] 파일 크기 확인 (약 107MB)
- [ ] 실행 테스트
- [ ] 비디오 다운로드 테스트
- [ ] 자막 다운로드 테스트
- [ ] 고화질 다운로드 테스트 (FFmpeg 확인)
