# YouTube 다운로더

YouTube 비디오와 자막을 다운로드하는 간단한 데스크톱 애플리케이션으로 학습 및 테스트 목적으로 작성되었습니다.

## 주요 기능

- ✅ YouTube 비디오 다운로드 (다양한 화질 지원)
- ✅ 자막 다운로드 (157개 이상 언어 지원)
- ✅ 비디오 + 자막 동시 다운로드
- ✅ 사용하기 쉬운 GUI 인터페이스
- ✅ CLI 명령줄 인터페이스도 지원
- ✅ 실시간 다운로드 진행률 표시
- ✅ 다운로드 취소 기능
- ✅ 다운로드 히스토리 관리
- ✅ 설정 자동 저장 및 불러오기
- ✅ URL 보안 검증
- ✅ FFmpeg 내장 (별도 설치 불필요)

## 빠른 시작 (실행 파일)

### Windows 사용자

1. [Releases](../../releases)에서 `YouTube-Downloader.exe` 다운로드
2. 다운로드한 파일 실행
3. 끝! 별도 설치 없이 바로 사용 가능

**특징:**
- FFmpeg 내장: 고화질 다운로드, 자막 병합 모두 지원
- 단일 파일: 107MB 크기의 독립 실행 파일
- 설치 불필요: 다운로드 후 바로 실행

## 개발자용 설치

### 필수 요구사항

