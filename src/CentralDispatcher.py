import settings
import smtplib
import time
from smtplib import SMTP
import BaseMailGenerator
from GraphiteMailGenerator import GraphiteMailGenerator

class CentralDispatcher(object):

    SLEEP_INTERVAL = 30

    def start(self):
        while True:
            for generator_cls in BaseMailGenerator.generator_registry:
                generator = generator_cls()
                mail = generator.create_mail()

                if mail:
                    conn = SMTP()
                    try:
                        print "Connecting.."
                        conn.connect(settings.EMAIL_HOST)
                        conn.set_debuglevel(False)

                        if settings.EMAIL_USE_TLS:
                            print "Starting TLS.."
                            conn.starttls()

                        print "Logging in.."
                        conn.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
                        print "Sending mail.."
                        conn.sendmail(mail['From'], mail['To'], mail.as_string())
                        print "Sent."
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

            time.sleep(self.SLEEP_INTERVAL)

CentralDispatcher().start()

