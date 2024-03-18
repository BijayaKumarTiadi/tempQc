import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.mime.text import MIMEText
import os
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime,timedelta

ZEPTO_USERNAME = os.environ.get('ZEPTO_USERNAME')
ZEPTO_PASSWD_KEY = os.environ.get('ZEPTO_PASSWD_KEY')
ZEPTO_SERVER = os.environ.get('ZEPTO_SERVER')
ZEPTO_PORT = int(os.environ.get('ZEPTO_PORT', 587))
ZEPTO_FROM = os.environ.get('ZEPTO_FROM')

port = 587
smtp_server = ZEPTO_SERVER
username = ZEPTO_USERNAME
password = ZEPTO_PASSWD_KEY

def zeptomail_send_email(subject, content, from_email, to_email):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = ZEPTO_FROM
        msg['To'] = ', '.join(to_email)

        msg.attach(MIMEText(content, 'html'))

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(username, password)

            server.send_message(msg)

        return {"status": "Success", "message": "Email sent successfully"}
    except Exception as e:
        raise Exception(str(e.smtp_error))
    
    
def zeptomail_send_email_with_attached(subject, content, from_email, to_email,document_buffer):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = ZEPTO_FROM
        msg['To'] = ', '.join(to_email)

        msg.attach(MIMEText(content, 'html'))                        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")   
        unique_filename = f"newsletter_doc_{timestamp}.docx"
        part = MIMEBase("application", "octet-stream")
        part.set_payload(document_buffer.getvalue())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {unique_filename}",
        )
        msg.attach(part)
        

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(username, password)

            server.send_message(msg)

        return {"status": "Success", "message": "Email sent successfully"}
    except Exception as e:
        raise Exception(str(e.smtp_error))