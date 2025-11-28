"""이메일 발송 유틸리티 (Gmail SMTP 기반)

SendGrid 대신 Gmail SMTP를 사용하여 비밀번호 재설정/환영 이메일을 전송합니다.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

# Gmail SMTP 설정 (환경변수에서 가져오기)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # TLS 기본 포트
SMTP_USER = os.getenv("SMTP_USER", "")  # Gmail 주소
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # 앱 비밀번호 권장
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "noreply@example.com")


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """공통 SMTP 이메일 발송 함수"""
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP_USER 또는 SMTP_PASSWORD가 설정되어 있지 않습니다. 이메일을 발송할 수 없습니다.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email

        part = MIMEText(html_body, "html", _charset="utf-8")
        msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [to_email], msg.as_string())

        logger.info(f"이메일 발송 성공: {to_email}, subject={subject}")
        return True

    except Exception as e:
        logger.error(f"이메일 발송 중 오류: {str(e)}")
        return False


def send_password_reset_email(to_email: str, reset_token: str, app_url: str = "http://localhost:8000") -> bool:
    """비밀번호 재설정 이메일 발송 (Gmail SMTP)"""
    reset_link = f"{app_url}/reset-password?token={reset_token}"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #AD8B73;">비밀번호 재설정</h2>
            <p>안녕하세요,</p>
            <p>비밀번호 재설정을 요청하셨습니다. 아래 버튼을 클릭하여 새 비밀번호를 설정하세요.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #AD8B73; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    비밀번호 재설정하기
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">
                이 링크는 30분 동안 유효합니다.<br>
                비밀번호 재설정을 요청하지 않으셨다면 이 이메일을 무시하세요.
            </p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                의류 치수 측정 시스템<br>
                이 이메일은 자동으로 발송되었습니다.
            </p>
        </div>
    </body>
    </html>
    """

    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP 설정이 없어 개발 모드로 비밀번호 재설정 링크만 로그에 출력합니다.")
        logger.info(f"[개발 모드] 비밀번호 재설정 링크: {reset_link}")
        return False

    return _send_email(to_email, "[의류 치수 측정] 비밀번호 재설정", html_content)


def send_welcome_email(to_email: str, name: str) -> bool:
    """회원가입 환영 이메일 발송 (Gmail SMTP, 선택사항)"""
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #AD8B73;">환영합니다, {name}님!</h2>
            <p>의류 치수 측정 시스템에 가입해 주셔서 감사합니다.</p>
            <p>이제 A4 용지와 함께 의류를 촬영하여 정확한 치수를 측정할 수 있습니다.</p>
            <div style="margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
                <h3 style="color: #5C4033; margin-top: 0;">주요 기능</h3>
                <ul style="color: #666;">
                    <li>📸 간편한 모바일 촬영</li>
                    <li>📏 정밀한 치수 측정</li>
                    <li>👔 내 옷장 관리</li>
                    <li>✏️ 수동 조정 기능</li>
                </ul>
            </div>
            <p>궁금한 점이 있으시면 언제든지 문의해 주세요.</p>
        </div>
    </body>
    </html>
    """

    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP 설정이 없어 환영 이메일을 발송할 수 없습니다.")
        return False

    return _send_email(to_email, "[의류 치수 측정] 회원가입을 환영합니다!", html_content)


