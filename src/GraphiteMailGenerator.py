import settings
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from warden_logging import log

import BaseMailGenerator

@BaseMailGenerator.register_generator
class GraphiteMailGenerator(BaseMailGenerator.BaseMailGenerator):

    def create_mail(self):
        if not settings.EMAIL_TO or settings.EMAIL_TO == '':
            log.error('No receiver email address defined.')
            return None

        if not os.path.isdir(settings.WHISPER_STORAGE_PATH):
            log.error('Invalid whisper storage path specified.')
            return None

        mail = self._setup_mail()
        files = self._attach_files(mail)
        return mail if (files > 0) else None

    def _setup_mail(self):
        mail = MIMEMultipart()
        mail['To'] = settings.EMAIL_TO
        mail['From'] = settings.EMAIL_FROM
        mail['Subject'] = settings.EMAIL_SUBJECT_VALIDATION_KEY
        mail.attach(MIMEText(settings.EMAIL_BODY_VALIDATION_KEY))
        return mail

    def _attach_files(self, mail):
        attached_files = 0
        log.debug("Scanning for files..")
        for path in self._walk_directory(settings.WHISPER_STORAGE_PATH):
            attachment = self.create_attachment(path, self._path_to_metric_filename(path))
            if attachment:
                mail.attach(attachment)
                attached_files += 1
        log.debug("Found %d files for sending." % attached_files)
        return attached_files

    def _walk_directory(self, path):
        if isinstance(path, str):
            for root, folders, files in os.walk(path):
                for f in self._select_files(root, files):
                    yield f
        elif isinstance(path, list) or isinstance(path, tuple):
            for p in path:
                if not os.path.isdir(p):
                    continue

                for root, folders, files in os.walk(p):
                    for f in self._select_files(root, files):
                        yield f

    def _select_files(self, dir, files):
        for filename in files:
            extension = os.path.splitext(filename)[1].strip()
            if extension == '.wsp':
                yield os.path.join(dir, filename)

    def _path_to_metric_filename(self, full_path):
        relevant_path = full_path[len(settings.WHISPER_STORAGE_PATH):].strip(os.sep)
        metric_filename = relevant_path.replace(os.sep, '.')
        return metric_filename