"""
SendGrid Email Service
Handles all email communications with proper HIPAA compliance
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import List, Optional, Dict
import os
import structlog
from datetime import datetime

logger = structlog.get_logger()


class EmailService:
    """
    Email service using SendGrid
    """

    def __init__(self):
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            logger.warning("SENDGRID_API_KEY not set - emails will be logged only")
            self.client = None
        else:
            self.client = SendGridAPIClient(api_key)

        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@youreHR.com')
        self.from_name = os.environ.get('FROM_NAME', 'Your EHR')

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Send email via SendGrid

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
            reply_to: Reply-to email address (optional)
            attachments: List of attachments (optional)

        Returns:
            Dict with success status and details
        """
        try:
            # Log email for debugging/compliance
            logger.info(
                "sending_email",
                to=to_email,
                subject=subject,
                has_attachments=bool(attachments)
            )

            # If no client configured, just log
            if not self.client:
                logger.warning(
                    "email_not_sent_no_config",
                    to=to_email,
                    subject=subject
                )
                return {
                    'success': False,
                    'error': 'Email service not configured',
                    'logged_only': True
                }

            # Build message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            # Add plain text version
            if text_content:
                message.add_content(Content("text/plain", text_content))

            # Add reply-to
            if reply_to:
                message.reply_to = Email(reply_to)

            # Add attachments
            if attachments:
                from sendgrid.helpers.mail import Attachment, FileContent, FileName, FileType, Disposition
                for att in attachments:
                    attachment = Attachment()
                    attachment.file_content = FileContent(att['content'])
                    attachment.file_name = FileName(att['filename'])
                    attachment.file_type = FileType(att.get('type', 'application/octet-stream'))
                    attachment.disposition = Disposition('attachment')
                    message.add_attachment(attachment)

            # Send
            response = self.client.send(message)

            logger.info(
                "email_sent",
                to=to_email,
                status_code=response.status_code,
                message_id=response.headers.get('X-Message-Id')
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'sent_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(
                "email_send_failed",
                to=to_email,
                error=str(e),
                exc_info=True
            )
            return {
                'success': False,
                'error': str(e)
            }

    async def send_appointment_confirmation(
        self,
        patient_email: str,
        appointment: Dict
    ) -> Dict:
        """Send appointment confirmation email"""
        subject = f"Appointment Confirmation - {appointment['appointment_date']}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Appointment Confirmed</h2>

            <p>Your appointment has been scheduled:</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Date:</strong> {appointment['appointment_date']}</p>
                <p><strong>Time:</strong> {appointment['start_time']}</p>
                <p><strong>Provider:</strong> Dr. {appointment.get('provider_name', 'TBD')}</p>
                <p><strong>Type:</strong> {appointment.get('appointment_type', 'Office Visit')}</p>
            </div>

            <p><strong>Location:</strong><br>
            123 Medical Center Dr<br>
            Suite 100<br>
            Your City, ST 12345</p>

            <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                Please arrive 15 minutes early to complete any necessary paperwork.
                If you need to cancel or reschedule, please call us at (555) 123-4567
                at least 24 hours in advance.
            </p>

            <p style="margin-top: 30px; font-size: 12px; color: #9ca3af;">
                This email may contain confidential health information protected by HIPAA.
                If you received this in error, please delete it immediately.
            </p>
        </body>
        </html>
        """

        text_content = f"""
        Appointment Confirmed

        Your appointment has been scheduled:

        Date: {appointment['appointment_date']}
        Time: {appointment['start_time']}
        Provider: Dr. {appointment.get('provider_name', 'TBD')}
        Type: {appointment.get('appointment_type', 'Office Visit')}

        Location:
        123 Medical Center Dr, Suite 100
        Your City, ST 12345

        Please arrive 15 minutes early. To cancel or reschedule, call (555) 123-4567
        at least 24 hours in advance.
        """

        return await self.send_email(
            to_email=patient_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    async def send_appointment_reminder(
        self,
        patient_email: str,
        appointment: Dict
    ) -> Dict:
        """Send appointment reminder email"""
        subject = f"Appointment Reminder - Tomorrow at {appointment['start_time']}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Appointment Reminder</h2>

            <p>This is a friendly reminder about your upcoming appointment:</p>

            <div style="background-color: #fef3c7; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                <p><strong>Tomorrow - {appointment['appointment_date']}</strong></p>
                <p><strong>Time:</strong> {appointment['start_time']}</p>
                <p><strong>Provider:</strong> Dr. {appointment.get('provider_name', 'TBD')}</p>
            </div>

            <p>We look forward to seeing you!</p>

            <p style="margin-top: 20px; font-size: 14px; color: #6b7280;">
                Need to cancel or reschedule? Call us at (555) 123-4567
            </p>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=patient_email,
            subject=subject,
            html_content=html_content
        )

    async def send_lab_results_notification(
        self,
        patient_email: str,
        patient_name: str
    ) -> Dict:
        """Notify patient that lab results are available"""
        subject = "New Lab Results Available"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Lab Results Available</h2>

            <p>Hello {patient_name},</p>

            <p>Your recent lab results are now available in your patient portal.</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>To view your results:</strong></p>
                <ol>
                    <li>Log in to your patient portal</li>
                    <li>Navigate to "Medical Records"</li>
                    <li>Select "Lab Results"</li>
                </ol>
            </div>

            <p>If you have any questions about your results, please contact your provider's office.</p>

            <p style="margin-top: 30px; font-size: 12px; color: #9ca3af;">
                This email contains confidential health information. If you received this in error,
                please delete it immediately and contact us.
            </p>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=patient_email,
            subject=subject,
            html_content=html_content
        )

    async def send_password_reset(
        self,
        email: str,
        reset_token: str,
        portal_url: str
    ) -> Dict:
        """Send password reset email"""
        reset_link = f"{portal_url}/auth/reset-password?token={reset_token}"

        subject = "Password Reset Request"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Password Reset Request</h2>

            <p>We received a request to reset your password. Click the button below to create a new password:</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}"
                   style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    Reset Password
                </a>
            </div>

            <p style="font-size: 14px; color: #6b7280;">
                This link will expire in 24 hours. If you didn't request this, you can safely ignore this email.
            </p>

            <p style="font-size: 14px; color: #6b7280;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <code style="background-color: #f3f4f6; padding: 8px; display: block; margin-top: 8px; word-break: break-all;">
                {reset_link}
                </code>
            </p>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content
        )

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict:
        """
        Send email to multiple recipients (max 1000 per call)
        """
        if len(recipients) > 1000:
            return {
                'success': False,
                'error': 'Maximum 1000 recipients per bulk send'
            }

        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=[To(email) for email in recipients],
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            if text_content:
                message.add_content(Content("text/plain", text_content))

            response = self.client.send(message)

            logger.info(
                "bulk_email_sent",
                recipient_count=len(recipients),
                status_code=response.status_code
            )

            return {
                'success': True,
                'recipient_count': len(recipients),
                'status_code': response.status_code
            }

        except Exception as e:
            logger.error("bulk_email_failed", error=str(e), exc_info=True)
            return {'success': False, 'error': str(e)}


# Global instance
email_service = EmailService()