- Python 3.9 이상
- [UV](https://github.com/astral-sh/uv) (권장 패키지 관리자)

### UV로 설치

```bash
# 1. 프로젝트 클론 또는 다운로드
cd youtube-downloader

# 2. 의존성 자동 설치
uv sync

# 3. 의존성 확인 (선택사항)
uv run python check_dependencies.py

# 4. 프로그램 실행
uv run python main.py
```

## 사용 방법

### GUI 사용 (권장)

1. **YouTube URL 입력**: 다운로드할 영상 URL을 입력하세요 (최근 URL 드롭다운 지원)
2. **다운로드 경로 선택**: 기본 경로는 `사용자폴더/Downloads/YouTube`
3. **다운로드 모드 선택**:
   - 비디오만
   - 자막만
   - 비디오+자막
4. **자막 언어 선택**: 드롭다운에서 원하는 언어 선택 (기본: 한국어)
5. **비디오 품질 선택**: best, 720p, 480p, 360p 중 선택
6. **다운로드 버튼 클릭**
7. **진행률 확인**: 실시간으로 다운로드 진행 상황 확인
8. **완료 후 폴더 열기**: 다운로드 완료 시 폴더 열기 옵션 제공

### CLI 사용

```bash
# 비디오만 다운로드
uv run python downloader.py "YouTube_URL"

# 자막만 다운로드
uv run python downloader.py "YouTube_URL" --subs-only

# 비디오 + 자막 다운로드
uv run python downloader.py "YouTube_URL" --with-subs

# 사용 가능한 자막 확인
uv run python downloader.py "YouTube_URL" --check-subs
```

## 자막 다운로드 팁

### 권장 사용법

- **한 번에 하나의 언어만**: 안정성을 위해 한 언어씩 다운로드하세요
- **여러 언어 필요 시**: 순차적으로 다운로드
  1. 한국어 자막 다운로드
  2. 같은 URL 입력
  3. 영어 선택 후 "자막만" 다운로드

### 지원 언어

- 🇰🇷 한국어 (ko)
- 🇺🇸 영어 (en)
- 🇯🇵 일본어 (ja)
- 🇨🇳 중국어 간체 (zh-Hans)
- 🇹🇼 중국어 번체 (zh-Hant)
- 🇪🇸 스페인어 (es)
- 🇫🇷 프랑스어 (fr)
- 🇩🇪 독일어 (de)
- 🇷🇺 러시아어 (ru)
- 🇵🇹 포르투갈어 (pt)
- 🇮🇹 이탈리아어 (it)

## 주의사항

> 📖 **상세한 보안 가이드는 [SECURITY.md](docs/SECURITY.md)를 참조하세요**

### 보안 가이드

- ✅ **공식 YouTube URL만 사용**: youtube.com, youtu.be 도메인만 허용
- ✅ **URL 검증**: 프로그램이 자동으로 URL을 검증하여 안전하지 않은 URL 차단
- ✅ **안전한 경로 사용**: 사용자 홈 디렉토리 또는 문서 폴더 권장

### 429 오류 (Too Many Requests)

YouTube가 요청을 제한하는 경우 발생합니다.

**해결 방법**:
1. 10분 후 재시도
2. 한 번에 1-2개 영상만 다운로드
3. 여러 영상 다운로드 시 각각 10초 이상 간격 두기

## 문제 해결

### "No module named 'yt_dlp'" 오류

```bash
uv sync
```

### yt-dlp 업데이트

```bash
uv add yt-dlp
uv sync
```

### 비디오 다운로드 실패

1. URL이 정확한지 확인
2. 영상이 비공개/삭제되지 않았는지 확인
3. yt-dlp를 최신 버전으로 업데이트

### 자막 다운로드 실패

1. "자막 확인" 버튼으로 자막 존재 여부 확인
2. 다른 언어로 시도
3. 10분 후 재시도 (429 오류인 경우)

## 빌드 가이드

실행 파일을 직접 빌드하려면 [Build Guide](docs/Build%20guide.md)를 참조하세요.

## 기술 스택

### 필수 의존성
- Python 3.9+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 다운로드 엔진
- [UV](https://github.com/astral-sh/uv) - 빠른 Python 패키지 관리자
- Tkinter - GUI 프레임워크 (Python 기본 포함)

### 내장 도구
- [FFmpeg](https://ffmpeg.org/) - 비디오/오디오 병합 및 변환 (실행 파일에 포함)

### 프로젝트 구조
```
youtube-downloader/
├── main.py                  # 메인 진입점
├── gui_app.py               # GUI 애플리케이션
├── downloader.py            # 다운로드 로직
├── config.py                # 설정 관리
├── logger.py                # 로깅 시스템
├── security.py              # 보안 검증
├── history.py               # 다운로드 히스토리
├── check_dependencies.py    # 의존성 확인 스크립트
├── run_tests.py             # 테스트 실행 스크립트
├── build.py                 # 빌드 스크립트
├── pyproject.toml           # 프로젝트 설정
├── README.md                # 프로젝트 문서
├── .gitignore               # Git 제외 파일 목록
│
├── tests/                   # 테스트 코드
│   ├── __init__.py
│   ├── test_config.py       # 설정 관리 테스트
│   ├── test_logger.py       # 로깅 시스템 테스트
│   ├── test_downloader.py   # 다운로더 테스트
│   └── test_security.py     # 보안 검증 테스트
│
├── docs/                    # 문서
│   ├── Build guide.md       # 빌드 가이드
│   └── SECURITY.md          # 보안 가이드
│
├── ffmpeg/                  # FFmpeg 바이너리 (빌드용, Git 제외)
│   └── ffmpeg.exe           # Static 빌드 FFmpeg
│
├── logs/                    # 로그 파일 (자동 생성, Git 제외)
│   └── youtube_downloader_YYYYMMDD.log
│
├── downloads/               # 다운로드 폴더 (자동 생성, Git 제외)
│
├── build/                   # 빌드 임시 파일 (자동 생성, Git 제외)
│
├── dist/                    # 빌드 결과물 (자동 생성, Git 제외)
│   └── YouTube-Downloader.exe  # 최종 실행 파일 (약 107MB)
│
├── .venv/                   # Python 가상 환경 (Git 제외)
│
├── config.json              # 사용자 설정 (자동 생성, Git 제외)
├── download_history.json    # 다운로드 히스토리 (자동 생성, Git 제외)
└── YouTube-Downloader.spec  # PyInstaller 설정 (자동 생성, Git 제외)
```

## 개발자 가이드

### 개발 환경 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd youtube-downloader

# 2. 의존성 설치
uv sync

# 3. 의존성 확인
uv run python check_dependencies.py

# 4. 개발 모드로 실행
uv run python main.py
```

### 테스트 실행

```bash
# 모든 테스트 실행
uv run python run_tests.py

# 특정 테스트만 실행
python -m unittest tests.test_config
```

### 실행 파일 빌드

자세한 내용은 [Build Guide](docs/Build%20guide.md)를 참조하세요.

```bash
# FFmpeg 준비 (static 빌드 버전)
# ffmpeg/ 폴더에 ffmpeg.exe 배치

# 빌드 실행
uv run python build.py

# 결과물: dist/YouTube-Downloader.exe (약 107MB)
```

## FAQ (자주 묻는 질문)

### Q: FFmpeg를 별도로 설치해야 하나요?

A: 아니요! 실행 파일 버전에는 FFmpeg가 이미 포함되어 있습니다. 다운로드 후 바로 모든 기능을 사용할 수 있습니다.

### Q: 프로그램이 실행되지 않아요

A: 
- **실행 파일 사용 시**: Windows Defender가 차단할 수 있습니다. "추가 정보" → "실행" 클릭
- **소스 코드 실행 시**: Python 3.9 이상 설치 확인 후 `uv sync` 실행

### Q: 다운로드가 너무 느려요

A: 다음을 시도해보세요:
1. 더 낮은 품질 선택 (720p 대신 480p)
2. 인터넷 연결 확인
3. VPN 사용 시 비활성화

### Q: 로그는 어디에 저장되나요?

A: `logs/youtube_downloader_YYYYMMDD.log` 파일에 저장됩니다.

### Q: 다운로드 히스토리는 어떻게 확인하나요?

A: GUI에서 "히스토리" 버튼을 클릭하면 모든 다운로드 기록을 볼 수 있습니다.

## 라이선스

이 프로젝트는 개인적/교육적 용도로 사용하세요.

다운로드한 콘텐츠의 저작권은 원 저작자에게 있으며, 저작권법을 준수해야 합니다.

## 문의 및 기여

버그 리포트나 기능 요청은 Issues에 등록해주세요.

---

**면책 조항**: 이 도구는 학습 및 개인 백업 목적으로만 사용하세요. YouTube 서비스 약관을 준수하고 저작권을 존중해주세요.
