from settings import *
import time
import os
import email
import string

if EMAIL_USE_SSL:
    from smtplib import SMTP_SSL as SMTP
else:
    from smtplib import SMTP

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def start():
    mail = MIMEMultipart()
    mail['To'] = EMAIL_TO
    mail['From'] = EMAIL_FROM
    mail['Subject'] = EMAIL_SUBJECT_VALIDATION_KEY

    content = MIMEText(EMAIL_BODY_VALIDATION_KEY)
    mail.attach(content)
    files = walk_directory(WHISPER_STORAGE_PATH)

    for path in files:
        if not os.path.isfile(path):
            continue

        attachment = setup_attachment(path)
        mail.attach(attachment)

    try:
        conn = SMTP(EMAIL_HOST)
        conn.set_debuglevel(False)
        conn.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        try:
            conn.sendmail(mail['From'], mail['To'], mail.as_string())
        finally:
            conn.close()

    except Exception, exc:
        print str(exc)

def setup_attachment(path):
    ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    # Read in the contents of the attachment
    fp = open(path, 'rb')
    msg = MIMEBase(maintype, subtype)
    msg.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment', filename=path_to_metric_filename(path))

    return msg

def walk_directory(path):
    file_list = []
    if isinstance(path, str):
        for root, folders, files in os.walk(path):
            file_list.extend(select_files(root, files))
    elif isinstance(path, list) or isinstance(path, tuple):
        paths = path
        for path in paths:
            for root, folders, files in os.walk(path):
                file_list.extend(select_files(root, files))

    return file_list

def select_files(dir, files):
    file_list = []
    for filename in files:
        extension = os.path.splitext(filename)[1].strip()
        if extension == '.wsp':
            file_list.append(os.path.join(dir, filename))
    return file_list


def path_to_metric_filename(full_path):
    relevant_path = full_path[len(WHISPER_STORAGE_PATH):].strip(os.sep)
    metric_filename = relevant_path.replace(os.sep, '.')
    return metric_filename


start()

