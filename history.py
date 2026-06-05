"""
history.py — pickle 기반 수집 URL 이력 관리 모듈
"""

import pickle
import os


def load_seen_urls(path: str = "seen_urls.pkl") -> set:
    """
    pkl 파일에서 기존 수집 URL set을 불러온다.
    파일이 없거나 손상된 경우 빈 set을 반환한다.
    """
    if not os.path.exists(path):
        print(f"[이력] {path} 파일 없음 → 빈 이력으로 시작합니다.")
        return set()

    try:
        with open(path, "rb") as f:
            seen = pickle.load(f)
        if not isinstance(seen, set):
            print(f"[이력] {path} 파일 형식이 올바르지 않습니다 → 빈 이력으로 초기화합니다.")
            return set()
        print(f"[이력] {len(seen)}개의 기존 URL을 로드했습니다.")
        return seen
    except pickle.UnpicklingError:
        print(f"[이력] {path} 파일이 손상되었습니다 → 빈 이력으로 초기화합니다.")
        return set()
    except Exception as e:
        print(f"[이력] 로드 중 예기치 않은 오류 발생: {e} → 빈 이력으로 초기화합니다.")
        return set()


def save_seen_urls(seen: set, path: str = "seen_urls.pkl") -> None:
    """
    현재 seen URL set을 pkl 파일로 저장한다.
    """
    try:
        with open(path, "wb") as f:
            pickle.dump(seen, f)
        print(f"[이력] {len(seen)}개의 URL을 {path}에 저장했습니다.")
    except Exception as e:
        print(f"[이력] 저장 실패: {e}")
