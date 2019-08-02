from flask import current_app, render_template
from flask_mail import Message
from flask_babel import _
from application import mail
from threading import Thread  # multiprocessing is an alternative module
# https://pythonhosted.org/Flask-Mail/


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


    ''' current_app._get_current_object() extracts the actual application
    instance from inside the proxy object'''

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
                sender=current_app.config['ADMINS'][0],
                recipients=[user.email],
                text_body=render_template('email/reset_password.txt',
                                          user=user, token=token),
                html_body=render_template('email/reset_password.html',
                                          user=user, token=token))
