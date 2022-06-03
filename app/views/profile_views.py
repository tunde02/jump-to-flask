from flask import Blueprint, render_template, request

from app.models import User, Question, Answer
from app.views.auth_views import login_required


bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/info/<string:username>')
def info(username):
    question_list_page = request.args.get('question_list_page', type=int, default=1)
    answer_list_page = request.args.get('answer_list_page', type=int, default=1)

    user = User.query.filter_by(username=username).first()
    user_question_list = Question.query.filter_by(user_id=user.id).order_by(Question.create_date.desc()).paginate(question_list_page, per_page=10)
    user_answer_list = Answer.query.filter_by(user_id=user.id).order_by(Answer.create_date.desc()).paginate(answer_list_page, per_page=10)

    return render_template('profile/profile_info.html', user=user, tab='info', user_question_list=user_question_list, user_answer_list=user_answer_list)


@bp.route('/recent/<string:username>')
def recent(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile/profile_recent.html', user=user, tab='recent')


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
