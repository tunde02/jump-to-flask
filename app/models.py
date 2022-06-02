from app import db


question_voter = db.Table(
    'question_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)


class Question(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    subject     = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id     = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user        = db.relationship('User',
        backref=db.backref('question_set', passive_deletes=True))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter       = db.relationship('User', secondary=question_voter,
        backref=db.backref('question_voter_set', passive_deletes=True))
    num_voter   = db.Column(db.Integer, nullable=False, default=0)
    category    = db.relationship('Category',
        back_populates='question', passive_deletes=True, uselist=False)
    num_views   = db.Column(db.Integer, nullable=False, default=0)


answer_voter = db.Table(
    'answer_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), primary_key=True)
)


class Answer(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer,
        db.ForeignKey('question.id', ondelete='CASCADE'))
    question    = db.relationship('Question',
        backref=db.backref('answer_set', passive_deletes=True))
    content     = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id     = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user        = db.relationship('User',
        backref=db.backref('answer_set', passive_deletes=True))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter       = db.relationship('User', secondary=answer_voter,
        backref=db.backref('answer_voter_set', passive_deletes=True))
    num_voter   = db.Column(db.Integer, nullable=False, default=0)


class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    nickname = db.Column(db.String(150), nullable=False, default='닉네임')
    password = db.Column(db.String(200), nullable=False)
    email    = db.Column(db.String(120), nullable=False)
    profile_image = db.Column(db.String(200), nullable=False, default='images/profile/default_profile.png')
    about_me = db.Column(db.String(200), nullable=False, default='')


class Comment(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    content     = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime(), nullable=True)
    answer_id   = db.Column(db.Integer,
        db.ForeignKey('answer.id', ondelete='CASCADE'), nullable=False)
    answer      = db.relationship('Answer',
        backref=db.backref('comment_set', passive_deletes=True))
    user_id     = db.Column(db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user        = db.relationship('User',
        backref=db.backref('comment_set', passive_deletes=True))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer,
        db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)
    question = db.relationship('Question',
        back_populates='category', passive_deletes=True, uselist=False)
    category_type = db.Column(db.String(20), nullable=False, default='FREE')
    category_text = db.Column(db.String(20), nullable=False, default='자유')
