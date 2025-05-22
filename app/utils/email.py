"""
Email utility functions
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> None:
    """
    Send an email
    
    In a production environment, this would use an email sending service
    like SendGrid, Mailgun, or AWS SES. For now, we just log the email.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content of the email (optional)
    """
    # For now, just log the email
    logger.info(
        f"Email sent to {email_to} with subject: {subject}"
    )
    
    # TODO: Implement actual email sending
    # Examples:
    
    # Using SendGrid:
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    # message = Mail(
    #     from_email=settings.EMAILS_FROM_EMAIL,
    #     to_emails=email_to,
    #     subject=subject,
    #     html_content=html_content
    # )
    # if text_content:
    #     message.plain_text_content = text_content
    # try:
    #     sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    #     sg.send(message)
    # except Exception as e:
    #     logger.error(f"Error sending email: {e}")
    
    # Using SMTP:
    # import smtplib
    # from email.mime.multipart import MIMEMultipart
    # from email.mime.text import MIMEText
    # message = MIMEMultipart("alternative")
    # message["Subject"] = subject
    # message["From"] = settings.EMAILS_FROM_EMAIL
    # message["To"] = email_to
    # if text_content:
    #     message.attach(MIMEText(text_content, "plain"))
    # message.attach(MIMEText(html_content, "html"))
    # try:
    #     with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
    #         server.starttls()
    #         server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    #         server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
    # except Exception as e:
    #     logger.error(f"Error sending email: {e}")


def send_verification_email(email_to: str, token: str) -> None:
    """
    Send email verification link
    
    Args:
        email_to: Recipient email address
        token: Verification token
    """
    subject = f"{settings.PROJECT_NAME} - Verify Your Email"
    
    # Link to frontend verification page
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    html_content = f"""
    <p>Hi there,</p>
    <p>Thank you for registering with {settings.PROJECT_NAME}!</p>
    <p>Please click the link below to verify your email address:</p>
    <p><a href="{verification_link}">Verify Email</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p>{verification_link}</p>
    <p>This link will expire in 24 hours.</p>
    <p>Best regards,</p>
    <p>{settings.PROJECT_NAME} Team</p>
    """
    
    text_content = f"""
    Hi there,
    
    Thank you for registering with {settings.PROJECT_NAME}!
    
    Please click the link below to verify your email address:
    {verification_link}
    
    This link will expire in 24 hours.
    
    Best regards,
    {settings.PROJECT_NAME} Team
    """
    
    send_email(email_to, subject, html_content, text_content)


def send_reset_password_email(email_to: str, token: str) -> None:
    """
    Send password reset link
    
    Args:
        email_to: Recipient email address
        token: Password reset token
    """
    subject = f"{settings.PROJECT_NAME} - Reset Your Password"
    
    # Link to frontend reset password page
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html_content = f"""
    <p>Hi there,</p>
    <p>You have requested to reset your password for {settings.PROJECT_NAME}.</p>
    <p>Please click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p>{reset_link}</p>
    <p>This link will expire in 4 hours.</p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>Best regards,</p>
    <p>{settings.PROJECT_NAME} Team</p>
    """
    
    text_content = f"""
    Hi there,
    
    You have requested to reset your password for {settings.PROJECT_NAME}.
    
    Please click the link below to reset your password:
    {reset_link}
    
    This link will expire in 4 hours.
    
    If you did not request a password reset, please ignore this email.
    
    Best regards,
    {settings.PROJECT_NAME} Team
    """
    
    send_email(email_to, subject, html_content, text_content)


def send_welcome_email(email_to: str) -> None:
    """
    Send welcome email
    
    Args:
        email_to: Recipient email address
    """
    subject = f"Welcome to {settings.PROJECT_NAME}"
    
    html_content = f"""
    <p>Hi there,</p>
    <p>Thank you for joining {settings.PROJECT_NAME}!</p>
    <p>We're excited to have you as part of our community.</p>
    <p>You can now access your account and explore our services.</p>
    <p>Best regards,</p>
    <p>{settings.PROJECT_NAME} Team</p>
    """
    
    text_content = f"""
    Hi there,
    
    Thank you for joining {settings.PROJECT_NAME}!
    
    We're excited to have you as part of our community.
    
    You can now access your account and explore our services.
    
    Best regards,
    {settings.PROJECT_NAME} Team
    """
    
    send_email(email_to, subject, html_content, text_content)