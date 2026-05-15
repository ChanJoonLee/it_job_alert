"""
main.py — IT 채용공고 자동 수집 & 이메일 알림 시스템 진입점
매일 오전 9시에 자동 실행되며, 최초 실행 시 즉시 한 번 실행한다.
"""

import os
import sys
import io
import time

# Windows 콘솔 한글 깨짐 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from datetime import datetime

import pandas as pd
import schedule

import config
from crawler  import fetch_jobs
from history  import load_seen_urls, save_seen_urls
from notifier import send_email


def run_job_alert() -> None:
    """
    전체 파이프라인 실행 함수:
    1. config의 키워드 목록 순회
    2. crawler.fetch_jobs()로 공고 수집
    3. history.load_seen_urls()로 기존 이력 로드
    4. 신규 공고만 필터링 (url 기준)
    5. 신규 공고가 있으면 notifier.send_email() 호출
    6. 전체 수집 결과를 pandas DataFrame으로 만들어 Excel 저장
    7. history.save_seen_urls()로 이력 업데이트
    8. 각 단계별 진행 상황 print로 출력
    """
    start_time = datetime.now()
    print(f"\n{'='*60}")
    print(f"[시작] IT 채용공고 수집 시작 — {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # ── 1단계: 기존 이력 로드 ──────────────────────────────────
    print("\n[단계 1/5] 수집 이력 로드 중...")
    seen_urls = load_seen_urls(config.SEEN_URLS_PATH)

    # ── 2단계: 키워드별 공고 수집 ──────────────────────────────
    print(f"\n[단계 2/5] 채용공고 수집 시작 (키워드: {config.SEARCH_KEYWORDS})")
    all_jobs: list[dict] = []

    for keyword in config.SEARCH_KEYWORDS:
        print(f"\n  ▶ 키워드: '{keyword}' (최대 {config.MAX_PAGES}페이지)")
        jobs = fetch_jobs(keyword, max_pages=config.MAX_PAGES)
        all_jobs.extend(jobs)

    print(f"\n[단계 2/5] 전체 수집 완료: {len(all_jobs)}건")

    # ── 3단계: 신규 공고 필터링 ────────────────────────────────
    print("\n[단계 3/5] 신규 공고 필터링 중...")
    new_jobs = [job for job in all_jobs if job["url"] not in seen_urls]
    dup_count = len(all_jobs) - len(new_jobs)
    print(f"  신규: {len(new_jobs)}건 | 중복(제외): {dup_count}건")

    # ── 4단계: 이메일 발송 ─────────────────────────────────────
    print("\n[단계 4/5] 이메일 발송 처리 중...")
    if new_jobs:
        success = send_email(new_jobs)
        status  = "성공" if success else "실패"
        print(f"  이메일 발송 {status}")
    else:
        print("  신규 공고 없음 → 이메일 미발송")

    # ── 5단계: Excel 저장 & 이력 업데이트 ─────────────────────
    print("\n[단계 5/5] 결과 저장 중...")

    if all_jobs:
        df = pd.DataFrame(all_jobs, columns=["keyword", "title", "company", "location", "deadline", "url"])
        df.to_excel(config.EXCEL_SAVE_PATH, index=False, engine="openpyxl")
        print(f"  Excel 저장 완료: {config.EXCEL_SAVE_PATH} ({len(df)}행)")
    else:
        print("  수집된 공고 없음 → Excel 저장 생략")

    # 신규 URL을 이력에 추가 후 저장
    new_urls = {job["url"] for job in new_jobs}
    seen_urls.update(new_urls)
    save_seen_urls(seen_urls, config.SEEN_URLS_PATH)

    elapsed = (datetime.now() - start_time).seconds
    print(f"\n{'='*60}")
    print(f"[완료] 소요 시간: {elapsed}초 | 신규 공고: {len(new_jobs)}건")
    print(f"{'='*60}\n")


def main() -> None:
    """
    스케줄러 진입점.
    최초 실행 시 즉시 한 번 실행하고, 매일 09:00에 재실행한다.
    Ctrl+C로 종료 가능.
    """
    print("IT 채용공고 자동 수집 시스템 시작")
    print(f"  수신 이메일: {config.RECEIVER_EMAIL}")
    print(f"  검색 키워드: {config.SEARCH_KEYWORDS}")
    print(f"  스케줄: 매일 09:00 자동 실행")
    print("  종료: Ctrl+C\n")

    # 최초 즉시 실행
    run_job_alert()

    # 매일 09:00 스케줄 등록
    schedule.every().day.at("09:00").do(run_job_alert)
    print("[스케줄러] 등록 완료 — 다음 실행: 오전 09:00")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # 30초마다 스케줄 확인
    except KeyboardInterrupt:
        print("\n[종료] 사용자가 Ctrl+C로 종료했습니다.")
        sys.exit(0)


if __name__ == "__main__":
    # 작업 디렉터리를 스크립트 위치로 고정 (상대 경로 일관성 보장)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
