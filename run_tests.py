#!/usr/bin/env python
"""
테스트 실행 스크립트

모든 단위 테스트를 실행하고 결과를 출력합니다.
"""

import unittest
import sys
import os

def run_tests():
    """모든 테스트 실행"""
    # tests 디렉토리를 Python 경로에 추가
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # 테스트 로더 생성
    loader = unittest.TestLoader()
    
    # tests 디렉토리에서 모든 테스트 발견
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 출력
    print("\n" + "="*70)
    print(f"테스트 실행 완료")
    print(f"총 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"에러: {len(result.errors)}")
    print("="*70)
    
    # 실패한 테스트가 있으면 종료 코드 1 반환
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
