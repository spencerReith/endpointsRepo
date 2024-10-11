import random
import string
import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to_email
    user = "tindar.official@gmail.com"
    msg['from'] = user
    password = "hkmy zpyu lyyy qdfw"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

def send_verification_email(to_email):
    subject = "Tindar Verification – Urgent"
    emailKey = alphanumericString(8)
    body = "Your Tindar verification code: " + emailKey
    send_email(to_email, subject, body)
    return emailKey

def send_ref_email(email1, email2):
    subject = "Referral – Tindar – Urgent"
    body = "Someone has referred you to another applicant on Tindar."
    send_email(email1, subject, body)
    send_email(email2, subject, body)


def alphanumericString(length):
    possibleChars = string.ascii_letters + string.digits
    return ''.join(random.choice(possibleChars) for char in range(length))

if __name__ == '__main__':
    send_verification_email("spencer.k.reith.26@dartmouth.edu")
    # print("\nVerification email sent.\n")