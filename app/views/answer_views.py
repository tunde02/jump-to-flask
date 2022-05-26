from datetime import datetime
from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect
from app import db
from app.models import Question, Answer
from app.forms import AnswerForm
from app.views.auth_views import login_required


bp = Blueprint('answer', __name__, url_prefix='/answer')


@bp.route('/create/<int:question_id>', methods=['POST'])
@login_required
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)

    if form.validate_on_submit():
        answer = Answer(question=question, content=request.form['content'], create_date=datetime.now(), user=g.user)

        db.session.add(answer)
        db.session.commit()

        return redirect(url_for('question.detail', question_id=question_id))

    page = request.args.get('page', type=int, default=1)
    answer_list = question.answer_set.paginate(page, per_page=10)

    return render_template('question/question_detail.html', question=question, answer_list=answer_list, form=form)


@bp.route('/modify/<int:answer_id>', methods=['GET', 'POST'])
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)

    if g.user != answer.user:
        flash("수정 권한이 없습니다.")

        return redirect(url_for('question.detail', question_id=answer.question.id))

    if request.method == 'POST': # POST
        form = AnswerForm()

        if form.validate_on_submit():
            form.populate_obj(answer)
            answer.modify_date = datetime.now()

            db.session.commit()

            return redirect(url_for('question.detail', question_id=answer.question.id))
    else: # GET
        form = AnswerForm(obj=answer)

    return render_template('answer/answer_form.html', form=form)


@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question.id

    if g.user != answer.user:
        flash('삭제 권한이 없습니다.')
    else:
        db.session.delete(answer)
        db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))


@bp.route('/vote/<int:answer_id>')
@login_required
def vote(answer_id):
    answer = Answer.query.get_or_404(answer_id)

    if g.user == answer.user:
        flash("본인이 작성한 글은 추천할 수 없습니다.")
    elif g.user in answer.voter:
        flash("이미 추천한 글입니다.")
    else:
        answer.voter.append(g.user)
        answer.num_voter += 1

        db.session.commit()

    return redirect(url_for('question.detail', question_id=answer.question.id))
