from warden_logging import log
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
                        log.debug("Connecting..")
                        conn.connect(settings.EMAIL_HOST)
                        conn.set_debuglevel(False)

                        if settings.EMAIL_USE_TLS:
                            log.debug("Starting TLS..")
                            conn.starttls()

                        log.debug("Logging in..")
                        conn.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
                        log.debug("Sending mail..")
                        conn.sendmail(mail['From'], mail['To'], mail.as_string())
                        log.debug("Sent.")
                    except smtplib.SMTPRecipientsRefused:
                        log.error("Receipient confused.")
                    except smtplib.SMTPHeloError:
                        log.error("Server didn't respond properly to HELO.")
                    except smtplib.SMTPSenderRefused:
                        log.error("Sender refused.")
                    except smtplib.SMTPDataError:
                        log.error("Unexpected error code.")
                    except Exception as exc:
                        log.exception(exc)
                    finally:
                        if hasattr(conn, 'sock') and conn.sock:
                            conn.quit()

            time.sleep(self.SLEEP_INTERVAL)

CentralDispatcher().start()

