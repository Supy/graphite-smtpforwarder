import settings
import time
import os
import email
import string
import smtplib
import sys
from smtplib import SMTP

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def start():
    if settings.EMAIL_TO == '':
        exit_with_error('No receiver email address defined.')

    if not os.path.isdir(settings.WHISPER_STORAGE_PATH):
        exit_with_error('Invalid whisper storage path specified.')

    mail = MIMEMultipart()
    mail['To'] = settings.EMAIL_TO
    mail['From'] = settings.EMAIL_FROM
    mail['Subject'] = settings.EMAIL_SUBJECT_VALIDATION_KEY

    content = MIMEText(settings.EMAIL_BODY_VALIDATION_KEY)
    mail.attach(content)

    attached_files = 0

    print "Scanning for files.."
    for path in walk_directory(settings.WHISPER_STORAGE_PATH):
        attachment = setup_attachment(path)

        if attachment:
            mail.attach(attachment)
            attached_files += 1

    print "Found %d files for sending." % attached_files
    if attached_files > 0:
        try:
            print "Connecting.."
            conn = SMTP(settings.EMAIL_HOST)
            conn.set_debuglevel(False)

            if settings.EMAIL_USE_TLS:
                print "Starting TLS.."
                conn.starttls()

            print "Logging in.."
            conn.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            print "Sending mail.."
            conn.sendmail(mail['From'], mail['To'], mail.as_string())
            print "Sent %d attachments." % attached_files
        except smtplib.SMTPRecipientsRefused:
            print "Receipient confused."
        except smtplib.SMTPHeloError:
            print "Server didn't respond properly to HELO."
        except smtplib.SMTPSenderRefused:
            print "Sender refused."
        except smtplib.SMTPDataError:
            print "Unexpected error code."
        except Exception as exc:
            print exc
        finally:
            if hasattr(conn, 'sock') and conn.sock:
                conn.quit()

def setup_attachment(path):
    ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    # Read in the contents of the attachment
    try:
        fp = open(path, 'rb')
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(fp.read())
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=path_to_metric_filename(path))

        return msg
    except IOError:
        print "Error reading contents of %s" % path
    finally:
        fp.close()

    return None

def walk_directory(path):
    if isinstance(path, str):
        for root, folders, files in os.walk(path):
            for f in select_files(root, files):
                yield f
    elif isinstance(path, list) or isinstance(path, tuple):
        for p in path:
            if not os.path.isdir(p):
                continue

            for root, folders, files in os.walk(p):
                for f in select_files(root, files):
                    yield f

def select_files(dir, files):
    for filename in files:
        extension = os.path.splitext(filename)[1].strip()
        if extension == '.wsp':
            yield os.path.join(dir, filename)

def path_to_metric_filename(full_path):
    relevant_path = full_path[len(settings.WHISPER_STORAGE_PATH):].strip(os.sep)
    metric_filename = relevant_path.replace(os.sep, '.')
    return metric_filename

def exit_with_error(msg):
    print msg
    sys.exit()

start()

