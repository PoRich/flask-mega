from flask import current_app
from hashlib import md5
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# adds is_authenticated, is_active, is_anonymous, get_id
from time import time
import jwt
from application import db, login
from application.search import add_to_index, remove_from_index, query_index


#  Mixin to auto manage an associated full-text index: SQLAlchemy-Elasticsearch
class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


'''  table not declared as a model b/c this is an auxi table with no other data
other than foreign keys '''
#  many-to-many relationships
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#many-to-many-relationships
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey(
                               'user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey(
                               'user.id'))
                     )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                                                  lazy='dynamic')


    '''
    querying this relationship from the left side will produce a list of
    followed users (those on the right side);

    User is the right side entity of the relationship
    secondary configures the association table used for this relationship

    primaryjoin indicates the condition that links the left side entity
    (follower) with the association table (join condition for the left side of
    the relationship is the user ID matching the follower_id)

    secondaryjoin is the condition that links the right side entity (the
    followed user)

    backref defines how the relationship will be accessed from the right side
    entity (from the left side, the relationship is named followed, for the
    rightside, the relationship is known as followers to represent all the
    left side users that are linked to the target user in the right side
    the lazy arg indicates the execution mode; mode of dynamic sets up the
    query to not run until specifically requested)

    (second) lazy applies to the left side query instead of the right side
    '''


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        # md5 support works on bytes not strings, encode string->bytes
        return 'https://www.gravatar.com/avatar/{}?d=wavatar&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            # standard SQLAlchemy ORM way to add relationship

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            # standard SQLAlchemy ORM way to remove relatinship

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    '''
    filter() can include arbitrary filtering conditions, unlike filter_by()

    is_following looks for items in the association table that have the left
    side foreign key set to the self user, and the right side set to the user
    argument
    '''

    def followed_posts(self):
        followed = Post.query.join(followers,
            (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)

        own = Post.query.filter_by(user_id=self.id)

        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        # expiration in seconds
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        '''
        NOTE: the contents of the token (including payload) are not securte
        and can be decoded by anyone: https://jwt.io/#debugger-io
        The tocken is secure b/c the payload is signed; the signature is
        invalidated if someone tampered / forged the payload int he token and
        someone would need the SECRET KEY to generate a new signature
        '''

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)
    '''
    static method can be invoked directly from the class; similar to a class
    method, w/ the only difference is that static methods do not receive the
    class as a first argument
    '''


@login.user_loader  # decorator registers function with Flask-Login
def load_user(id):
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    # variable to assist indexing functions in a generic way
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
