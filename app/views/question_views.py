import os, uuid, shutil

from datetime import datetime
from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect, secure_filename

from app import db
from app.models import Question, Answer, User, Category
from app.forms import QuestionForm, AnswerForm
from app.views.auth_views import login_required
from config.development import UPLOAD_FOLDER, ALLOWED_EXTENSIONS


bp = Blueprint('question', __name__, url_prefix='/question')


def get_category_text(category_type='FREE'):
    category_text = '자유'

    if category_type == 'FREE': # 자유
        category_text = '자유'
    elif category_type == 'QUESTION': # 질문
        category_text = '질문'
    elif category_type == 'INFORMATION': # 정보
        category_text = '정보'
    elif category_type == 'BOAST': # 비틱
        category_text = '비틱'
    elif category_type == 'SUGGESTION': # 건의
        category_text = '건의'
    elif category_type == 'NOTICE': # 공지
        category_text = '공지'

    return category_text


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_images(request, question_id):
    # 게시글에 쓰인 이미지 파일 저장
    uploaded_images_path = os.path.join(UPLOAD_FOLDER, 'temp')
    post_images_path = os.path.join(UPLOAD_FOLDER, 'posts', question_id)

    if not os.path.exists(post_images_path):
        os.makedirs(post_images_path)

    if request.form.get('upload_images'):
        _filenames = request.form.get('upload_images')[:-1].split('|')

        for filename in _filenames:
            before = os.path.join(uploaded_images_path, filename)
            destination = os.path.join(post_images_path, filename)
            shutil.move(before, destination)


def remove_temp_uploaded_images(content, question_id):
    # 게시글 폴더의 이미지들 중 content에 없는 것 삭제
    post_images_path = os.path.join(UPLOAD_FOLDER, 'posts', question_id)

    for filename in os.listdir(post_images_path):
        if filename not in content:
            os.remove(os.path.join(post_images_path, filename))


@bp.route('/list')
def _list():
    kw = request.args.get('kw', type=str, default='')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
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

    question_list = question_list.paginate(page, per_page=per_page)

    return render_template('question/question_list.html', question_list=question_list, page=page, per_page=per_page, kw=kw, category=category_type)


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

    question.num_views += 1
    db.session.commit()

    return render_template('question/question_detail.html', question=question, answer_list=answer_list, form=form, sort=sort)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = QuestionForm()

    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, create_date=datetime.now(), user=g.user)

        question.content = form.content.data if form.content.data else 'ㅈㄱㄴ'
        question.category = Category(question=question, category_type=form.category_type.data, category_text=get_category_text(form.category_type.data))

        db.session.add(question)
        db.session.commit()

        # 이미지 불러오는 경로 변경
        question.content = question.content.replace('/temp/', f"/posts/{question.id}/")
        db.session.commit()

        save_uploaded_images(request, str(question.id))
        remove_temp_uploaded_images(form.content.data, str(question.id))

        return redirect(url_for('question.detail', question_id=question.id))

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
            if form.content.data and form.content.data != "<p><br></p>":
                form.content.data = form.content.data.replace('/temp/', f'/posts/{question.id}/')
            else:
                form.content.data = 'ㅈㄱㄴ'

            form.populate_obj(question)
            question.modify_date = datetime.now()
            question.category.category_type = form.category_type.data
            question.category.category_text = get_category_text(question.category.category_type)

            save_uploaded_images(request, str(question.id))
            remove_temp_uploaded_images(form.content.data, str(question.id))

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

    # 게시글에 쓰인 이미지 폴더째로 삭제
    post_images_path = os.path.join(UPLOAD_FOLDER, 'posts', str(question.id))
    shutil.rmtree(post_images_path)

    db.session.delete(question)
    db.session.commit()

    return redirect(url_for('question._list'))


@bp.route('/vote/<int:question_id>')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user in question.voter:
        flash("이미 추천한 글입니다.")
    else:
        question.voter.append(g.user) # 동일한 사용자가 여러 번 추천해도 내부적으로 중복되지 않게끔 처리됨
        question.num_voter += 1

        db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        file = request.files["image"]

        if file.filename == '':
            return "error.png"

        if file and allowed_file(file.filename):
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{str(uuid.uuid4())}.{file_extension}")

            # 파일 이름 중복을 피하기 위해
            # 같은 이름이 존재하지 않을 때까지 uudi 새로 생성
            while os.path.exists(UPLOAD_FOLDER + "/" + filename):
                filename = secure_filename(f"{str(uuid.uuid4())}.{file_extension}")

            temp_path = os.path.join(UPLOAD_FOLDER, 'temp')
            file.save(os.path.join(temp_path, filename))

            return filename

    return "error.png"
