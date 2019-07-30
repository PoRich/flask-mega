from hashlib import md5
from datetime import datetime
from application import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # adds is_authenticated, is_active, is_anonymous, get_id
from time import time
import jwt

'''  table not declared as a model b/c this is an auxi table with no other data
other than foreign keys '''
#  many-to-many relationships https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#many-to-many-relationships
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
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
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
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
            self.followed.append(user)  # standard SQLAlchemy ORM way to add relatinship

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)  # standard SQLAlchemy ORM way to remove relatinship

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
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
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
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)
    '''
    static method can be invoked directly from the class; similar to a class
    method, w/ the only difference is that static methods do not receive the
    class as a first argument
    '''


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader # decorator registers function with Flask-Login
def load_user(id):
    return User.query.get(int(id))
