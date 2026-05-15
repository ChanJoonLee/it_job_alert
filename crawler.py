"""
crawler.py — 사람인(saramin.co.kr) IT 채용공고 수집 모듈
"""

import sys
import io
import time

# Windows 콘솔 한글 깨짐 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus

# 사람인 검색 기본 URL
BASE_URL = "https://www.saramin.co.kr/zf_user/search/recruit"

# 봇 차단 우회용 헤더
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.saramin.co.kr/",
}


def _build_url(keyword: str, page: int) -> str:
    """키워드와 페이지 번호로 사람인 검색 URL을 생성한다."""
    params = {
        "searchType": "search",
        "searchword": keyword,
        "recruitPage": page,
    }
    return f"{BASE_URL}?{urlencode(params, quote_via=quote_plus)}"


def _parse_job_list(soup: BeautifulSoup, keyword: str) -> list[dict]:
    """
    BeautifulSoup 객체에서 채용공고 목록을 파싱해 dict 리스트로 반환한다.
    사람인 HTML 구조 변경에 대비해 여러 선택자를 시도한다.
    """
    jobs = []

    # 공고 카드: .item_recruit 또는 .list_item
    items = soup.select(".item_recruit") or soup.select(".list_item")

    for item in items:
        try:
            # 공고 제목 & URL
            title_tag = item.select_one(".job_tit a") or item.select_one("h2 a") or item.select_one("a.job_tit")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href  = title_tag.get("href", "")
            url   = f"https://www.saramin.co.kr{href}" if href.startswith("/") else href

            # 회사명
            company_tag = item.select_one(".corp_name a") or item.select_one(".company a")
            company = company_tag.get_text(strip=True) if company_tag else "정보 없음"

            # 지역
            location_tag = item.select_one(".work_place") or item.select_one(".job_condition span:first-child")
            location = location_tag.get_text(strip=True) if location_tag else "정보 없음"

            # 마감일
            deadline_tag = item.select_one(".job_date .date") or item.select_one(".deadlines")
            deadline = deadline_tag.get_text(strip=True) if deadline_tag else "정보 없음"

            jobs.append({
                "keyword":  keyword,
                "title":    title,
                "company":  company,
                "location": location,
                "deadline": deadline,
                "url":      url,
            })
        except Exception as e:
            # 개별 항목 파싱 실패는 건너뜀
            print(f"  [파싱] 항목 파싱 오류(건너뜀): {e}")
            continue

    return jobs


def fetch_jobs(keyword: str, max_pages: int = 3) -> list[dict]:
    """
    사람인에서 keyword로 검색한 채용공고 목록을 반환한다.

    반환 형식:
        [{'keyword': ..., 'title': ..., 'company': ...,
          'location': ..., 'deadline': ..., 'url': ...}, ...]

    구현 조건:
    - requests + BeautifulSoup 사용
    - User-Agent 헤더 설정 (봇 차단 우회)
    - 페이지 반복 수집 (for 루프)
    - 수집 실패 시 try/except로 예외 처리, 실패 페이지는 건너뜀
    - 각 페이지 수집 후 1~2초 지연
    """
    all_jobs: list[dict] = []

    for page in range(1, max_pages + 1):
        url = _build_url(keyword, page)
        print(f"  [수집] '{keyword}' 키워드 {page}페이지 요청 중... ({url})")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # 4xx / 5xx → HTTPError 발생

            soup = BeautifulSoup(response.text, "html.parser")
            page_jobs = _parse_job_list(soup, keyword)

            if not page_jobs:
                print(f"  [수집] {page}페이지 공고 없음 (마지막 페이지이거나 차단됨) → 중단")
                break

            all_jobs.extend(page_jobs)
            print(f"  [수집] {page}페이지 {len(page_jobs)}건 수집 완료 (누적: {len(all_jobs)}건)")

        except requests.exceptions.ConnectionError:
            print(f"  [수집] {page}페이지 네트워크 연결 오류 → 건너뜀")
            continue
        except requests.exceptions.HTTPError as e:
            print(f"  [수집] {page}페이지 HTTP 오류 {e} → 건너뜀")
            continue
        except requests.exceptions.Timeout:
            print(f"  [수집] {page}페이지 요청 시간 초과 → 건너뜀")
            continue
        except Exception as e:
            print(f"  [수집] {page}페이지 예기치 않은 오류: {e} → 건너뜀")
            continue

        # 서버 부하 방지를 위한 랜덤 지연 (1~2초)
        delay = random.uniform(1.0, 2.0)
        time.sleep(delay)

    print(f"[수집] '{keyword}' 키워드 총 {len(all_jobs)}건 수집 완료")
    return all_jobs


# ─────────────────────────────────────────────
# 단독 테스트 실행용
# ─────────────────────────────────────────────
if __name__ == "__main__":
    results = fetch_jobs("python", max_pages=1)
    print(f"\n── 수집 결과 ({len(results)}건) ──")
    for i, job in enumerate(results, 1):
        print(f"{i:3}. [{job['company']}] {job['title']}")
        print(f"      마감: {job['deadline']} | 지역: {job['location']}")
        print(f"      URL : {job['url']}")
