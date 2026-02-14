import json
import os
from datetime import datetime
from pathlib import Path

class DownloadHistory:
    """다운로드 히스토리 관리 클래스"""
    
    def __init__(self, history_file='download_history.json'):
        """
        히스토리 관리자 초기화
        
        Args:
            history_file (str): 히스토리 파일 경로
        """
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        """히스토리 파일을 로드합니다."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"히스토리 파일 로드 실패: {e}")
                return []
        return []
    
    def save_history(self):
        """현재 히스토리를 파일에 저장합니다."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"히스토리 파일 저장 실패: {e}")
            return False
    
    def add_download(self, url, title, mode, quality=None, subtitle_langs=None, 
                     file_path=None, file_size=None, status='success'):
        """
        다운로드 기록 추가
        
        Args:
            url (str): YouTube URL
            title (str): 비디오 제목
            mode (str): 다운로드 모드 (video, subtitles, video_subs)
            quality (str): 비디오 품질
            subtitle_langs (list): 자막 언어 목록
            file_path (str): 저장된 파일 경로
            file_size (int): 파일 크기 (bytes)
            status (str): 다운로드 상태 (success, failed, cancelled)
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'title': title,
            'mode': mode,
            'quality': quality,
            'subtitle_langs': subtitle_langs,
            'file_path': file_path,
            'file_size': file_size,
            'status': status
        }
        
        self.history.insert(0, record)  # 최신 항목을 맨 앞에
        
        # 최대 100개까지만 유지
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        self.save_history()
    
    def get_recent_downloads(self, limit=10):
        """
        최근 다운로드 목록 가져오기
        
        Args:
            limit (int): 가져올 최대 개수
            
        Returns:
            list: 다운로드 기록 목록
        """
        return self.history[:limit]
    
    def get_all_downloads(self):
        """모든 다운로드 기록 가져오기"""
        return self.history
    
    def get_downloads_by_status(self, status):
        """
        특정 상태의 다운로드 기록 가져오기
        
        Args:
            status (str): 상태 (success, failed, cancelled)
            
        Returns:
            list: 필터링된 다운로드 기록
        """
        return [record for record in self.history if record.get('status') == status]
    
    def search_downloads(self, query):
        """
        제목이나 URL로 다운로드 기록 검색
        
        Args:
            query (str): 검색어
            
        Returns:
            list: 검색 결과
        """
        query_lower = query.lower()
        results = []
        
        for record in self.history:
            title = record.get('title', '').lower()
            url = record.get('url', '').lower()
            
            if query_lower in title or query_lower in url:
                results.append(record)
        
        return results
    
    def get_statistics(self):
        """
        다운로드 통계 가져오기
        
        Returns:
            dict: 통계 정보
        """
        total = len(self.history)
        success = len([r for r in self.history if r.get('status') == 'success'])
        failed = len([r for r in self.history if r.get('status') == 'failed'])
        cancelled = len([r for r in self.history if r.get('status') == 'cancelled'])
        
        total_size = sum(r.get('file_size', 0) for r in self.history if r.get('file_size'))
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'cancelled': cancelled,
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024) if total_size else 0
        }
    
    def clear_history(self):
        """모든 히스토리 삭제"""
        self.history = []
        self.save_history()
    
    def delete_record(self, index):
        """
        특정 기록 삭제
        
        Args:
            index (int): 삭제할 기록의 인덱스
        """
        if 0 <= index < len(self.history):
            del self.history[index]
            self.save_history()
            return True
        return False

# 전역 히스토리 인스턴스
_history_instance = None

def get_history():
    """전역 히스토리 인스턴스 가져오기"""
    global _history_instance
    if _history_instance is None:
        _history_instance = DownloadHistory()
    return _history_instance
