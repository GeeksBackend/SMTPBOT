from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib, os

load_dotenv('.env')

def send_mail(title:str, message:str, to_user:str) -> str:
    sender = os.environ.get('smtp_email')
    password = os.environ.get('smtp_password')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    msg = EmailMessage()
    msg['Subject'] = title
    msg['From'] = os.environ.get('SMTP_EMAIL')
    msg['To'] = to_user
    msg.set_content(message)

    try:
        server.login(sender, password)
        server.send_message(msg)
        return "Send Mail Success"
    except Exception as error:
        return f"Error {error}"
# print(send_mail("Geeks Osh", "Здраствуйте сегодня у вас урок в 20:00", "ktoktorov144@gmail.com"))

emails = ['ktoktorov144@gmail.com', 'toktorovkurmanbek92@gmail.com', "toktoroveldos15@gmail.com",
        'nursultandev@gmail.com', 'bekakasymjanov@gmail.com']
def mailing_email(email_list:list) -> str:
    for email in email_list: #Заголовок: Здраствуйте {email} Текст: Это рассылка сделана через Python SMTP
        print(send_mail(f"Здраствуйте {email}", "Это рассылка сделана через Python SMTP", email))
mailing_email(emails)