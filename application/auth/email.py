import requests
import smtplib
from email.mime.text import MIMEText
from flask import current_app, render_template
from flask_mail import Message
from flask_babel import _
from application import mail
from threading import Thread  # multiprocessing is an alternative module



# https://pythonhosted.org/Flask-Mail/
# FLASK-MAIL implementaiton
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
    #current_app._get_current_object() extracts the actual application instance from inside the proxy object


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
                sender=current_app.config['ADMINS'][0],
                recipients=[user.email],
                text_body=render_template('email/reset_password.txt',
                                          user=user, token=token),
                html_body=render_template('email/reset_password.html',
                                          user=user, token=token))


### REFERENCE CODE

'''
# MAILGUN SMTP implementation
def send_async_email(app, msg):
    with app.app_context():
        s = smtplib.SMTP(current_app.config['MAILGUN_SERVER'],
                         current_app.config['MAILGUN_PORT'])

        s.login('postmaster@' + current_app.config['MAILGUN_DOMAIN'],
                current_app.config['MAILGUN_PW'])
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()


def send_email(subject, sender, recipients, text_body, html_body):
    # TODO REGISTER DOMAIN, PUT VALID CREDIT CARD ON FILE W/ MAILGUN
    msg = MIMEText(text_body)
    msg['Subject'] = subject
    msg['From'] = sender + "@" + current_app.config['MAILGUN_DOMAIN']
    msg['To'] = recipients  # must be verified accounts until DNS is verified
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
    #current_app._get_current_object() extracts the actual application instance from inside the proxy object

'''

def mailgun_api():
    # TODO - make functional
    p = requests.post(
        "https://api.mailgun.net/v3/sandboxa341bc8908f24a8eb52bee693f305a3f.mailgun.org",
        auth=("api", current_app.config['MAILGUN_KEY']),
        data={"from": "mailgun@sandboxa341bc8908f24a8eb52bee693f305a3f.mailgun.org",
              "to": ["info@bedfordap.com", "bedforap1@gmail.com"],
              "subject": "Hello",
              "text": "Testing some Mailgun awesomness! API"})
    return p
# You can see a record of this email in your logs: https://app.mailgun.com/app/logs.
# You can send up to 300 emails/day from this sandbox server.
# Next, you should add your own domain so you can send 10000 emails/month for free.
