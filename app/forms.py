from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired('제목은 필수입력 항목입니다.')])
    content = TextAreaField('내용', validators=[])
    category_type = StringField('카테고리', validators=[DataRequired('카테고리는 필수입력 항목입니다.')])


class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('답변 내용은 필수입력 항목입니다.')])


class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired('아이디는 필수입력 항목입니다.'), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수입력 항목입니다.'), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired('비밀번호 확인은 필수입력 항목입니다.')])
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력 항목입니다.'), Email()])


class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired('아이디는 필수입력 항목입니다.'), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수입력 항목입니다.')])


class FindIdForm(FlaskForm):
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력 항목입니다.'), Email()])


class FindPasswordForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired('아이디는 필수입력 항목입니다.'), Length(min=3, max=25)])
    email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력 항목입니다.'), Email()])


class ChangePasswordForm(FlaskForm):
    password1 = PasswordField('새로운 비밀번호', validators=[DataRequired('새로운 비밀번호는 필수입력 항목입니다.'), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired('비밀번호 확인은 필수입력 항목입니다.')])


class CommentForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('댓글 내용은 필수입력 항목입니다.')])
