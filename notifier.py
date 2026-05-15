"""
notifier.py — HTML 형식 이메일 발송 모듈 (smtplib)
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import config


def _build_html(new_jobs: list[dict]) -> str:
    """채용공고 목록을 HTML 테이블 문자열로 변환한다."""
    today = datetime.now().strftime("%Y년 %m월 %d일")

    rows = ""
    for i, job in enumerate(new_jobs, 1):
        rows += f"""
        <tr style="background-color: {'#f9f9f9' if i % 2 == 0 else '#ffffff'};">
            <td style="padding:8px; border:1px solid #ddd; text-align:center;">{i}</td>
            <td style="padding:8px; border:1px solid #ddd;">
                <a href="{job['url']}" style="color:#1a73e8; text-decoration:none;">
                    {job['title']}
                </a>
            </td>
            <td style="padding:8px; border:1px solid #ddd;">{job['company']}</td>
            <td style="padding:8px; border:1px solid #ddd;">{job.get('location', '-')}</td>
            <td style="padding:8px; border:1px solid #ddd;">{job.get('deadline', '-')}</td>
            <td style="padding:8px; border:1px solid #ddd; text-align:center;">
                {job.get('keyword', '-')}
            </td>
        </tr>"""

    html = f"""
    <html>
    <body style="font-family: 'Malgun Gothic', Arial, sans-serif; color: #333;">
        <h2 style="color:#1a73e8;">📋 IT 채용공고 알림 — {today}</h2>
        <p>신규 채용공고 <strong>{len(new_jobs)}건</strong>이 수집되었습니다.</p>

        <table style="border-collapse:collapse; width:100%; font-size:13px;">
            <thead>
                <tr style="background-color:#1a73e8; color:#fff;">
                    <th style="padding:10px; border:1px solid #ddd; width:40px;">#</th>
                    <th style="padding:10px; border:1px solid #ddd;">공고 제목</th>
                    <th style="padding:10px; border:1px solid #ddd; width:140px;">회사명</th>
                    <th style="padding:10px; border:1px solid #ddd; width:100px;">지역</th>
                    <th style="padding:10px; border:1px solid #ddd; width:100px;">마감일</th>
                    <th style="padding:10px; border:1px solid #ddd; width:80px;">키워드</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <br>
        <p style="font-size:11px; color:#888;">
            본 메일은 IT 채용공고 자동 수집 시스템에서 자동 발송되었습니다.
        </p>
    </body>
    </html>
    """
    return html


def send_email(new_jobs: list[dict]) -> bool:
    """
    new_jobs 목록을 HTML 테이블 형식으로 이메일 발송한다.

    반환: 발송 성공 True / 실패 False

    구현 조건:
    - config.py의 계정 정보 사용
    - MIMEMultipart + MIMEText(html) 사용
    - smtplib 연결 실패, 로그인 실패, 발송 실패를 각각 처리
    """
    if not new_jobs:
        print("[이메일] 신규 공고가 없어 이메일을 발송하지 않습니다.")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"[IT 채용알림] 신규 공고 {len(new_jobs)}건 — {today}"

    # 메시지 구성
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = config.EMAIL_ID
    msg["To"]      = config.RECEIVER_EMAIL

    html_content = _build_html(new_jobs)
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # SMTP 연결
    try:
        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10)
    except (smtplib.SMTPConnectError, ConnectionRefusedError, OSError) as e:
        print(f"[이메일] SMTP 서버 연결 실패: {e}")
        return False

    # TLS 시작
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
    except smtplib.SMTPException as e:
        print(f"[이메일] TLS 협상 실패: {e}")
        server.quit()
        return False

    # 로그인
    try:
        server.login(config.EMAIL_ID, config.EMAIL_PW)
    except smtplib.SMTPAuthenticationError as e:
        print(f"[이메일] 로그인 실패 (계정/앱 비밀번호 확인 필요): {e}")
        server.quit()
        return False
    except smtplib.SMTPException as e:
        print(f"[이메일] 로그인 중 오류: {e}")
        server.quit()
        return False

    # 발송
    try:
        server.sendmail(config.EMAIL_ID, config.RECEIVER_EMAIL, msg.as_string())
        print(f"[이메일] 발송 성공 → {config.RECEIVER_EMAIL} ({len(new_jobs)}건)")
        server.quit()
        return True
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[이메일] 수신자 거부: {e}")
    except smtplib.SMTPSenderRefused as e:
        print(f"[이메일] 발신자 거부: {e}")
    except smtplib.SMTPDataError as e:
        print(f"[이메일] 데이터 전송 오류: {e}")
    except smtplib.SMTPException as e:
        print(f"[이메일] 발송 실패: {e}")
    finally:
        try:
            server.quit()
        except Exception:
            pass

    return False
