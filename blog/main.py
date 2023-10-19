import re
import hmac
import hashlib
from flask import Flask, request, render_template, redirect, make_response
from .db_setup import Post, Base, engine, User
from sqlalchemy.orm import sessionmaker
 
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
SECRET_KEY = 'django-insecure-d)4hdz49%1g_^cyefc&wez^c$yumvmh)4md(wh=(8t$l9tw^6g'


def make_password_val(password):
    return f'{hash_str(password)}|{SECRET_KEY}'


def check_password_val(password, key, hash):
    h = f'{hash_str(password, key)}'

    return h == hash


def hash_str(s, key=SECRET_KEY):
    return hmac.new(key.encode(), s.encode(), hashlib.md5).hexdigest()


def make_secure_val(s):
    s = str(s)
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    val = h.split('|')[0]
    return h == make_secure_val(val)


@app.route('/blog')
def show_posts():
    posts = session.query(Post).all()
    return render_template('posts.html', posts=posts)


@app.route('/blog.json')
def jsonify():
    import json
    posts = session.query(Post).all()
    return json.dumps([p.as_dict() for p in posts])


@app.route('/post-created/<id>')
def post_created(id):
    newpost = session.query(Post).filter_by(id=int(id)).first()
    return render_template('post.html', p=newpost)


@app.route('/newpost', methods=['get', 'post'])
def create_post():
    if request.method == 'POST':
        subject = request.form.get('subject', None)
        post = request.form.get('post', None)

        if subject and post:
            newpost = Post(subject=subject, post=post)
            session.add(newpost)
            session.commit()
            return redirect(f'/post-created/{newpost.id}')
        else:
            return render_template('postform.html', error='subject or post is empty!')

    return render_template('postform.html')


@app.route('/welcome')
def welcome():
    user_id_cookie = request.cookies.get('user_id', None)

    if user_id_cookie and check_secure_val(user_id_cookie):
        user_id = int(user_id_cookie.split('|')[0])
        user = session.query(User).filter_by(id=user_id).first()
        return f'Welcome {user.username}'
    else:
        return redirect('/signup')


@app.route('/logout')
def logout():
    user_id_cookie = request.cookies.get('user_id', None)

    if user_id_cookie:
        response = make_response(redirect('/'))
        response.set_cookie('user_id', '')

        return response


@app.route('/signup', methods=['get', 'post'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        verify = request.form.get('verify', None)
        email = request.form.get('email', None)

        is_error = error_email = error_password = error_username = None

        if not username:
            error_username = 'Username is not valid'
            is_error = True

        if password != verify:
            error_password = 'Password is not valid'
            is_error = True

        if not validate_email(email):
            error_email = 'Email is not valid'
            is_error = True

        if is_error:
            return render_template(
                'signup.html', error_email=error_email, error_username=error_username, error_password=error_password
            )

        newuser = User(username=username, password=make_password_val(password), email=email)
        session.add(newuser)
        session.commit()

        newuser = session.query(User).filter_by(username=username).first()
        response = make_response(redirect('/welcome'))
        response.set_cookie('user_id', make_secure_val(newuser.id))

        return response

    return render_template('signup.html')


@app.route('/signin', methods=['get', 'post'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        is_error = error_username = None

        if not username:
            error_username = 'Username is not valid'
            is_error = True

        if is_error:
            return render_template('signin.html', error_username=error_username)

        user = session.query(User).filter_by(username=username).first()
        password_hash_words = user.password.split('|')
        if check_password_val(password, password_hash_words[1], password_hash_words[0]):
            res = make_response(redirect('/welcome'))
            res.set_cookie('user_id', make_secure_val(user.id))

            return res

        else:
            error_password = 'password is not correct'
            return render_template('signin.html', error_username=error_username, error_password=error_password)

    return render_template('signin.html')


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True

    return False


@app.route('/set-cookie')
def setcookie():
    visits = 0
    visit_cookie_val = request.cookies.get('visits')

    if visit_cookie_val:
        is_secure_val = check_secure_val(visit_cookie_val)
        if is_secure_val:
            visits = int(visit_cookie_val.split('|')[0])

    visits = visits + 1

    res = make_response(f'You ve visited us for {visits} times')
    res.set_cookie('visits', make_secure_val(visits))

    return res


if __name__=='__main__':
    app.run()
