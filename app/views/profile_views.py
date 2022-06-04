from flask import Blueprint, render_template, request, g
from sqlalchemy import desc, literal

from app import db
from app.models import User, Question, Answer
from app.views.auth_views import login_required, update_num_notice


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


@bp.route('/modify/<string:username>')
@login_required
def modify(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile/profile_modify.html', user=user, tab='modify')


@bp.route('/withdrawl/<string:username>')
@login_required
def withdrawl(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile/profile_withdrawl.html', user=user, tab='withdrawl')
