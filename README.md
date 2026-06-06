# IT 채용공고 자동 알림 시스템

사람인(saramin.co.kr)에서 IT 채용공고를 수집하고, 이전에 보낸 적 없는 신규 공고만 이메일로 발송하는 Python 자동화 프로그램입니다.

`python main.py`를 실행하면 즉시 한 번 수집을 진행하고, 이후 프로그램이 켜져 있는 동안 매일 오전 9시에 같은 작업을 반복합니다.

## 실행 전 준비

필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

이메일 발송에 사용할 계정 정보는 `config.py`에 직접 적지 않고 환경변수로 넣습니다. PowerShell에서는 아래처럼 설정합니다.

```powershell
$env:JOB_ALERT_EMAIL_ID="your_email@naver.com"
$env:JOB_ALERT_EMAIL_PW="앱_비밀번호"
$env:JOB_ALERT_RECEIVER_EMAIL="receiver@email.com"
```

각 값의 의미는 다음과 같습니다.

| 환경변수 | 의미 |
|---|---|
| `JOB_ALERT_EMAIL_ID` | 발신 이메일 계정 |
| `JOB_ALERT_EMAIL_PW` | 발신 계정의 앱 비밀번호 |
| `JOB_ALERT_RECEIVER_EMAIL` | 알림을 받을 이메일 주소 |

PowerShell에서 설정한 환경변수는 현재 터미널 창에서만 유지됩니다. 새 터미널에서 실행할 때는 다시 설정해야 합니다.

## 설정 변경

[config.py](config.py)에서 수집 조건과 이메일 서버를 조정합니다.

```python
SMTP_PROVIDER = "naver"   # "naver" 또는 "gmail"

SEARCH_KEYWORDS = ["python", "백엔드", "데이터분석"]
MAX_PAGES = 3

SEEN_URLS_PATH = "seen_urls.pkl"
EXCEL_SAVE_PATH = "jobs_result.xlsx"
```

`SEARCH_KEYWORDS`는 검색할 키워드 목록이고, `MAX_PAGES`는 키워드마다 최대 몇 페이지까지 수집할지 정하는 값입니다.

## 실행

```bash
python main.py
```

실행 후 종료하려면 `Ctrl+C`를 누릅니다.

## 전체 흐름

```text
1. main.py 실행
2. 환경변수와 config.py 설정 로드
3. run_job_alert() 즉시 1회 실행
4. seen_urls.pkl에서 기존 발송 URL 이력 로드
5. config.SEARCH_KEYWORDS에 있는 키워드를 하나씩 사람인에서 검색
6. 각 키워드별 채용공고 제목, 회사명, 지역, 마감일, URL 수집
7. 이미 이력에 있는 URL은 중복으로 판단해 제외
8. 신규 공고가 있으면 HTML 이메일로 발송
9. 전체 수집 결과를 jobs_result.xlsx로 저장
10. 신규 공고 URL을 seen_urls.pkl에 저장
11. 매일 09:00에 다시 실행되도록 스케줄 등록
12. 프로그램이 켜져 있는 동안 30초마다 스케줄 확인
```

## 파일 역할

| 파일 | 역할 |
|---|---|
| `main.py` | 전체 실행 흐름과 스케줄러 관리 |
| `config.py` | 이메일, 검색 키워드, 저장 경로 설정 |
| `crawler.py` | 사람인 채용공고 수집 |
| `history.py` | 이미 처리한 공고 URL 이력 저장/로드 |
| `notifier.py` | 신규 공고 이메일 발송 |
| `requirements.txt` | 실행에 필요한 Python 패키지 목록 |

## 실행 중 생성되는 파일

| 파일 | 설명 |
|---|---|
| `seen_urls.pkl` | 이미 이메일 알림 처리한 공고 URL 이력 |
| `jobs_result.xlsx` | 마지막 실행에서 수집한 전체 공고 목록 |
| `__pycache__/` | Python이 자동 생성하는 캐시 폴더 |

위 파일들은 실행 결과물이므로 Git에는 포함하지 않습니다.

## 이메일 내용

신규 공고가 있을 때만 메일을 보냅니다. 메일에는 아래 항목이 HTML 테이블로 들어갑니다.

| 항목 |
|---|
| 번호 |
| 공고 제목 |
| 회사명 |
| 지역 |
| 마감일 |
| 검색 키워드 |

신규 공고가 없으면 이메일은 보내지 않고, 수집 결과 저장과 이력 저장만 진행합니다.

## 주의사항

- 네이버나 Gmail을 사용할 때는 일반 비밀번호가 아니라 앱 비밀번호를 사용해야 합니다.
- 사람인 페이지 구조가 바뀌면 `crawler.py`의 HTML 선택자 수정이 필요할 수 있습니다.
- `seen_urls.pkl`을 삭제하면 기존 발송 이력이 초기화되어 같은 공고가 다시 신규로 잡힐 수 있습니다.
- 프로그램을 종료하면 매일 09:00 자동 실행도 멈춥니다.
