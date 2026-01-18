import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
    
    def _create_smtp_connection(self):
        """Create and return SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            raise
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment: Optional[bytes] = None,
        attachment_filename: Optional[str] = None
    ) -> bool:
        """Send a single email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachment if provided
            if attachment and attachment_filename:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment_filename}'
                )
                msg.attach(part)
            
            # Send email
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(
        self,
        lead: Dict[str, Any],
        lead_magnet: Dict[str, Any],
        asset_bytes: Optional[bytes] = None
    ) -> bool:
        """Send welcome email with lead magnet"""
        subject = f"Your Free {lead_magnet.get('title', 'Resource')} is Here! 🎉"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #6366f1;">Hi {lead.get('name', 'there')}! 👋</h1>
                
                <p>Thanks for downloading <strong>{lead_magnet.get('title', 'your resource')}</strong>!</p>
                
                <p>{lead_magnet.get('value_promise', 'This resource will help you achieve great results.')}</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: #4f46e5; margin-top: 0;">What's Next?</h2>
                    <ul>
                        <li>Download your resource attached to this email</li>
                        <li>Review the content and start implementing</li>
                        <li>Watch for follow-up emails with additional tips</li>
                    </ul>
                </div>
                
                <p>If you have any questions, just reply to this email. I'm here to help!</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Your Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #6b7280;">
                    You're receiving this email because you downloaded {lead_magnet.get('title', 'a resource')} from our website.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Determine filename
        lead_type = lead_magnet.get('type', 'resource')
        filename = f"{lead_magnet.get('title', 'resource').replace(' ', '_')}.pdf"
        if lead_type == 'calculator':
            filename = filename.replace('.pdf', '.html')
        
        return self.send_email(
            to_email=lead.get('email'),
            subject=subject,
            body=body,
            attachment=asset_bytes,
            attachment_filename=filename
        )
    
    def send_nurture_email(
        self,
        lead: Dict[str, Any],
        email_template: Dict[str, Any]
    ) -> bool:
        """Send a nurture sequence email"""
        subject = email_template.get('subject', 'Quick tip for you')
        body_template = email_template.get('body', '')
        
        # Replace placeholders
        body = body_template.replace('{name}', lead.get('name', 'there'))
        body = body.replace('{{name}}', lead.get('name', 'there'))
        
        # Wrap in HTML template
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                {body.replace(chr(10), '<br>')}
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Your Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #6b7280;">
                    You're receiving this email as part of our nurture sequence.
                    <a href="#" style="color: #6366f1;">Unsubscribe</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=lead.get('email'),
            subject=subject,
            body=html_body
        )
    
    def send_upgrade_offer_email(
        self,
        lead: Dict[str, Any],
        upgrade_offer: Dict[str, Any]
    ) -> bool:
        """Send upgrade offer email"""
        subject = f"Special Offer: {upgrade_offer.get('title', 'Upgrade Available')}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #6366f1;">Hi {lead.get('name', 'there')}! 🚀</h1>
                
                <p>I hope you've been enjoying the resource you downloaded!</p>
                
                <h2 style="color: #4f46e5;">{upgrade_offer.get('title', 'Special Offer')}</h2>
                
                <p>{upgrade_offer.get('description', 'Take your results to the next level with this special offer.')}</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{upgrade_offer.get('link', '#')}" 
                       style="display: inline-block; background: #6366f1; color: white; 
                              padding: 15px 30px; text-decoration: none; border-radius: 5px;
                              font-weight: bold;">
                        Learn More →
                    </a>
                </div>
                
                <p>Have questions? Just reply to this email!</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Your Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=lead.get('email'),
            subject=subject,
            body=body
        )
    
    def send_bulk_emails(
        self,
        leads: List[Dict[str, Any]],
        email_template: Dict[str, Any]
    ) -> Dict[str, int]:
        """Send emails to multiple leads"""
        results = {'success': 0, 'failed': 0}
        
        for lead in leads:
            success = self.send_nurture_email(lead, email_template)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Bulk email results: {results['success']} sent, {results['failed']} failed")
        return results