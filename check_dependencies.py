#!/usr/bin/env python
"""
의존성 확인 스크립트

필수 및 선택적 의존성이 올바르게 설치되었는지 확인합니다.
"""

import sys
import subprocess
import shutil

def check_python_version():
    """Python 버전 확인"""
    print("=" * 60)
    print("Python 버전 확인")
    print("=" * 60)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"현재 Python 버전: {version_str}")
    
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python 버전 요구사항 충족 (3.9 이상)")
        return True
    else:
        print("❌ Python 3.9 이상이 필요합니다")
        print("   yt-dlp 최신 버전은 Python 3.9 이상을 요구합니다")
        return False

def check_python_package(package_name, import_name=None):
    """Python 패키지 설치 확인"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} 설치됨")
        return True
    except ImportError:
        print(f"❌ {package_name} 설치 안 됨")
        return False

def check_command(command, name):
    """명령어 실행 가능 여부 확인"""
    path = shutil.which(command)
    if path:
        try:
            result = subprocess.run(
                [command, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_output = result.stdout or result.stderr
            version_line = version_output.split('\n')[0] if version_output else "버전 정보 없음"
            print(f"✅ {name} 설치됨: {version_line}")
            print(f"   경로: {path}")
            return True
        except Exception as e:
            print(f"⚠️  {name} 발견되었으나 실행 실패: {e}")
            return False
    else:
        print(f"❌ {name} 설치 안 됨 또는 PATH에 없음")
        return False

def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("YouTube 다운로더 의존성 확인")
    print("=" * 60 + "\n")
    
    all_ok = True
    
    # Python 버전 확인
    if not check_python_version():
        all_ok = False
    print()
    
    # 필수 Python 패키지 확인
    print("=" * 60)
    print("필수 Python 패키지 확인")
    print("=" * 60)
    
    required_packages = [
        ('yt-dlp', 'yt_dlp'),
        ('tkinter', 'tkinter'),
    ]
    
    for package_name, import_name in required_packages:
        if not check_python_package(package_name, import_name):
            all_ok = False
    print()
    
    # 선택적 도구 확인
    print("=" * 60)
    print("선택적 도구 확인 (권장)")
    print("=" * 60)
    
    optional_tools = [
        ('ffmpeg', 'FFmpeg'),
        ('node', 'Node.js'),
    ]
    
    optional_ok = True
    for command, name in optional_tools:
        if not check_command(command, name):
            optional_ok = False
    print()
    
    # 결과 요약
    print("=" * 60)
    print("확인 결과 요약")
    print("=" * 60)
    
    if all_ok:
        print("✅ 모든 필수 의존성이 설치되어 있습니다!")
    else:
        print("❌ 일부 필수 의존성이 누락되었습니다.")
        print("\n설치 방법:")
        print("  uv sync  # UV 사용")
        print("  또는")
        print("  pip install yt-dlp  # pip 사용")
    
    print()
    
    if not optional_ok:
        print("⚠️  일부 선택적 도구가 설치되지 않았습니다.")
        print("   프로그램은 작동하지만, 일부 기능이 제한될 수 있습니다.")
        print("\n선택적 도구 설치 방법:")
        print("  - FFmpeg: README.md의 'FFmpeg 설치' 섹션 참조")
        print("  - Node.js: README.md의 'Node.js 설치' 섹션 참조")
    else:
        print("✅ 모든 선택적 도구가 설치되어 있습니다!")
    
    print("\n" + "=" * 60)
    
    # 종료 코드 반환
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
