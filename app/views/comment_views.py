from datetime import datetime
from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect
from app import db
from app.models import Answer, Comment
from app.forms import CommentForm
from app.views.auth_views import login_required


bp = Blueprint('comment', __name__, url_prefix='/comment')


@bp.route('/create/<int:answer_id>', methods=['POST'])
@login_required
def create(answer_id):
    form = CommentForm()
    answer = Answer.query.get_or_404(answer_id)

    if form.validate_on_submit():
        comment = Comment(answer=answer, user=g.user, content=request.form['content'], create_date=datetime.now())

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('question.detail', question_id=answer.question.id))

    answer_list = Answer.query.filter(Answer.question_id == answer.question.id) \
        .order_by(Answer.num_voter.desc(), Answer.create_date.desc()) \
        .paginate(page=1, per_page=5)

    return render_template('question/question_detail.html', question=answer.question, answer_list=answer_list, form=form, sort=0)


@bp.route('/delete/<int:comment_id>')
@login_required
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    question_id = comment.answer.question.id

    if g.user != comment.user:
        flash('삭제 권한이 없습니다.')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))
