from datetime import datetime, timedelta
import re
from unidecode import unidecode
import bcrypt


class SomeUtils:
    @staticmethod
    def beedoc_to_dict(beedoc):
        return {
            'id': beedoc.id,
            'author': beedoc.author,
            'title': beedoc.title,
            'category': beedoc.category.name,
            'time': beedoc.time,
            'comments': beedoc.comments,
            'likes': beedoc.likes,
            'dislikes': beedoc.dislikes,
            'data': beedoc.data
        }

    @staticmethod
    def pass_encrypt(password):
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))
        return hashed

    @staticmethod
    def pass_decrypt(password, hashed):
        if bcrypt.hashpw(password, hashed) == hashed:
            return True
        else:
            return False

    @staticmethod
    def comment_to_dict(comment):
        return {
            'beedoc': comment.beedoc,
            'author': comment.author,
            'time': comment.time,
            'data': comment.data
        }

    @staticmethod
    def flash_to_dict(falsh):
        return {
            'id': falsh.id,
            'author': falsh.author,
            'time': falsh.time,
            'text': falsh.text
        }

    @staticmethod
    def to_unicode(text):
        res = text
        if not isinstance(res, unicode):
            try:
                res = unicode(res, "utf-8")
            except UnicodeDecodeError:
                res = unicode(res, "ISO-8859-1")
        res = unidecode(res)
        return res

    @staticmethod
    def normalize_name(name):
        res = name
        if not isinstance(res, unicode):
            try:
                res = unicode(res, "utf-8")
            except UnicodeDecodeError:
                res = unicode(res, "ISO-8859-1")
        res = unidecode(res)
        # we take out anything in brackets
        i = res.find('(')
        if i != -1:
            j = res.find(')')
            res = res[0:i:1] + res[j+1::]
        res = re.sub('[^0-9a-zA-Z]+', ' ', res)
        res = re.sub(' +', '', res)
        res = res.lower()
        res = res.strip()

        return res

    @staticmethod
    def generate_word(length):
        import string
        from random import choice
        chars = string.letters + string.digits
        word = ''.join([choice(chars) for _ in xrange(length)])
        return word

    @staticmethod
    def generate_timestamp():
        return datetime.now().strftime("%s")

    @staticmethod
    def generate_id(data):
        word1 = SomeUtils.generate_word(2)
        word2 = SomeUtils.generate_word(3)
        if 'title' in data.keys():
            return word1 + SomeUtils.normalize_name(data['title']) + word2 + data['author']
        else:
            return word1 + SomeUtils.normalize_name(data['text']) + word2 + data['author']

    @staticmethod
    def genarate_token(email, length):
        word1 = SomeUtils.generate_word(4)
        word2 = SomeUtils.generate_word(8)

        user = email.split('@')[0]
        # length is in hours
        expiration_date = datetime.now() + timedelta(hours=length)
        token = word1 + str(expiration_date.strftime("%s")) + word2 + user + str(len(user))
        return token

    @staticmethod
    def generate_pass():
        return SomeUtils.generate_word(16)

    @staticmethod
    def token_checker(token):
        last_part_len = int(token[::-1][0]) + 1
        expiration_date = long(token[4::][::-1][(8 + last_part_len)::][::-1])
        now = long(datetime.now().strftime("%s"))
        if now > expiration_date:
            return False
        return True

    @staticmethod
    def mail_checker(email):
        # Only enseirb-matmeca is accepted
        parts = email.split('@')
        if len(parts) != 2:
            return False
        if parts[1] == 'enseirb-matmeca.fr':
            return True
        else:
            return False

    @staticmethod
    def send_mail(email, password, title):
        """
        Send mail from beenewseirb@gmail.com
        :param email:
        :return: confirmation notice or error
        """
        import smtplib
        import string

        fromaddr = 'BeeNews'
        subject = title
        msg = 'Hi!\nThank you for subscribing to BeeNews.\nHere is your password: ' + password + \
              '\nYou need to change it ASAP\nEnjoy!'
        body = string.join((
            "From: %s" % fromaddr,
            "To: %s" % email,
            "Subject: %s" % subject,
            "",
            msg,
            ), "\r\n"
        )

        # Credentials (if needed)
        username = 'beenewseirb@gmail.com'
        password = 'ladotevirherveux'

        # The actual mail send
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, email, body)
        server.quit()
