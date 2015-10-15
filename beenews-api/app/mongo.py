import json
from flask import Blueprint, request, jsonify, render_template, url_for
from mongoengine import *
from .app_utils import requires_token
from contrib.some_utils import SomeUtils
from contrib.category_utils import CategoryUtils
from datetime import datetime

mongo = Blueprint('mongo', __name__)

# Connect to the database
@mongo.record_once
def connect_to_base(setup_state):
    CONF = setup_state.app.config
    connect(db=CONF['MONGO_DB'], host=CONF['MONGO_HOST'], port=27017)
    register_connection(alias='default', name=CONF['MONGO_DB'], host=CONF['MONGO_HOST'], port=27017)


# ------------------------------------------------- MONGO DOCUMENTS ------------------------------------------------- #
class Calendar(Document):
    sign_up_date = LongField(required=True)
    email = StringField(required=True, unique=True)
    last_seen = LongField(required=True)
    last_token = StringField(required=True, default='123')

    meta = {
        'indexes': [
            {
                'fields': ['email']
            }
        ],
        'ordering': ['+email']
    }


class RecognizedAuthor(Document):
    pseudo = StringField(required=True)
    alias = StringField(required=True, default='all')


class Likes(Document):
    beedoc = StringField(required=True)
    user = StringField(required=True)
    like = IntField(required=True, default=0)
    dislike = IntField(required=True, default=0)
    time = LongField(required=True)

    meta = {
        'indexes': [
            {
                'fields': ['time']
            }
        ],
        'ordering': ['+time']
    }


class BeeUser(Document):
    """
        Accounts
    """
    pseudo = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    access = IntField(required=True, default=1)  # 0 reader, 1 writer, 2 mode, 3 admin
    token = StringField(required=True, default='123')
    web_token = StringField(required=True, default='123')

    meta = {
        'indexes': [
            {
                'fields': ['email']
            }
        ],
        'ordering': ['+email']
    }


class Category(Document):
    """
        Categories: News, oNews, Gossip
    """
    name = StringField(required=True)


class BeeDoc(Document):
    """
        The Article class to use in mongodb
    """
    id = StringField(required=True, primary_key=True, unique=True)
    author = StringField(required=True)  # Pseudo of the author
    alias = StringField(required=True, default='all')
    title = StringField(required=True)
    category = ReferenceField(Category, required=True)  # News, Official News, Gossip
    time = LongField(required=True)
    comments = IntField(required=True, default=0)  # Number of comments
    likes = IntField(required=True, default=0)  # Number of likes
    dislikes = IntField(required=True, default=0)  # Number of dislikes
    visibility = IntField(required=True, default=0)  # 0 not visible, 1 visible
    data = DynamicField(default={})
    meta = {
        'indexes': [
            {
                'fields': ['category']
            },
            {
                'fields': ['author']
            },
            {
                'fields': ['time']
            }
        ],
        'ordering': ['+time']
    }

    @classmethod
    def update_doc(cls, self, args):
        for k in list(args):
            self.data[k] = args[k]
        self._mark_as_changed('data')


class FlashNews(Document):
    id = StringField(required=True, primary_key=True, unique=True)
    time = LongField(required=True)
    text = StringField(required=True)
    author = StringField(required=True)

    meta = {
        'indexes': [
            {
                'fields': ['time']
            },
            {
                'fields': ['author']
            }
        ],
        'ordering': ['+time']
    }


class Comment(Document):
    """
        The comments
    """
    beedoc = StringField(required=True)
    author = StringField(required=True)
    time = LongField(required=True)
    data = DynamicField(default={})

    meta = {
        'indexes': [
            {
                'fields': ['time']
            }
        ],
        'ordering': ['+time']
    }

    @classmethod
    def update_com(cls, self, args):
        for k in list(args):
            self.data[k] = args[k]
        self._mark_as_changed('data')


# -------------------------------------------------- USER FUNCTIONS -------------------------------------------------- #
@mongo.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()

    username = data['username']
    pseudo = data['pseudo']

    if not SomeUtils.mail_checker(username):
        return jsonify({'success': 'no', 'more': 'Use your @enseirb-matmeca.fr'})

    password = SomeUtils.generate_pass()

    try:
        BeeUser.objects.get(pseudo=pseudo)
        return jsonify({'success': 'no', 'more': 'Pseudo already used'})
    except DoesNotExist:
        try:
            BeeUser.objects.get(email=username)
            return jsonify({'success': 'no', 'more': 'Email already used'})
        except DoesNotExist:
            beeuser = BeeUser(pseudo=pseudo, email=username, password=SomeUtils.pass_encrypt(password))
            beeuser.web_token = SomeUtils.genarate_token(username, 12)
            beeuser.save()
            sign_up_date = long(datetime.now().strftime("%s"))
            calendar = Calendar(email=username, sign_up_date=sign_up_date, last_seen=sign_up_date)
            calendar.save()
            rec_author = RecognizedAuthor(pseudo=pseudo, alias='all')
            rec_author.save()

    SomeUtils.send_mail(username, password, 'Welcome to BeeNewsFamily', 1)

    return jsonify({'success': 'yes', 'more': 'Sign up successful'})


