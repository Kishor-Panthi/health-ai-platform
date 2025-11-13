"""
Twilio SMS Service
Handles SMS communications for appointments, reminders, and alerts
"""
from twilio.rest import Client
from typing import Dict, Optional
import os
import structlog
from datetime import datetime

logger = structlog.get_logger()


class SMSService:
    """
    SMS service using Twilio
    """

    def __init__(self):
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_number = os.environ.get('TWILIO_PHONE_NUMBER')

        if not all([account_sid, auth_token, self.from_number]):
            logger.warning("Twilio not configured - SMS will be logged only")
            self.client = None
        else:
            self.client = Client(account_sid, auth_token)

    async def send_sms(
        self,
        to_number: str,
        message: str
    ) -> Dict:
        """
        Send SMS message

        Args:
            to_number: Phone number in E.164 format (+15551234567)
            message: SMS message content (max 1600 characters)

        Returns:
            Dict with success status and details
        """
        try:
            # Validate phone number format
            if not to_number.startswith('+'):
                # Assume US number if no country code
                to_number = f'+1{to_number.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")}'

            # Truncate message if too long
            if len(message) > 1600:
                message = message[:1597] + "..."
                logger.warning("sms_message_truncated", to=to_number, original_length=len(message))

            logger.info("sending_sms", to=to_number, length=len(message))

            # If no client configured, just log
            if not self.client:
                logger.warning("sms_not_sent_no_config", to=to_number, message=message)
                return {
                    'success': False,
                    'error': 'SMS service not configured',
                    'logged_only': True
                }

            # Send via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )

            logger.info(
                "sms_sent",
                to=to_number,
                sid=twilio_message.sid,
                status=twilio_message.status
            )

            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'to': twilio_message.to,
                'sent_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("sms_send_failed", to=to_number, error=str(e), exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def send_appointment_reminder(
        self,
        phone_number: str,
        appointment: Dict
    ) -> Dict:
        """Send appointment reminder SMS"""
        message = f"""
Appointment Reminder:
Date: {appointment['appointment_date']}
Time: {appointment['start_time']}
Provider: Dr. {appointment.get('provider_name', 'TBD')}

Please call (555) 123-4567 to cancel/reschedule.
Reply STOP to opt out.
        """.strip()

        return await self.send_sms(phone_number, message)

    async def send_verification_code(
        self,
        phone_number: str,
        code: str
    ) -> Dict:
        """Send verification code for MFA"""
        message = f"""
Your verification code is: {code}

This code expires in 10 minutes.
Do not share this code with anyone.

Reply STOP to opt out.
        """.strip()

        return await self.send_sms(phone_number, message)

    async def send_prescription_ready(
        self,
        phone_number: str,
        pharmacy_name: str,
        medication_name: str
    ) -> Dict:
        """Notify patient prescription is ready for pickup"""
        message = f"""
Your prescription for {medication_name} is ready for pickup at {pharmacy_name}.

Reply STOP to opt out.
        """.strip()

        return await self.send_sms(phone_number, message)

    async def send_lab_results_notification(
        self,
        phone_number: str
    ) -> Dict:
        """Notify patient that lab results are available"""
        message = """
Your lab results are now available in your patient portal.
Log in to view: https://portal.youreHR.com

Reply STOP to opt out.
        """.strip()

        return await self.send_sms(phone_number, message)

    async def send_appointment_confirmed(
        self,
        phone_number: str,
        appointment: Dict
    ) -> Dict:
        """Send appointment confirmation SMS"""
        message = f"""
Appointment Confirmed!
{appointment['appointment_date']} at {appointment['start_time']}
Dr. {appointment.get('provider_name', 'TBD')}

Call (555) 123-4567 for changes.
Reply STOP to opt out.
        """.strip()

        return await self.send_sms(phone_number, message)

    async def get_message_status(self, message_sid: str) -> Dict:
        """
        Check status of sent message

        Returns:
            Dict with status: queued, sending, sent, failed, delivered, undelivered
        """
        if not self.client:
            return {'success': False, 'error': 'SMS service not configured'}

        try:
            message = self.client.messages(message_sid).fetch()

            return {
                'success': True,
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'date_sent': message.date_sent,
                'error_code': message.error_code,
                'error_message': message.error_message
            }

        except Exception as e:
            logger.error("get_message_status_failed", sid=message_sid, error=str(e))
            return {'success': False, 'error': str(e)}


# Global instance
sms_service = SMSService()
