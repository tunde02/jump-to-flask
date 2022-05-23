from datetime import datetime
from flask import Blueprint, url_for, request, render_template
from werkzeug.utils import redirect
from app import db
from app.models import Question, Answer
from app.forms import AnswerForm


bp = Blueprint('answer', __name__, url_prefix='/answer')


@bp.route('/create/<int:question_id>', methods=['POST'])
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)

    if form.validate_on_submit():
        answer = Answer(question=question, content=request.form['content'], create_date=datetime.now())

        db.session.add(answer)
        db.session.commit()

        return redirect(url_for('question.detail', question_id=question_id))

    return render_template('question/question_detail.html', question=question, form=form)
