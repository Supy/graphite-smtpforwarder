from email.mime.base import MIMEBase
from email import encoders

generator_registry = []

def register_generator(cls):
    generator_registry.append(cls)
    return cls

class BaseMailGenerator(object):

    def create_mail(self):
        pass

    def create_attachment(self, path, name):
        ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        try:
            fp = open(path, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=name)
            return msg
        except IOError:
            print "Error reading contents of %s" % path
        finally:
            fp.close()

        return None