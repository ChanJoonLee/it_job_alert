# ─────────────────────────────────────────────
# 이메일 계정 설정 (실제 값으로 교체 후 사용)
# ─────────────────────────────────────────────
EMAIL_ID       = "your_naver_id@naver.com"   # 발신 계정
EMAIL_PW       = "your_app_password"          # 앱 비밀번호 (2단계 인증 설정 후 발급)
RECEIVER_EMAIL = "receiver@example.com"       # 수신자 이메일

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
