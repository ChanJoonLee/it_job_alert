# IT 채용공고 자동 알림 시스템

사람인(saramin.co.kr)에서 IT 채용공고를 자동 수집하고, 신규 공고를 이메일로 알려주는 Python 자동화 도구입니다.  
매일 오전 9시에 자동 실행되며, 중복 공고는 제외하고 새로운 공고만 발송합니다.

## 주요 기능

- **자동 크롤링** — 사람인에서 키워드별 채용공고 수집 (최대 N페이지)
- **중복 제거** — pickle 기반 URL 이력 관리로 이미 알림된 공고 제외
- **이메일 알림** — 신규 공고를 HTML 테이블 형식으로 이메일 발송
- **Excel 저장** — 전체 수집 결과를 `.xlsx` 파일로 저장
- **스케줄러** — 매일 09:00 자동 실행 (첫 실행 시 즉시 1회 실행)

## 프로젝트 구조

```
it_job_alert/
├── main.py          # 진입점 — 파이프라인 실행 및 스케줄러
├── crawler.py       # 사람인 크롤러 (requests + BeautifulSoup)
├── notifier.py      # 이메일 발송 모듈 (smtplib)
├── history.py       # URL 수집 이력 관리 (pickle)
├── config.py        # 설정 파일 (이메일, 키워드, 경로 등)
├── requirements.txt # 의존 패키지 목록
├── seen_urls.pkl    # 수집 이력 (자동 생성)
└── jobs_result.xlsx # 수집 결과 Excel (자동 생성)
```

## 설치

```bash
pip install -r requirements.txt
```

**필요 패키지**

| 패키지 | 버전 | 용도 |
|--------|------|------|
| requests | 2.31.0 | HTTP 요청 |
| beautifulsoup4 | 4.12.3 | HTML 파싱 |
| pandas | 2.2.2 | DataFrame / Excel 저장 |
| openpyxl | 3.1.2 | Excel 파일 엔진 |
| schedule | 1.2.2 | 스케줄러 |

## 설정

이메일 계정은 보안을 위해 환경변수로 설정합니다. PowerShell 기준 예시는 아래와 같습니다.

```powershell
$env:JOB_ALERT_EMAIL_ID="your_email@naver.com"
$env:JOB_ALERT_EMAIL_PW="앱_비밀번호"
$env:JOB_ALERT_RECEIVER_EMAIL="receiver@email.com"
```

`config.py`에서 검색 키워드, 수집 페이지 수, SMTP 공급자 등을 조정할 수 있습니다.

```python
# 이메일 계정: 환경변수에서 읽음
EMAIL_ID       = os.getenv("JOB_ALERT_EMAIL_ID", "your_email@naver.com")
EMAIL_PW       = os.getenv("JOB_ALERT_EMAIL_PW", "app_password")
RECEIVER_EMAIL = os.getenv("JOB_ALERT_RECEIVER_EMAIL", EMAIL_ID)

# SMTP 공급자 ("naver" 또는 "gmail")
SMTP_PROVIDER = "naver"

# 검색 키워드 목록
SEARCH_KEYWORDS = ["python", "백엔드", "데이터분석"]

# 키워드당 최대 수집 페이지 수
MAX_PAGES = 3
```

### 네이버 메일 앱 비밀번호 발급

1. 네이버 로그인 → **보안설정** → **2단계 인증** 활성화
2. **외부 앱 비밀번호** → 새 비밀번호 생성
3. 발급된 비밀번호를 `EMAIL_PW`에 입력

### Gmail 사용 시

```python
SMTP_PROVIDER = "gmail"
```
Gmail도 동일하게 **앱 비밀번호** 발급 후 사용합니다.  
(Google 계정 → 보안 → 2단계 인증 → 앱 비밀번호)

## 실행

```bash
python main.py
```

실행하면 즉시 1회 수집·발송 후, 이후 매일 09:00에 자동 실행됩니다.  
종료는 `Ctrl+C`입니다.

### 실행 흐름

```
1단계  수집 이력 로드 (seen_urls.pkl)
2단계  키워드별 사람인 크롤링
3단계  신규 공고 필터링 (중복 URL 제외)
4단계  신규 공고 이메일 발송
5단계  Excel 저장 & 이력 업데이트
```

### 실행 예시 출력

```
============================================================
[시작] IT 채용공고 수집 시작 — 2026-05-15 09:00:00
============================================================

[단계 1/5] 수집 이력 로드 중...
[이력] 142개의 기존 URL을 로드했습니다.

[단계 2/5] 채용공고 수집 시작 (키워드: ['python', '백엔드', '데이터분석'])
  ▶ 키워드: 'python' (최대 3페이지)
  ...

[단계 3/5] 신규 공고 필터링 중...
  신규: 12건 | 중복(제외): 34건

[단계 4/5] 이메일 발송 처리 중...
  이메일 발송 성공

[단계 5/5] 결과 저장 중...
  Excel 저장 완료: jobs_result.xlsx (46행)

============================================================
[완료] 소요 시간: 38초 | 신규 공고: 12건
============================================================
```

## 이메일 형식

신규 채용공고를 아래와 같은 HTML 테이블로 발송합니다.

| # | 공고 제목 | 회사명 | 지역 | 마감일 | 키워드 |
|---|-----------|--------|------|--------|--------|
| 1 | Python 백엔드 개발자 | ABC Corp | 서울 | 06/30 | python |
| 2 | 데이터 분석가 (신입) | XYZ Inc | 판교 | 상시 | 데이터분석 |

## 크롤러 단독 테스트

```bash
python crawler.py
```

`python` 키워드로 1페이지 수집 결과를 콘솔에 출력합니다.

## 주의사항

- `config.py`에 이메일 비밀번호를 평문으로 저장합니다. 공개 저장소에 업로드하지 마세요.
- 사람인 HTML 구조가 변경되면 크롤러 선택자 수정이 필요할 수 있습니다.
- 서버 부하 방지를 위해 페이지 요청 간 1~2초 랜덤 지연이 적용됩니다.
