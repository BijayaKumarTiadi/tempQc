import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import os


SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_EMAIL = os.environ.get('SENDGRID_EMAIL')


def sendgrid_send_mail(subject, content, from_email, to_email):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        from_email = Email(from_email)
        to_email = to_email
        message = Content("text/html", content)
        mail = Mail(from_email, to_email, subject, message)
        response = sg.client.mail.send.post(request_body=mail.get())
        
        if response.status_code == 202:
            return {"status": "Success", "message": "Email sent successfully"}
        else:
            raise Exception("Email sent failed")

    except Exception as e:
        return {"status": "Error", "message": str(e)}