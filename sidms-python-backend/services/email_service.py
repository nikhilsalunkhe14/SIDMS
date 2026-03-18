import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('MAIL_PORT', 587))
        self.username = os.getenv('MAIL_USERNAME')
        self.password = os.getenv('MAIL_PASSWORD')
        self.use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    
    def send_email(self, to_email, subject, body, is_html=False):
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_otp_email(self, to_email, otp_code):
        subject = "Your SIDMS OTP Code"
        body = f"""
        Hello,
        
        Your One-Time Password (OTP) for SIDMS is: {otp_code}
        
        This OTP will expire in 5 minutes.
        
        If you didn't request this OTP, please ignore this email.
        
        Best regards,
        SIDMS Team
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_verification_email(self, to_email, verification_link):
        subject = "Verify Your SIDMS Account"
        body = f"""
        Hello,
        
        Thank you for registering with SIDMS. Please click the link below to verify your email:
        
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        SIDMS Team
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_welcome_email(self, to_email, username):
        subject = "Welcome to SIDMS"
        body = f"""
        Hello {username},
        
        Welcome to the Secure IAC Data Management System (SIDMS)!
        
        Your account has been successfully created and verified.
        
        You can now log in and start using the system.
        
        Best regards,
        SIDMS Team
        """
        
        return self.send_email(to_email, subject, body)
