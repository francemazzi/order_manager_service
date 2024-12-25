from flask import current_app
from flask_mail import Message
from threading import Thread
from extensions import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body=None):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_welcome_email(user):
    subject = "Benvenuto in Order Manager!"
    text_body = f"""
    Ciao {user.first_name or user.email},
    
    Grazie per esserti registrato su Order Manager!
    
    Il tuo account è stato creato con successo.
    
    Cordiali saluti,
    Il team di Order Manager
    """
    
    html_body = f"""
    <h1>Benvenuto in Order Manager!</h1>
    <p>Ciao {user.first_name or user.email},</p>
    <p>Grazie per esserti registrato su Order Manager!</p>
    <p>Il tuo account è stato creato con successo.</p>
    <br>
    <p>Cordiali saluti,<br>
    Il team di Order Manager</p>
    """
    
    send_email(subject, [user.email], text_body, html_body) 