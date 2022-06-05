import os

from flask import Blueprint, flash, render_template, request, g, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename, redirect
from sqlalchemy import desc, literal

from app import db
from app.forms import UserModifyForm
from app.models import User, Question, Answer
from app.views.auth_views import login_required, update_num_notice
from config.development import UPLOAD_FOLDER


bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/info/<string:username>')
def info(username):
    question_list_page = request.args.get('question_list_page', type=int, default=1)
    answer_list_page = request.args.get('answer_list_page', type=int, default=1)

    user = User.query.filter_by(username=username).first()
    user_question_list = Question.query.filter_by(user_id=user.id).order_by(Question.create_date.desc()).paginate(question_list_page, per_page=10)
    user_answer_list = Answer.query.filter_by(user_id=user.id).order_by(Answer.create_date.desc()).paginate(answer_list_page, per_page=10)

    return render_template('profile/profile_info.html', user=user, tab='info', user_question_list=user_question_list, user_answer_list=user_answer_list)


@bp.route('/recent/<string:username>', methods=['GET', 'POST'])
@login_required
def recent(username):
    page = request.args.get('page', type=int, default=1)
    user = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        checked_recent_str_list = request.form.get('selected', type=str, default='').split('|')[:-1]
        checked_recent_tuple_list = [(e.split('-')[0], e.split('-')[1]) for e in checked_recent_str_list]

        for recent_notice in checked_recent_tuple_list:
            if recent_notice[0] == 'QUESTION':
                checked_question = Question.query.get_or_404(recent_notice[1])
                checked_question.is_updated = False
            else:
                checked_answer = Answer.query.get_or_404(recent_notice[1])
                checked_answer.is_updated = False

        update_num_notice(user)

        db.session.commit()

    recent_question_list = db.session.query( \
        literal('새 답변').label('notice_info'), \
        Question.id.label('id'), \
        Question.id.label('post_id'), \
        Question.subject.label('content'), \
        Question.create_date.label('create_date'))\
        .filter(Question.user_id == user.id).filter(Question.is_updated == True)
    recent_answer_list = db.session.query( \
        literal('새 댓글').label('notice_info'), \
        Answer.id.label('id'), \
        Answer.question_id.label('post_id'), \
        Answer.content.label('content'), \
        Answer.create_date.label('create_date')) \
        .filter(Answer.user_id == user.id).filter(Answer.is_updated == True)
    recent_list = recent_question_list.union(recent_answer_list).order_by(desc('create_date')).paginate(page, per_page=10)

    return render_template('profile/profile_recent.html', user=user, tab='recent', recent_list=recent_list)


@bp.route('/modify/<string:username>', methods=['GET', 'POST'])
@login_required
def modify(username):
    user = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        form = UserModifyForm()

        if form.validate_on_submit():
            error = None

            if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
                error = '이미 존재하는 아이디입니다.'
            elif form.nickname.data != user.nickname and User.query.filter_by(nickname=form.nickname.data).first():
                error = '이미 존재하는 닉네임입니다.'
            elif form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
                error = '이미 존재하는 이메일입니다.'

            if error is None:
                if form.profile_image.data is not None:
                    file_extension = form.profile_image.data.filename.rsplit('.', 1)[1].lower()
                    file_name = secure_filename(f"{form.username.data}.{file_extension}")
                    file_path = os.path.join(UPLOAD_FOLDER, 'profile', file_name)

                    form.profile_image.data.save(file_path)
                    form.profile_image.data = f"images/profile/{file_name}"
                else:
                    form.profile_image.data = user.profile_image

                if  form.password.data != '':
                    form.password.data = generate_password_hash(form.password.data)
                else:
                    form.password.data = user.password

                form.populate_obj(user)

                db.session.commit()
            else:
                flash(error)
    else:
        form = UserModifyForm(obj=user)

    return render_template('profile/profile_modify.html', user=user, tab='modify', form=form)


@bp.route('/withdrawl/<string:username>', methods=['GET', 'POST'])
@login_required
def withdrawl(username):
    user = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template('profile/profile_withdrawl.html', user=user, tab='withdrawl')
