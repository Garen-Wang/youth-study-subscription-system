import smtplib
from email.mime.text import MIMEText

import ver

from config import _mail_host, _mail_user, _mail_pass


class MailWorker:
    def __init__(self, host=_mail_host, user=_mail_user, ver=_mail_pass):
        self.host = host
        self.user = user
        self.ver = ver
        self.sender = None
        self.receiver = None
        self.message = None

    def write_message(self, subject, content, receiver, sender='garen-wang@qq.com'):
        self.sender = sender
        self.receiver = receiver
        self.message = MIMEText(content, 'plain', 'utf-8')
        self.message['Subject'] = subject
        self.message['From'] = sender
        self.message['To'] = receiver

    def send(self):
        if self.message is None:
            raise Exception('self.message is None')
        try:
            smtp_object = smtplib.SMTP()
            smtp_object.connect(self.host, 25)
            smtp_object.login(self.user, self.ver)
            smtp_object.sendmail(self.sender, self.receiver, self.message.as_string())
            smtp_object.quit()
            # print('sent')
        except smtplib.SMTPException as e:
            raise e


def test():
    mail_worker = MailWorker(_mail_host, _mail_user, _mail_pass)
    mail_worker.write_message('title', 'Hello, email!', 'garen-wang@outlook.com', 'garen-wang@qq.com')
    mail_worker.send()


def send(title, content, receiver):
    mail_worker = MailWorker(_mail_host, _mail_user, _mail_pass)
    mail_worker.write_message(title, content, receiver)
    mail_worker.send()


def send_verification_code(email_address):
    title = 'Youth Study Subscription System Verification Code'
    content = ver.generate(email_address)
    send(title, content, email_address)
    # print(content)


def send_reminder(email_address, name, season, episode):
    title = "Don't forget to get youth study done!"
    content = '''Dear {}:
    please finish Youth Study season {} episode {} when available in this week!
    Good good study, day day up!
    (This is an automatic reply, indicating that you still did not finish youth study at the last update.)
    '''.format(name, season, episode)
    send(title, content, email_address)

# test()
