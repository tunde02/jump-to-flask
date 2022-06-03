import functools, os

from flask import Blueprint, url_for, render_template, flash, request, session, g
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect, secure_filename

from app import db, mail
from app.forms import ChangePasswordForm, FindIdForm, FindPasswordForm, UserCreateForm, UserLoginForm
from app.models import User, Question, Answer
from config.development import SHOULD_CHANGED_PASSWORD, UPLOAD_FOLDER


bp = Blueprint('auth', __name__, url_prefix='/auth')


# login_required 어노테이션 추가
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''

            return redirect(url_for('auth.login', next=_next))

        return view(*args, **kwargs)

    return wrapped_view


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()

    if request.method == 'POST' and form.validate_on_submit():
        error = None

        if User.query.filter_by(username=form.username.data).first():
            error = '이미 존재하는 아이디입니다.'
        elif User.query.filter_by(nickname=form.nickname.data).first():
            error = '이미 존재하는 닉네임입니다.'

        if error is None:
            user = User(username=form.username.data,
                nickname=form.nickname.data,
                password=generate_password_hash(form.password1.data),
                email=form.email.data,
                about_me=form.about_me.data)

            if form.profile_image.data is not None:
                file_extension = form.profile_image.data.filename.rsplit('.', 1)[1].lower()
                file_name = secure_filename(f"{form.username.data}.{file_extension}")
                file_path = os.path.join(UPLOAD_FOLDER, 'profile', file_name)

                form.profile_image.data.save(file_path)
                user.profile_image = f"images/profile/{file_name}"

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('main.index'))
        else:
            flash(error)

    return render_template('auth/signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        elif check_password_hash(user.password, SHOULD_CHANGED_PASSWORD):
            return redirect(url_for('auth.change_password', user_id=user.id))

        if error is None:
            session.clear()
            session['user_id'] = user.id
            _next = request.args.get('next', '')

            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@bp.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('main.index'))


@bp.route('/findid', methods=['GET', 'POST'])
def find_id():
    form = FindIdForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).all()

        if not user:
            flash('존재하지 않는 이메일입니다.')
        else:
            user_email = user[0].email
            username_list = [u.username for u in user]
            message = Message('Pybo 아이디 찾기 메일', recipients=[user_email])
            message.body = '회원님의 아이디 목록 :\n\n{0}'.format('\n'.join(username_list))

            mail.send(message)

            return render_template('auth/email_sended.html')

    return render_template('auth/find_form.html', form=form, find_mode='id')


@bp.route('/findpassword', methods=['GET', 'POST'])
def find_password():
    form = FindPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, email=form.email.data).first()

        if not user:
            flash('존재하지 않는 아이디 혹은 이메일입니다.')
        else:
            user.password = generate_password_hash(SHOULD_CHANGED_PASSWORD)

            db.session.commit()

            message = Message('Pybo 비밀번호 초기화 메일', recipients=[user.email])
            message.body = '회원님의 비밀번호가 초기화되었습니다.\n임시 비밀번호\n\n{0}\n\n를 이용해 로그인하여 새로운 비밀번호를 설정해주세요.'.format(SHOULD_CHANGED_PASSWORD)

            mail.send(message)

            return render_template('auth/email_sended.html')

    return render_template('auth/find_form.html', form=form, find_mode='password')


@bp.route('/changepassword/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    form = ChangePasswordForm()

    if request.method == 'POST' and form.validate_on_submit:
        user = User.query.get_or_404(user_id)
        user.password = generate_password_hash(form.password1.data)

        db.session.commit()

        flash('비밀번호가 변경되었습니다.\n새로운 비밀번호로 로그인해주세요.')

        return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html', form=form)
