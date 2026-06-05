# ─────────────────────────────────────────────
import os

# 이메일 계정 설정
# 제출본에는 비밀번호를 직접 넣지 않고, 실행할 PC의 환경변수에서 읽도록 구성한다.
# PowerShell 예시:
#   $env:JOB_ALERT_EMAIL_ID="your_email@naver.com"
#   $env:JOB_ALERT_EMAIL_PW="앱_비밀번호"
#   $env:JOB_ALERT_RECEIVER_EMAIL="receiver@email.com"
# ─────────────────────────────────────────────
EMAIL_ID       = os.getenv("JOB_ALERT_EMAIL_ID", "your_email@naver.com")
EMAIL_PW       = os.getenv("JOB_ALERT_EMAIL_PW", "app_password")
RECEIVER_EMAIL = os.getenv("JOB_ALERT_RECEIVER_EMAIL", EMAIL_ID)

# ─────────────────────────────────────────────
# SMTP 서버 설정 — "naver" 또는 "gmail" 선택
# ─────────────────────────────────────────────
SMTP_PROVIDER = "naver"   # "naver" | "gmail"

SMTP_CONFIG = {
    "naver": {"host": "smtp.naver.com", "port": 587},
    "gmail": {"host": "smtp.gmail.com",  "port": 587},
}

# 선택된 공급자의 host / port
SMTP_HOST = SMTP_CONFIG[SMTP_PROVIDER]["host"]
SMTP_PORT = SMTP_CONFIG[SMTP_PROVIDER]["port"]

# ─────────────────────────────────────────────
# 크롤링 설정
# ─────────────────────────────────────────────
SEARCH_KEYWORDS = ["python", "백엔드", "데이터분석"]
MAX_PAGES       = 3   # 키워드당 최대 수집 페이지 수

# ─────────────────────────────────────────────
# 파일 경로
# ─────────────────────────────────────────────
SEEN_URLS_PATH  = "seen_urls.pkl"
EXCEL_SAVE_PATH = "jobs_result.xlsx"