@mongo.route('/login', methods=['POST'])
def login():
    """ login endpoint

    :return: JSON object containing api key or an error
    """
    data = request.get_json()

    username = data['username']
    old_token = request.headers.get('X-BeenewsAPI-Token', None)
    remember = None

    print username

    if SomeUtils.mail_checker(username):
        try:
            if old_token:
                beeuser = BeeUser.objects.get(email=username, token=old_token)
            else:
                password = data['password']
                remember = data['remember']
                beeuser = BeeUser.objects.get(email=username)
                if not SomeUtils.pass_decrypt(password, beeuser.password):
                    return jsonify({'success': 'no', 'more': 'Email or password/token incorrect'})

            if not remember:
                # generate a token for 2 hours
                token = SomeUtils.genarate_token(username, 2)
            elif remember:
                # generate token for the user and make it last 7 days
                token = SomeUtils.genarate_token(username, 168)
            else:
                return jsonify({'success': 'no', 'more': 'Connection data are incoherent'})

            beeuser.token = token
            beeuser.web_token = SomeUtils.genarate_token(username, 12)
            beeuser.save()
            try:
                calendar = Calendar.objects.get(email=username)
                calendar.last_seen = long(datetime.now().strftime("%s"))
                calendar.last_token = token
                calendar.save()
                return jsonify({'success': 'yes',
                                'more': 'Log in successful',
                                'token': token,
                                'pseudo': beeuser.pseudo})
            except DoesNotExist:
                return jsonify({'success': 'no', 'more': 'User info are incoherent'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Email or password/token incorrect'})
    else:
        return jsonify({'success': 'no', 'more': 'Use the same email asked during sign up'})


@mongo.route('/actualize_token', methods=['POST'])
@requires_token
def actualize_token():
    data = request.get_json()

    username = data['username']
    remember = data['remember']
    token = request.headers.get('X-BeenewsAPI-Token', None)

    if not SomeUtils.token_checker(token):
        return jsonify({'success': 'no', 'more': 'You have to log in'})

    if not remember:
        # generate a token for 2 hours
        new_token = SomeUtils.genarate_token(username, 2)
    elif remember:
        # generate token for the user and make it last 7 days
        new_token = SomeUtils.genarate_token(username, 168)
    else:
        return jsonify({'success': 'no', 'more': 'Remember data are incoherent'})

    if SomeUtils.mail_checker(username):
        try:
            beeuser = BeeUser.objects.get(email=username, token=token)
            beeuser.token = new_token
            beeuser.save()
            try:
                calendar = Calendar.objects.get(email=username)
                calendar.last_seen = long(datetime.now().strftime("%s"))
                calendar.save()
                return jsonify({'success': 'yes',
                                'more': 'Token actualized successfully',
                                'token': new_token})
            except DoesNotExist:
                return jsonify({'success': 'no', 'more': 'User info are incoherent'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Email or token incorrect'})
    else:
        return jsonify({'success': 'no', 'more': 'Use the same email asked during sign up'})


@mongo.route('/logout', methods=['POST'])
@requires_token
def logout():
    """ logout endpoint

    :return: JSON object containing api key or an error
    """
    data = request.get_json()

    username = data['username']
    token = request.headers.get('X-BeenewsAPI-Token', None)

    try:
        beeuser = BeeUser.objects.get(email=username, token=token)
        try:
            calendar = Calendar.objects.get(email=username)
            calendar.last_token = beeuser.token
            calendar.save()
            beeuser.token = ''
            beeuser.save()
            return jsonify({'success': 'yes', 'more': 'Log out successful'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Calendar error. Contact admins.'})
    except DoesNotExist:
        return jsonify({'success': 'no', 'more': 'Email or token invalid'})


@mongo.route('/change_pass', methods=['POST'])
@requires_token
def change_pass():
    data = request.get_json()

    username = data['username']
    old_password = data['old_password']
    new_password = data['new_password']

    token = request.headers.get('X-BeenewsAPI-Token', None)

    try:
        beeuser = BeeUser.objects.get(email=username, token=token)
        if not SomeUtils.pass_decrypt(old_password, beeuser.password):
            return jsonify({'success': 'no', 'more': 'Password invalid'})
        beeuser.password = SomeUtils.pass_encrypt(new_password)
        beeuser.save()
        return jsonify({'success': 'yes', 'more': 'Password change successful'})
    except DoesNotExist:
        return jsonify({'success': 'no', 'more': 'Email or password invalid'})


@mongo.route('/reinit_pass', methods=['POST'])
@requires_token
def reinit_pass():
    data = request.get_json()

    username = data['username']

    token = request.headers.get('X-BeenewsAPI-Token', None)

    try:
        Calendar.objects.get(email=username, last_token=token)
        try:
            beeuser = BeeUser.objects.get(email=username)
            password = SomeUtils.generate_pass()
            beeuser.password = SomeUtils.pass_encrypt(password)
            beeuser.token = ''
            beeuser.save()
            SomeUtils.send_mail(username, password, 'Password Forgotten', 2)
            return jsonify({'success': 'yes', 'more': 'Password sent successfully'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Email invalid'})
    except DoesNotExist:
        return jsonify({'success': 'no', 'more': 'Email invalid or not in database'})


# ------------------------------------------------ ARTICLES FUNCTIONS ------------------------------------------------ #

@mongo.route('/add', methods=['POST'])
@requires_token
def add():
    infos = request.get_json()
    category = infos['category']
    doc_type = infos['type']
    data = infos['data']
    username = infos['username']

    token = request.headers.get('X-BeenewsAPI-Token', None)
    if token:
        try:
            beeuser = BeeUser.objects.get(email=username, token=token)
        except DoesNotExist:
            try:
                beeuser = BeeUser.objects.get(email=username, web_token=token)
            except DoesNotExist:
                return jsonify({'success': 'no', 'more': 'Token/email invalid'})
        if beeuser.access >= 1:
            response = add_wargs(beeuser.email, beeuser.pseudo, category, doc_type, data)
            return response
        else:
            return jsonify({'success': 'no', 'more': 'Access denied'})
    else:
        return jsonify({'success': 'no', 'more': 'No token given'})


def add_wargs(email, author, category, doc_type, data):
    Category.objects(name=category).update_one(set__name=category, upsert=True)
    category = Category.objects.get(name=category)
    timestamp = SomeUtils.generate_timestamp()
    alias = data['alias']
    uni_text = SomeUtils.to_unicode(data['text'])
    data['text'] = uni_text
    if doc_type == 'comment':
        beedoc = data['beedoc']
        try:
            doc = BeeDoc.objects.get(id=beedoc)
            doc.comments += 1
            doc.save()
            comment = Comment(beedoc=beedoc, time=timestamp, author=author, data=data)
            comment.save()
            response = jsonify(
                {'success': 'yes', 'more': "Comment for article " + str(beedoc) + " has been added/updated"})
        except DoesNotExist:
            response = jsonify({'success': 'no', 'more': "Doc ref incorrect"})
        return response
    elif doc_type == 'article':
        try:
            RecognizedAuthor(pseudo=author, alias=alias)
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': "Not authorized to post in " + alias})
        id = SomeUtils.generate_id(data)
        beedoc = BeeDoc(category=category, id=id, time=timestamp, alias=alias, author=author, title=data['title'],
                        data=data)
        beedoc.save()
        response = jsonify({'success': 'yes', 'more': "Article with title " + str(
                            data['title']) + " has been added/updated to the category " + str(beedoc.category.name)})
        SomeUtils.send_mail(email, '', 'You have submitted an article', 3)
        SomeUtils.send_mail('ladotevi@enseirb-matmeca.fr', beedoc.id, 'Validation of article', 4)
        return response
    elif doc_type == 'flash':
        id = SomeUtils.generate_id(data)
        flash = FlashNews(id=id, time=timestamp, text=data['text'], author=author)
        flash.save()
        response = jsonify({'success': 'yes', 'more': "FlashNews " + str(flash.text) + " has been added/updated by " + \
                                                      str(flash.author)})
        return response
    else:
        return jsonify({'success': 'no', 'more': "Error: Bad doc_type"})


@mongo.route('/get_beedoc', methods=['GET'])
@requires_token
def get_beedoc():
    """
    Use to get articles
    :return: JSON containing the last 10 articles according to category
    """
    username = request.args.get('username', None)
    category_name = request.args.get('category', None)
    alias = request.args.get('alias', None)
    offset = request.args.get('offset', 0)
    token = request.headers.get('X-BeenewsAPI-Token', None)

    if username:
        try:
            beeuser = BeeUser.objects.get(email=username, token=token)
            if not SomeUtils.token_checker(beeuser.token):
                return jsonify({'success': 'no', 'more': 'Token expired'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Invalid token/username'})

    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            if category_name == 'news':
                if alias == 'all':
                    beedocs = BeeDoc.objects(category=category, visibility=1)[offset:offset + 10]
                else:
                    beedocs = BeeDoc.objects(category=category, alias=alias, visibility=1)[offset:offset + 10]
                response = [SomeUtils.beedoc_to_dict(beedoc) for beedoc in beedocs]
                if beedocs:
                    return jsonify({'success': 'yes', 'more': response})
                else:
                    return jsonify({'success': 'no', 'more': 'No Article found'})
            else:
                beedocs = BeeDoc.objects(category=category, author='eirbmmk', visibility=1)[offset:offset + 10]
                if beedocs:
                    response = [SomeUtils.beedoc_to_dict(beedoc) for beedoc in beedocs]
                    return jsonify({'success': 'yes', 'more': response})
                else:
                    return jsonify({'success': 'no', 'more': 'No Article found'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Category asked does not exist'})
    else:
        return jsonify({'success': 'no', 'more': 'No category given'})


@mongo.route('/get_comment', methods=['GET'])
@requires_token
def get_comment():
    """
    Use to get comments
    :return: JSON containing the last 10 articles according to category
    """
    beedoc_ref = request.args.get('beedoc', None)
    offset = int(request.args.get('offset', 0))

    return_offset = 0

    if beedoc_ref:
        total_comments = Comment.objects(beedoc=beedoc_ref)
        total = len(total_comments)
        if offset < 0:
            comments = total_comments[0:]
        elif offset == 10000:
            if total >= 10:
                comments = total_comments[(total - 10):]
                return_offset = total - 10
            else:
                comments = total_comments[0:]
        else:
            comments = total_comments[offset:]
            return_offset = offset - 10

        if comments:
            response = [SomeUtils.comment_to_dict(comment) for comment in comments]
            return jsonify({'success': 'yes', 'more': response, 'offset': return_offset})
        else:
            return jsonify({'success': 'no', 'more': 'No Comment found'})
    else:
        return jsonify({'success': 'no', 'more': 'No Article reference given'})


@mongo.route('/get_onews', methods=['GET'])
def get_onews():
    import requests

    url = 'http://appli.eirbmmk.fr/News'
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
    r = requests.post(url=url, headers=headers)
    return jsonify(onews=json.loads(r.text))


@mongo.route('/like_state', methods=['POST'])
@requires_token
def like_state():
    data = request.get_json()
    beedoc_ref = data['beedoc']
    username = data['username']

    if beedoc_ref:
        try:
            the_like_state = Likes.objects.get(beedoc=beedoc_ref, user=username)
            return jsonify({'success': 'yes', 'more': 'Like state found',
                            'like': the_like_state.like,
                            'dislike': the_like_state.dislike})
        except DoesNotExist:
            the_like_state = Likes(beedoc=beedoc_ref, user=username, time=SomeUtils.generate_timestamp())
            the_like_state.save()
            return jsonify({'success': 'yes', 'more': 'Not in database',
                            'like': the_like_state.like,
                            'dislike': the_like_state.dislike})
    else:
        return jsonify({'success': 'no', 'more': 'No Article reference given'})


@mongo.route('/likes', methods=['POST'])
@requires_token
def like_or_dislike():
    data = request.get_json()
    beedoc_ref = data['beedoc']
    action = data['action']
    username = data['username']

    if beedoc_ref:
        try:
            try:
                the_like_state = Likes.objects.get(beedoc=beedoc_ref, user=username)
            except DoesNotExist:
                the_like_state = Likes(beedoc=beedoc_ref, user=username, time=SomeUtils.generate_timestamp())

            beedoc = BeeDoc.objects.get(id=beedoc_ref)
            if action == 'like':
                if the_like_state.like == 0 and the_like_state.dislike == 0:
                    beedoc.likes += 1
                    beedoc.save()
                    the_like_state.like = 1
                    the_like_state.save()

                if the_like_state.dislike == 1:
                    beedoc.dislikes += -1
                    beedoc.save()
                    the_like_state.like = 0
                    the_like_state.dislike = 0
                    the_like_state.save()
            elif action == 'dislike':
                if the_like_state.dislike == 0 and the_like_state.like == 0:
                    beedoc.dislikes += 1
                    beedoc.save()
                    the_like_state.dislike = 1
                    the_like_state.save()

                if the_like_state.like == 1:
                    beedoc.likes += -1
                    beedoc.save()
                    the_like_state.like = 0
                    the_like_state.dislike = 0
                    the_like_state.save()
            else:
                return jsonify({'success': 'no', 'more': 'Action must be like or dislike'})
            return jsonify({'success': 'yes', 'more': 'Action ' + str(action) + 'reference given'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'Bad Article reference given'})
    else:
        return jsonify({'success': 'no', 'more': 'No Article reference given'})


@mongo.route('/get_flash', methods=['GET'])
@requires_token
def get_flash():
    offset = request.args.get('offset', 0)

    flash_news = FlashNews.objects[offset:offset + 10]
    if flash_news:
        response = [SomeUtils.flash_to_dict(flash_new) for flash_new in flash_news]
        return jsonify({'success': 'yes', 'more': response})
    else:
        return jsonify({'success': 'no', 'more': 'No flashnews found'})


@mongo.route('/change_access', methods=['POST'])
def change_access():
    infos = request.get_json()
    username = infos['username']
    password = infos['password']
    access = infos['access']

    # Change this later
    if password == 'ladotevirherveux':
        try:
            beeuser = BeeUser.objects.get(email=username)
            beeuser.access = int(access)
            beeuser.save()
            return jsonify({'success': 'yes', 'more': 'Access changed to ' + str(access)})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'User does not exist'})
    else:
        return jsonify({'success': 'yes', 'more': 'Password incorrect'})


@mongo.route('/set_visibility', methods=['POST'])
def set_visibility():
    infos = request.get_json()
    beedoc = infos['beedoc']
    password = infos['password']
    visibility = infos['visibility']

    if visibility not in [0, 1]:
        return jsonify({'success': 'no', 'more': 'visibility must be 0 or 1'})

    # Change this later
    if password == 'ladotevirherveux':
        try:
            beedoc = BeeDoc.objects.get(id=beedoc)
            beedoc.visibility = int(visibility)
            beedoc.save()
            try:
                beeuser = BeeUser.objects.get(pseudo=beedoc.author)
            except DoesNotExist:
                return jsonify({'success': 'no', 'more': 'Invalid author'})
            if visibility == 0:
                SomeUtils.send_mail(beeuser.email, '', 'Sorry for your article', 5)
            else:
                SomeUtils.send_mail(beeuser.email, '', 'Validation of your article', 6)
            return jsonify({'success': 'yes', 'more': 'Visibility changed to ' + str(visibility)})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'BeeDoc does not exist'})
    else:
        return jsonify({'success': 'yes', 'more': 'Password incorrect'})


@mongo.route('/recognized_author', methods=['POST'])
def add_recognized_author():
    infos = request.get_json()
    username = infos['username']
    password = infos['password']
    alias = infos['alias']

    if alias not in CategoryUtils.RECOGNIZED_ALIASES:
        return jsonify({'success': 'no', 'more': 'Alias not recognized'})

    # Change this later
    if password == 'ladotevirherveux':
        try:
            beeuser = BeeUser.objects.get(email=username)
            rec_author = RecognizedAuthor(pseudo=beeuser.pseudo, alias=alias)
            rec_author.save()
            return jsonify({'success': 'yes', 'more': username + ' added to recognized author!'})
        except DoesNotExist:
            return jsonify({'success': 'no', 'more': 'User does not exist'})
    else:
        return jsonify({'success': 'yes', 'more': 'Password incorrect'})


# ------------------------------------------------ WEB FUNCTIONS ------------------------------------------------ #
@mongo.route('/web/home')
def web_home():
    return render_template('home.html',
                           page_name='Home')

@mongo.route('/web/post_page')
def web_post_page():
    return render_template('post.html',
                           page_name='Post')


@mongo.route('/web/confirm')
def web_confirm():
    return render_template('confirm.html',
                           page_name='Confirmation')


@mongo.route('/web/post', methods=['POST'])
def web_post():
    infos = request.get_json()
    user = infos['userData']
    article = infos['articleData']

    email = user['email']
    password = user['password']

    try:
        beeuser = BeeUser.objects.get(email=email)
        if not SomeUtils.pass_decrypt(password, beeuser.password):
            return jsonify({'success': 'no', 'more': 'Email or password/token incorrect'})
    except DoesNotExist:
        return jsonify({'success': 'no', 'more': 'Email invalid or not in database'})

    category = article['category']
    doc_type = article['type']
    data = article['data']

    if beeuser.access >= 1:
        response = add_wargs(email, beeuser.pseudo, category, doc_type, data)
        return response
    else:
        return jsonify({'success': 'no', 'more': 'Access denied'})
