from flask import Blueprint, request, jsonify, abort
from mongoengine import *
from .app_utils import requires_token
from contrib.some_utils import SomeUtils
from contrib.category_utils import CategoryUtils


mongo = Blueprint('mongo', __name__)

# Connect to the database
@mongo.record_once
def connect_to_base(setup_state):
    CONF = setup_state.app.config
    connect(db=CONF['MONGO_DB'], host=CONF['MONGO_HOST'], port=27017)
    register_connection(alias='default', name=CONF['MONGO_DB'], host=CONF['MONGO_HOST'], port=27017)

# ------------------------------------------------- MONGO DOCUMENTS ------------------------------------------------- #
class BeeUser(Document):
    """
        Accounts
    """
    pseudo = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    access = IntField(required=True, default=0)     # 0 reader, 1 writer, 2 admin
    token = StringField(required=True)

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
    author = StringField(required=True)                     # BDE, BDS, BAR .....
    category = ReferenceField(Category, required=True)      # News, Official News, Gossip
    time = LongField(required=True)
    comments = IntField(required=True, default=0)           # Number of comments
    likes = IntField(required=True, default=0)              # Number of likes
    dislikes = IntField(required=True, default=0)           # Number of dislikes
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
    def update_doc(cls, self, args):
        for k in list(args):
            self.data[k] = args[k]
        self._mark_as_changed('data')

# -------------------------------------------------- USER FUNCTIONS -------------------------------------------------- #

@mongo.route('/sign_up', methods=['POST'])
def sign_up():
    pass

@mongo.route('/login', methods=['POST'])
def login():
    """ login endpoint

    :return: JSON object containing api key or an error
    """
    data = request.get_json()

    username = data['username']
    password = data['password']
    remember = data['remember']

    if remember == 'no':
        # generate a token for an hour
        pass
    elif remember == 'yes':
        # generate token for the user and make it last 7 days
        if not (username, password) in {('cogniteam', "rocks all data"), (u'a\u0416a', 'geodatacogniteev')}:
            abort(422, {'identification': ['invalid']})

        return jsonify(token='123')
    else:
        pass

@mongo.route('/logout', methods=['POST'])
@requires_token
def logout():
    """ logout endpoint

    :return: JSON object containing api key or an error
    """
    data = request.get_json()

    username = data['username']

    # make the token expire

    return jsonify(token='123')

# ------------------------------------------------ ARTICLES FUNCTIONS ------------------------------------------------ #

@mongo.route('/add', methods=['POST'])
@requires_token
def add():
    infos = request.get_json()
    category = infos['category']
    doc_type = infos['type']
    data = infos['data']

    response = add_wargs(category, doc_type, data)
    return response

def add_wargs(category, doc_type, data):
    Category.objects(name=category).update_one(set__name=category, upsert=True)
    category = Category.objects.get(name=category)
    timestamp = SomeUtils.generate_timestamp()
    author = data['author']
    if doc_type == 'comment':
        beedoc = data['beedoc']
        comment = Comment(beedoc=beedoc, time=timestamp, author=author, data=data)
        comment.save()
        response = "Comment for article " + str(beedoc) + " has been added/updated"
        return response
    elif doc_type == 'article':
        id = SomeUtils.generate_id(data)
        beedoc = BeeDoc(category=category, id=id, time=timestamp, author=author, data=data)
        beedoc.save()
        response = "Article with title " + str(data['title']) + " has been added/updated to the category " + \
                   str(beedoc.category.name)
        return response
    else:
        return "Error: Bad doc_type"

@mongo.route('/get_beedoc', methods=['GET'])
@requires_token
def get_beedoc():
    """
    Use to get articles
    :return: JSON containing the last 10 articles according to category
    """
    category_name = request.args.get('category', None)
    author = request.args.get('author', None)
    offset = request.args.get('offset', 0)

    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            if category_name == 'news':
                if author in CategoryUtils.RECOGNIZED_AUTHOR:
                    
        except DoesNotExist:


    else:
        return jsonify({'success': 'no', 'more': 'No category given'})



@mongo.route('/get_comment', methods=['GET'])
@requires_token
def get_comment():
    """
    Use to get comments
    :return: JSON containing the last 10 articles according to category
    """
    category = request.args.get('category', None)
    author = request.args.get('author', None)
    offset = request.args.get('offset', 0)
    full = request.args.get('full', 'no')

