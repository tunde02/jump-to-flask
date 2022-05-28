from datetime import datetime
from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect
from app import db
from app.models import Question, Answer, User, Category
from app.forms import QuestionForm, AnswerForm
from app.views.auth_views import login_required


bp = Blueprint('question', __name__, url_prefix='/question')


def get_category_text(category_type='FREE'):
    category_text = '자유'

    if category_type == 'FREE': # 자유
        category_text = '자유'
    elif category_type == 'QUESTION': # 질문
        category_text = '질문'
    elif category_type == 'NOTICE': # 공지
        category_text = '공지'

    return category_text


@bp.route('/list')
def _list():
    kw = request.args.get('kw', type=str, default='')
    page = request.args.get('page', type=int, default=1)
    category_type = request.args.get('category', type=str, default='')

    # Category
    question_list = Question.query.join(Category) \
        .filter(Category.category_type == category_type if category_type else True) \
        .order_by(Question.create_date.desc())

    # Search
    if kw:
        search = '%%{}%%'.format(kw)
        subquery = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(subquery, subquery.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |   # 질문 제목
                    Question.content.ilike(search) |   # 질문 내용
                    User.username.ilike(search) |      # 질문 작성자
                    subquery.c.content.ilike(search) | # 답변 내용
                    subquery.c.username.ilike(search)  # 답변 작성자
                    ) \
            .distinct()

    question_list = question_list.paginate(page, per_page=10)

    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw, category=category_type)


@bp.route('/detail/<int:question_id>')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    page = request.args.get('page', type=int, default=1)
    sort = request.args.get('sort', type=int, default=0)
    answer_list = Answer.query.filter(Answer.question_id == question.id)

    if sort == 0: # 추천순
        answer_list = answer_list.order_by(Answer.num_voter.desc(), Answer.create_date.desc())
    elif sort == 1: # 최신순
        answer_list = answer_list.order_by(Answer.create_date.desc())
    elif sort == 2: # 오래된순
        answer_list = answer_list.order_by(Answer.create_date)

    answer_list = answer_list.paginate(page, per_page=5)

    return render_template('question/question_detail.html', question=question, answer_list=answer_list, form=form, sort=sort)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = QuestionForm()

    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        category_type = form.category_type.data
        category_text = get_category_text(category_type)
        question.category = Category(question=question, category_type=category_type, category_text=category_text)

        db.session.add(question)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template('question/question_form.html', form=form)


@bp.route('/modify/<int:question_id>', methods=['GET', 'POST'])
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user != question.user:
        flash('수정 권한이 없습니다.')

        return redirect(url_for('question.detail', question_id=question_id))

    if request.method == 'POST': # POST
        form = QuestionForm()

        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()
            question.category.category_type = form.category_type.data
            question.category.category_text = get_category_text(question.category.category_type)

            db.session.commit()

            return redirect(url_for('question.detail', question_id=question_id))
    else: # GET
        form = QuestionForm(obj=question, category_type=question.category.category_type)

    return render_template('question/question_form.html', form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user != question.user:
        flash("삭제 권한이 없습니다.")

        return redirect(url_for('question.detail', question_id=question_id))

    db.session.delete(question)
    db.session.commit()

    return redirect(url_for('question._list'))


@bp.route('/vote/<int:question_id>')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user == question.user:
        flash("본인이 작성한 글은 추천할 수 없습니다.")
    else:
        question.voter.append(g.user) # 동일한 사용자가 여러 번 추천해도 내부적으로 중복되지 않게끔 처리됨

        db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))
