from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
import time
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import  os
import webbrowser
from gtts import gTTS
from datetime import datetime
from passlib.hash import sha256_crypt
from PIL import Image
from flask import request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# for sqllite 3
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tech_blog.sqlite3'

# for postgresql
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:123@localhost/db'


##### data model   #####
# data base for posts
db_post = SQLAlchemy(app)
class Post(db_post.Model):
    id = db_post.Column('post_id', db_post.Integer, primary_key=True)
    title = db_post.Column(db_post.String(1000))
    category = db_post.Column(db_post.String(100))
    postid = db_post.Column(db_post.String(100), unique=True)
    content = db_post.Column(db_post.String(100000))
    writer = db_post.Column(db_post.String(100))
    date = db_post.Column(db_post.DateTime(timezone=True), nullable=False)
    def __init__(self, title, category, postid, content, writer):
        self.title = title
        self.category = category
        self.postid = postid
        self.content = content
        self.writer = writer
        # t = time.localtime()
        self.date = datetime.now()

    def __repr__(self):
        return '<user %r>' % self.title

def initializie_db_post():
    db_post.create_all()


# data base for users
db_user = SQLAlchemy(app)
class User(db_user.Model):
    id = db_user.Column('user_id', db_user.Integer, primary_key=True)
    username = db_user.Column(db_user.String(100))
    userid = db_user.Column(db_user.String(100), unique=True)
    password = db_user.Column(db_user.String(100))
    email = db_user.Column(db_user.String(100), unique=True)
    mobile = db_user.Column(db_user.String(100), unique=True)
    gender = db_user.Column(db_user.String(100))
    status = db_user.Column(db_user.String(100))
    def __init__(self, userid, username, email, password, gender, mobile, status):
        self.username = username
        self.userid = userid
        self.email = email
        self.password = password
        self.gender = gender
        self.mobile = mobile
        self.status = status
    def __repr__(self):
        return '<user %r>' % self.name

def initializie_db_user():
    db_user.create_all()


# data base for comments
db_comment = SQLAlchemy(app)
class Comment(db_comment.Model):
    id = db_comment.Column('comment_id', db_comment.Integer, primary_key=True)
    userid = db_comment.Column(db_comment.String(100))
    postid = db_comment.Column(db_comment.String(100))
    content = db_comment.Column(db_comment.String(10000))
    date = db_comment.Column(db_comment.DateTime())

    def __init__(self, userid, postid, content):
        self.userid = userid
        self.postid = postid
        self.content = content

        self.date = datetime.now()

    def __repr__(self):
        return '<user %r>' % self.name

def initializie_db_comment():
    db_comment.create_all()


# data base for likes
db_likes = SQLAlchemy(app)
class Likes(db_likes.Model):
    id = db_likes.Column('likes_id', db_likes.Integer, primary_key=True)
    userid = db_likes.Column(db_likes.String(100))
    postid = db_likes.Column(db_likes.String(100))
    status = db_likes.Column(db_likes.String(100))
    def __init__(self, userid, postid, status):
        self.userid = userid
        self.postid = postid
        self.status = status

    def __repr__(self):
        return '<user %r>' % self.name


def initializie_db_likes():
    db_likes.create_all()




@app.before_request
def before_request():
    # before request
    initializie_db_post()
    initializie_db_user()
    initializie_db_comment()
    initializie_db_likes()


@app.route('/')
def index():
    error = ''
    #if user is logged-in
    if 'userid' in session:
        userid = session['userid']
        status = session['status']


    # if user is not logged-in
    else:
        userid = "@none@"
        status="@none@"
    return render_template("index.html", userid=userid,status=status)


@app.route('/login/', methods=["POST", "GET"])
def login():
    if 'userid' in session:
        # already login
        flash('You are already logged-in .', category='warning')
        return redirect(url_for('index'))
    else:
        error1 = ''
        error2 = ''
        if request.method == 'POST':
            try:
                tab = request.form['tab']
                # if login is selected
                if tab == 'login':
                    userid = request.form['userid']
                    password = request.form['password']
                    if not userid or not password:
                        error1 = 'Please enter all field .'
                        return render_template("login.html", userid="@none@", error1=error1, error2=error2)
                    else:
                        usr = User.query.all()

                        for s in usr:
                            if s.userid == userid and sha256_crypt.verify(password,
                                                                          s.password) and ( s.status=='Active'or s.status=='Admin' or s.status=='admin' or s.status=='active'  ):
                                session['userid'] = s.userid
                                session['username'] = s.username
                                session['email'] = s.email
                                session['id'] = s.id
                                session['status'] = s.status
                                flash(' Welcome ' + s.username + ' !', category='success')
                                return redirect(url_for('index'))
                        ###  for inactive user ###

                        usr = User.query.filter_by(userid=userid).all()
                        try:
                            if usr[0].status=='Inactive':
                                error1 ="You are Deactivated Temporarialy ! Contact me for more details .."
                                return render_template("login.html", userid="@none@", error1=error1, error2=error2)
                        except Exception as e:
                            pass
                        error1 = 'Invalid Credentials Please Try Again !'
                        return render_template("login.html", userid="@none@", error1=error1, error2=error2)
                        ##########################
                # if forgot password is selected
                else:
                    username = request.form['username']
                    userid = request.form['userid1']
                    email = request.form['email']
                    mobile = request.form['mobile']

                    if not userid or not mobile or not username or not email:
                        error2 = 'Please enter all field .'
                        return render_template("login.html", userid="@none@", error1=error1, error2=error2)

                    else:

                        usr = User.query.all()
                        for s in usr:
                            if s.userid == userid and s.username == username and s.email == email and s.mobile == mobile:
                                flash(' Welcome ' + s.username + ' !', category='success')
                                flash(' Updated Your Password here . ', category='info')
                                session['userid'] = s.userid
                                session['username'] = s.username
                                session['email'] = s.email
                                session['id'] = s.id
                                session['status'] = s.status

                                return redirect(url_for('profile'))
                        error2 = 'Invalid Credentials Please Try Again !'
                        return render_template("login.html", userid="@none@", error1=error1, error2=error2)
            except Exception as e:
                return render_template("500.html", error=e)

        # get method
        else:
            return render_template("login.html", userid="@none@", error1='', error2='')

@app.route('/logout/')
def logout():
    # remove the username from the session if it is there
    if 'userid' in session:
        flash(' ' + session['username'] + ' you are successfully Logged-out !', category='info')
    else:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    username = session['username']
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('id', None)
    session.pop('status', None)
    return redirect(url_for('index'))


@app.route('/signup/', methods=["POST", "GET"])
def signup():
    if 'userid' in session:
        flash('You need to Logged-out first !', category='warning')
        return redirect(url_for('index'))

    userid = "@none@"
    error = ''
    try:
        if request.method == 'POST':
            gender = request.form['gender']
            password1 = request.form['password1']
            password2 = request.form['password2']
            mobile = request.form['mobile']
            email = request.form['email']
            userid = request.form['userid']
            username = request.form['username']
            status = 'Active'

            try:
                usr1 = User.query.filter_by(userid=userid).all()
                a = usr1[0].userid
                flag1 = True
            except Exception as e:
                flag1 = False
            try:
                usr2 = User.query.filter_by(email=email).all()
                a = usr2[0].email
                flag2 = True
            except Exception as e:
                flag2 = False
            try:
                usr3 = User.query.filter_by(mobile=mobile).all()
                a = usr3[0].mobile
                flag3 = True
            except Exception as e:
                flag3 = False

            if flag1:
                flash(' Userid : ' + userid + ' is already exists.', category='danger')
                return render_template("signup.html", userid="@none@",status='@none@')

            elif flag2:
                flash('Email-id : ' + email + ' is already registered.', category='danger')
                return render_template("signup.html", userid="@none@",status='@none@')

            elif password1 != password2:
                flash('Entered Password does not matches.', category='danger')
                return render_template("signup.html", userid="@none@",status='@none@')

            elif flag3:
                flash('Mobile no : ' + mobile + ' is already registered.', category='danger')
                return render_template("signup.html", userid="@none@",status='@none@')


            else:

                # encrypting the password
                password = sha256_crypt.encrypt(str(password1))

                # saving the corresponding caption
                f = request.files['img']
                u = User.query.all()
                m = 0
                for i in u:
                    m = max(i.id, m)
                if f:
                    f.save("/static/img/profile/" + str(m + 1) + ".jpg")
                else:
                    # default profile picture
                    if gender == 'male':
                        img = "static/img/profile/male.jpg"
                        image = Image.open(img)
                        image.save("static/img/profile/" + userid + ".jpg")

                    else:
                        img = "static/img/profile/female.jpg"
                        image = Image.open(img)
                        image.save("static/img/profile/" + userid + ".jpg")

                initializie_db_user()
                usr = User(userid, username, email, password, gender, mobile, status)
                db_user.session.add(usr)
                db_user.session.commit()
            # starting the session
            session['userid'] = userid
            session['username'] = username
            session['email'] = email
            session['id'] = m + 1
            session['status'] = "Inactive"
            flash('Congratulations ' + username + '.  You are Successfully Logged-in !', category='success')
            return redirect(url_for('index'))


        else:
            # GET method
            return render_template("signup.html", userid="@none@",status='@none@', error=error)
    except Exception as e:
        return render_template("500.html", userid='@none@',status='@none@', error=e)


@app.route('/profile/')
def profile():
    try:
        if 'userid' in session:
            userid = session['userid']
            usr = User.query.filter_by(userid=userid).all()
            user = usr[0]
            return render_template("profile.html", userid=userid,status=session['status'], user=user)

        else:
            userid = "@none@"
            flash('You need to Logged-in first !', category='warning')
            return redirect(url_for('index'))
    except Exception as e:
        return render_template("500.html", userid=session['userid'] ,status=session['status']   , error=e)


@app.route('/update_profile/<form>', methods=["POST", "GET"])
def upadte_profile(form):
    if 'userid' not in session:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    try:
        if request.method == 'POST':
            if form == 'profile_picture':
                f = request.files['file']
                if f:
                    img = "static/img/profile/" + session['userid'] + ".jpg"
                    f.save(img)
                    flash('Profile picture updated successfully . ', category='success')
                    return redirect(url_for('profile'))
                else:
                    flash('Please select a picture . ', category='danger')
                    return redirect(url_for('profile'))

            elif form == 'userid':
                userid = request.form['userid']
                if userid:
                    # if userid  already exists
                    usr1 = User.query.filter_by(userid=userid).all()
                    if usr1:
                        flash(' Userid: ' + userid + ' is already exists.', category='danger')
                        return redirect(url_for('profile'))
                    else:
                        usr = User.query.filter_by(userid=session['userid']).all()
                        posts = Post.query.filter_by(writer=session['userid']).all()
                        cmt = Comment.query.filter_by(userid=session['userid']).all()
                        l = Likes.query.filter_by(userid=session['userid']).all()

                        # UPDATING THE profile picture name
                        os.rename("static/img/profile/" + session['userid'] + ".jpg",
                                  "static/img/profile/" + str(userid) + ".jpg")

                        # updating all field in different tables
                        initializie_db_user()
                        usr[0].userid = userid
                        db_user.session.commit()

                        initializie_db_post()
                        for p in posts:
                            p.writer = userid
                        db_post.session.commit()

                        initializie_db_comment()
                        for c in cmt:
                            c.userid = userid
                        db_comment.session.commit()

                        initializie_db_likes()
                        for c in l:
                            c.userid = userid
                        db_likes.session.commit()

                        session['userid'] = userid

                        flash(' Userid is successfully updated . ', category='success')
                        return redirect(url_for('profile'))

                else:
                    flash('Please enter a userid . ', category='danger')
                    return redirect(url_for('profile'))

            elif form == 'email':
                email = request.form['email']
                if email:
                    # if email  already exists
                    usr1 = User.query.filter_by(email=email).all()
                    if usr1:
                        flash(' Email-id: ' + email + ' is already exists.', category='danger')
                        return redirect(url_for('profile'))
                    else:
                        usr = User.query.filter_by(userid=session['userid']).all()

                        # updating all field in different tables
                        initializie_db_user()
                        usr[0].email = email
                        db_user.session.commit()

                        session['email'] = email

                        flash(' Email-id is successfully updated . ', category='success')
                        return redirect(url_for('profile'))

                else:
                    flash('Please enter a Email-id. ', category='danger')
                    return redirect(url_for('profile'))

            elif form == 'username':
                username = request.form['username']
                if username:
                    usr = User.query.filter_by(userid=session['userid']).all()
                    initializie_db_user()
                    usr[0].username = username
                    db_user.session.commit()
                    flash(' Username is successfully updated . ', category='success')
                    return redirect(url_for('profile'))
                else:
                    flash('Please enter a username . ', category='danger')
                    return redirect(url_for('profile'))

            elif form == 'password':
                password1 = request.form['password1']
                password2 = request.form['password2']
                if password2 and password1:
                    if password2 == password1:
                        # encrypting the password
                        password = sha256_crypt.encrypt(str(password1))

                        usr = User.query.filter_by(userid=session['userid']).all()

                        usr[0].password = password
                        initializie_db_user()
                        db_user.session.commit()
                        flash(' Password is successfully updated . ', category='success')
                        return redirect(url_for('profile'))
                    else:
                        flash('Entered Password does not match  . ', category='danger')
                        return redirect(url_for('profile'))
                else:
                    flash('Please enter password . ', category='danger')
                    return redirect(url_for('profile'))

            elif form == 'mobile':
                mobile = request.form['mobile']
                if mobile:
                    usr3 = User.query.filter_by(mobile=mobile).all()

                    if usr3:
                        flash('Mobile no : ' + usr3[0].mobile + ' is already registered.', category='danger')
                        return redirect(url_for('profile'))
                    else:
                        usr = User.query.filter_by(userid=session['userid']).all()
                        usr[0].mobile = mobile
                        initializie_db_user()
                        db_user.session.commit()
                        flash(' Mobile no. is successfully updated . ', category='success')
                        return redirect(url_for('profile'))


                else:
                    flash('Please enter a mobile no . ', category='danger')
                    return redirect(url_for('profile'))

            elif form == 'delete_account':
                userid = session['userid']
                flag = delete_user(userid)
                return redirect(url_for('logout'))


            else:
                return render_template("500.html", userid=session['userid'] ,status=session['status'], error='Problem in Profile Updation.')


        else:
            return "GET method "
            # return render_template("signup.html", username=username1, error=error)
    except Exception as e:
        return render_template("500.html", userid=session['userid'],status=session['status'], error=e)


@app.route('/post/')
def post():
    if 'userid' in session:
        userid = session['userid']
        status=session['status']
    else:
        userid = "@none@"
        status = "@none@"
    posts = Post.query.filter_by(category="General").all()
    # if items are present in the category
    if posts:
        list = []
        length = 0
        for p in posts:
            list.append(p.postid)
            length = length + 1
        i=random.randint(0, length-1)
        currentid = list[i]
        min_post_id = list[0]
        try:
            max_post_id = list[length - 1]
        except:
            max_post_id = list[0]
        try:
            next_post_id= list[i + 1]
        except:
            next_post_id = list[0]
        try:
            prev_post_id= list[i - 1]
        except:
            prev_post_id = list[i]

        posts = Post.query.filter_by(postid=currentid).all()
        p = posts[0]

        # to find posted time
        tm = posted_time(p)

        # comments
        count_comment =count_comments(p.postid)
        cmt = Comment.query.filter_by(postid=p.postid)


        # likes and dislike
        likes=count_likes(p.postid)
        dislikes=count_dislikes(p.postid)

        return render_template("post.html", userid=userid, post=p, maxid=max_post_id, minid=min_post_id,                               previd=prev_post_id,
                               nextid=next_post_id, p_tm=tm, cmt=cmt,
                               count_comment=count_comment, likes=likes, dislikes=dislikes,status=status, type='normal')

    # if no items in the category
    else:
        flash('This category doesnot contains any post.', category='warning')
        return redirect(url_for('index'))


@app.route('/post/<cid>')
def post1(cid):
    try:
        if 'userid' in session:
            userid = session['userid']
            status = session['status']
        else:
            userid = "@none@"
            status = "@none@"

        # request by pressing category button
        if cid == 'Gr' or cid == 'Tc' or cid == 'Ed' or cid == 'En' or cid == 'Gm':
            cat = category_finder(cid[0:3])
            posts = Post.query.filter_by(category=cat).all()
            # if items are present in the category
            if posts:
                list = []
                length = 0
                for p in posts:
                    list.append(p.postid)
                    length = length + 1

                i = random.randint(0, length - 1)
                currentid = list[i]
                min_post_id = list[0]
                try:
                    max_post_id = list[length - 1]
                except:
                    max_post_id = list[0]
                try:
                    next_post_id = list[i + 1]
                except:
                    next_post_id = list[0]
                try:
                    prev_post_id = list[i - 1]
                except:
                    prev_post_id = list[i]

                posts = Post.query.filter_by(postid=currentid).all()
                p = posts[0]

                # to find posted time
                tm = posted_time(p)

                # comments
                count_comment = count_comments(p.postid)
                cmt = Comment.query.filter_by(postid=p.postid)

                # likes and dislikes
                likes = count_likes(p.postid)
                dislikes = count_dislikes(p.postid)

                return render_template("post.html", userid=userid, post=p, maxid=max_post_id, minid=min_post_id, previd=prev_post_id,
                                       nextid=next_post_id, p_tm=tm, cmt=cmt,
                                       count_comment=count_comment, likes=likes, dislikes=dislikes,status=status, type='normal')


            # if no items in the category
            else:
                flash('This category doesnot contains any post.', category='warning')
                return redirect(url_for('index'))



        # request by next or prev button
        else:

            cat = category_finder(cid[0:2])
            currentid = cid[:]

            posts = Post.query.filter_by(category=cat).all()
            if posts:
                list = []
                length = 0
                for p in posts:
                    list.append(p.postid)
                    length = length + 1
                pos=0
                for i in list:
                    if i==currentid:
                        break
                    pos=pos+1
                i= pos


                minid = list[0]
                try:
                    maxid = list[length - 1]
                except:
                    maxid = list[0]
                try:
                    nextid = list[i + 1]
                except:
                    nextid = list[0]
                try:
                    previd = list[i - 1]
                except:
                    previd = list[i]

                posts = Post.query.filter_by(postid=currentid).all()
                p = posts[0]

            # to find posted time
            tm = posted_time(p)

            # comments
            count_comment = count_comments(p.postid)
            cmt = Comment.query.filter_by(postid=p.postid)

            # likes and dislike
            likes = count_likes(p.postid)
            dislikes = count_dislikes(p.postid)

            audio_creater(p)




            return render_template("post.html", userid=userid, post=p, maxid= maxid, minid=minid, previd=previd,
                                   nextid=nextid, p_tm=tm, cmt=cmt,
                                   count_comment=count_comment, likes=likes, dislikes=dislikes,status=status    , type = 'normal')

    except Exception as e:
        return render_template("500.html", userid=session['userid'],status=status, error=e)

@app.route('/add_post/', methods=["POST", "GET"])
def add_post():
    try:
        error = ''
        if 'userid' in session:
            if request.method == 'POST':
                initializie_db_post()
                title = request.form['title']
                content = request.form['content']
                category = request.form['category']
                f = request.files['file']

                # to generate cid automatically
                posts = Post.query.filter_by(category=category).all()
                if posts:
                    maxid = max_id_post(posts)
                    m_id = int(maxid[3:5])
                    m_id = m_id + 1
                else:
                    m_id = 1
                postid = post_id_generator(category, m_id)
                error = ''
                post = Post(title, category, postid, content, session['userid'])
                db_post.session.add(post)
                db_post.session.commit()
                # saving the corresponding caption
                if f:
                    f.save("static/img/posts/" + str(postid) + ".jpg")
                # deafault post picture
                else:
                    img = "static/img/posts/default.jpg"
                    image = Image.open(img)
                    image.save("static/img/posts/" + str(postid) + ".jpg")
                post = Post.query.filter_by(postid=postid).all()
                # To create mp4 file
                audio_creater(post[0])
                flash('Post Added Successfully !', category='success')
                return redirect(url_for('post1', cid=postid))
            else:
                # return "GET method oops!"
                return render_template("add_post.html", userid=session['userid'] ,status=session['status'], error=error, writer=session['userid'])
        else:
            flash('You need to Logged-in first !', category='warning')
            return redirect(url_for('index'))


    except Exception as e:
        return render_template("500.html", userid=session['userid'] ,status=session['status'], error=e)

@app.route('/my_post/<postid>', methods=["POST", "GET"])
def my_post(postid):
    if 'userid' in session:
        userid = session['userid']
        status = session['status']
    else:
        userid = "@none@"
        status = "@none@"
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))

    s = postid.split('+', 1)
    search_writer = s[0]
    postid = s[1]

    if request.method == 'POST':
        search_writer = session['userid']
        posts = Post.query.filter_by(writer=search_writer).all()
        if posts:
            list = []
            length = 0
            for p in posts:
                list.append(p.postid)
                length = length + 1

            i = int(length / 2)
            currentid = list[i]
            minid = list[0]
            try:
                maxid = list[length - 1]
            except:
                maxid = list[0]
            try:
                nextid = list[i + 1]
            except:
                nextid = list[0]
            try:
                previd = list[i - 1]
            except:
                previd = list[i]

            posts = Post.query.filter_by(postid=currentid).all()
            p = posts[0]

            # to find posted time
            tm = posted_time(p)

            # comments
            count_comment = count_comments(p.postid)
            cmt = Comment.query.filter_by(postid=p.postid)

            # likes and dislikes
            likes = count_likes(p.postid)
            dislikes = count_dislikes(p.postid)

            return render_template("my_post.html", userid=userid, post=p, maxid=maxid, minid=minid, previd=previd,
                                   nextid=nextid, p_tm=tm, cmt=cmt,
                                   count_comment=count_comment, likes=likes, dislikes=dislikes,status=status, type='search_writer')
        else:
            flash('Something went wrong ...  ! ', category='warning')
            return redirect(url_for('index', cid=postid))
    # get method
    else:
        posts = Post.query.filter_by(writer=search_writer).all()
        if posts:
            list = []
            length = 0
            for p in posts:
                list.append(p.postid)
                length = length + 1
            for i in range(0, length):
                if list[i] == postid:
                    break

            currentid = list[i]
            minid = list[0]
            try:
                maxid = list[length - 1]
            except:
                maxid = list[0]
            try:
                nextid = list[i + 1]
            except:
                nextid = list[0]
            try:
                previd = list[i - 1]
            except:
                previd = list[i]

            posts = Post.query.filter_by(postid=currentid).all()
            p = posts[0]

            # to find posted time
            tm = posted_time(p)

            # comments
            cmt = Comment.query.filter_by(postid=p.postid)
            count_comment = 0
            if cmt:
                for c in cmt:
                    count_comment = count_comment + 1

            else:
                count_comment = 0

            # likes and dislike
            likes = 0
            dislikes = 0
            l1 = Likes.query.filter_by(status='like', postid=p.postid).all()
            l2 = Likes.query.filter_by(status='dislike', postid=p.postid).all()
            if l1:
                for l in l1:
                    likes = likes + 1
            else:
                likes = 0
            if l2:
                for l in l2:
                    dislikes = dislikes + 1
            else:
                dislikes = 0

            return render_template("my_post.html", userid=userid, post=p, maxid=maxid, minid=minid, previd=previd,
                               nextid=nextid, p_tm=tm, cmt=cmt,
                               count_comment=count_comment, likes=likes, dislikes=dislikes, status=status, type='search_writer')

        else:
            flash('You blogs does not exists in the system ! ', category='info')
            return redirect(url_for('index', cid=postid))

@app.route('/post_update/<postid>', methods=["POST", "GET"])
def post_update(postid):
        error = ''
        if 'username' not in session:
            flash('You need to Logged-in first !', category='warning')
            return redirect(url_for('index'))

        #### Update the given Post ##########
        post = Post.query.filter_by(postid=postid).all()
        if request.method == 'POST':
            initializie_db_post()
            title = request.form['title']
            content = request.form['content']
            f = request.files['file']
            if not f:
                # do not  want to change image
                pass
            else:
                # update image
                f.save("static/img/posts/" + str(postid) + ".jpg")


            # updating mp4 file

            file = 'C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\\audio\\' +postid + '.mp4'
            os.remove(file)
            tts = gTTS(text= title +"  ..  This blog is Posted by " + post[0].writer + ". .. " +content,  lang='en', slow=False)
            tts.save(file)
            #return content
            initializie_db_post()
            post[0].title=title
            post[0].content = content
            db_post.session.commit()


            flash('Post Updated Successfully !', category='success')
            return redirect(url_for('my_post', postid=post[0].writer+'+'+postid))
        # "GET method "
        else:
            post = Post.query.filter_by(postid=postid).all()
            if post:
                p=post[0]
                return render_template("update_post.html",status=session['status'], userid=session['userid'], error=error,
                                       writer=session['userid'],post=p)

            else:
                flash('Post Does not Exists  !', category='Warning')
                return redirect(url_for('index'))

@app.route('/delete_mypost/<postid>')
def delete_mypost(postid):
    error = ''
    if 'username' not in session:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    flag = delete_post(postid)
    if flag:
        return redirect(url_for('my_post', postid=session['userid'] + '+'))
    else:
        return redirect(url_for('my_post', postid=session['userid'] + '+' + postid))

@app.route('/comment_process/<string>', methods=["POST", "GET"])
def comment_process(string):
    if 'userid' not in session:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    if request.method == 'POST':
        content = request.form['content']
        s = string.split('+')
        userid = str(s[0])
        postid = str(s[1])
        postid, type = postid.split('*')
        if type == 'normal':
            initializie_db_comment()
            cmt = Comment(userid, postid, content)
            db_comment.session.add(cmt)
            db_comment.session.commit()
            flash('Your Comment saved successfully !', category='success')
            return redirect(url_for('post1', cid=postid))
        else:
            p = Post.query.filter_by(postid=postid).all()
            postid = p[0].writer + '+' + p[0].postid
            initializie_db_comment()
            cmt = Comment(userid, p[0].postid, content)
            db_comment.session.add(cmt)
            db_comment.session.commit()
            flash('Your Comment saved successfully !', category='success')
            return redirect(url_for('search_writer', postid=postid))

@app.route('/likes_process/<string>')
def likes(string):
    error = ''
    if 'userid' in session:
        s, postid = string.split('+')
        postid, type = postid.split('*')
        userid = session['userid']


        initializie_db_likes()
        l = Likes.query.filter_by(userid=userid, postid=postid).all()
        if type == 'normal':
            # like
            if s == "like":
                if l:
                    # already dislike
                    if l[0].status == "dislike":
                        l[0].status = "like"
                        db_likes.session.commit()
                        # return " changing dislike into like"
                        return redirect(url_for('post1', cid=postid))
                    else:
                        # return "already like "
                        return redirect(url_for('post1', cid=postid))
                # neither like or dislike previously
                else:
                    l = Likes(userid, postid, s)
                    db_likes.session.add(l)
                    db_likes.session.commit()
                    # return "new like"
                    return redirect(url_for('post1', cid=postid))
            # dislike
            else:
                if l:
                    # already like
                    if l[0].status == "like":
                        l[0].status = "dislike"
                        db_likes.session.commit()
                        # return " changing like into dislike"
                        return redirect(url_for('post1', cid=postid))
                    else:
                        # return "already dislike "
                        return redirect(url_for('post1', cid=postid))

                # neither like or dislike previously
                else:
                    l = Likes(userid, postid, s)
                    db_likes.session.add(l)
                    db_likes.session.commit()
                    # return "new dislike"
                    return redirect(url_for('post1', cid=postid))
        # search_writer
        else:
            p = Post.query.filter_by(postid=postid).all()
            postid = p[0].writer + '+' + p[0].postid

            # like
            if s == "like":
                if l:
                    # already dislike
                    if l[0].status == "dislike":
                        l[0].status = "like"
                        db_likes.session.commit()
                        # return " changing dislike into like"
                        return redirect(url_for('search_writer', postid=postid))
                    else:
                        # return "already like "
                        return redirect(url_for('search_writer', postid=postid))
                # neither like or dislike previously
                else:
                    l = Likes(userid, p[0].postid, s)
                    db_likes.session.add(l)
                    db_likes.session.commit()
                    # return "new like"
                    return redirect(url_for('search_writer', postid=postid))
            # dislike
            else:
                if l:
                    # already like
                    if l[0].status == "like":
                        l[0].status = "dislike"
                        db_likes.session.commit()
                        # return " changing like into dislike"
                        return redirect(url_for('search_writer', postid=postid))
                    else:
                        # return "already dislike "
                        return redirect(url_for('search_writer', postid=postid))

                # neither like or dislike previously
                else:
                    l = Likes(userid, p[0].postid, s)
                    db_likes.session.add(l)
                    db_likes.session.commit()
                    # return "new dislike"
                    return redirect(url_for('search_writer', postid=postid))



    else:
        userid = "@none@"
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))

@app.route('/search_writer/<postid>', methods=["POST", "GET"])
def search_writer(postid):
    if 'userid' in session:
        userid = session['userid']
        status = session['status']
    else:
        userid = "@none@"
        status = "@none@"

    s = postid.split('+', 1)
    search_writer = s[0]
    postid = s[1]

    if request.method == 'POST':
        search_writer = request.form['search_writer']

        posts = Post.query.filter_by(writer=search_writer).all()
        if posts:
            list = []
            length = 0
            for p in posts:
                list.append(p.postid)
                length = length + 1

            i = int(length / 2)
            currentid = list[i]
            minid = list[0]
            try:
                maxid = list[length - 1]
            except:
                maxid = list[0]
            try:
                nextid = list[i + 1]
            except:
                nextid = list[0]
            try:
                previd = list[i - 1]
            except:
                previd = list[i]

            posts = Post.query.filter_by(postid=currentid).all()
            p = posts[0]

            # to find posted time
            tm = posted_time(p)

            # comments
            count_comment = count_comments(p.postid)
            cmt = Comment.query.filter_by(postid=p.postid)

            # likes and dislikes
            likes = count_likes(p.postid)
            dislikes = count_dislikes(p.postid)

            return render_template("post.html", userid=userid, post=p, maxid=maxid, minid=minid, previd=previd,
                                   nextid=nextid, p_tm=tm, cmt=cmt,
                                   count_comment=count_comment, likes=likes, dislikes=dislikes,status=status, type='search_writer')
        elif search_writer:
            flash('Writer Name : ' + search_writer + ' does not found. Please check your spelling  ! ',
                  category='danger')
            return redirect(url_for('post1', cid=postid))
        else:
            flash('Please enter a Writer Name  ! ', category='danger')
            return redirect(url_for('post1', cid=postid))


    else:
        # get method
        posts = Post.query.filter_by(writer=search_writer).all()
        if posts:
            list = []
            length = 0
            for p in posts:
                list.append(p.postid)
                length = length + 1
            for i in range(0, length):
                if list[i] == postid:
                    break

            currentid = list[i]
            minid = list[0]
            try:
                maxid = list[length - 1]
            except:
                maxid = list[0]
            try:
                nextid = list[i + 1]
            except:
                nextid = list[0]
            try:
                previd = list[i - 1]
            except:
                previd = list[i]

            posts = Post.query.filter_by(postid=currentid).all()
            p = posts[0]

            # to find posted time
            tm = posted_time(p)

            # comments
            cmt = Comment.query.filter_by(postid=p.postid)
            count_comment = 0
            if cmt:
                for c in cmt:
                    count_comment = count_comment + 1

            else:
                count_comment = 0

            # likes and dislike
            likes = 0
            dislikes = 0
            l1 = Likes.query.filter_by(status='like', postid=p.postid).all()
            l2 = Likes.query.filter_by(status='dislike', postid=p.postid).all()
            if l1:
                for l in l1:
                    likes = likes + 1
            else:
                likes = 0
            if l2:
                for l in l2:
                    dislikes = dislikes + 1
            else:
                dislikes = 0

        return render_template("post.html", userid=userid, post=p, maxid=maxid, minid=minid, previd=previd,
                               nextid=nextid, p_tm=tm, cmt=cmt,
                               count_comment=count_comment, likes=likes, dislikes=dislikes,status=status, type='search_writer')

@app.route('/admin/<str>', methods=["POST", "GET"])
def admin(str):
    error = ''
    if 'username' not in session:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    elif session['status'] != 'Admin':
        flash('You are not Admin !', category='warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        #### Change the user Status to Inactive ##########
        if str == 'user_deactivate':
            userid = request.form['user']
            usr = User.query.filter_by(userid=userid).all()
            if userid == '':
                flash('Please enter an User id !', category='warning')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            elif usr:
                initializie_db_user()
                usr[0].status = "Inactive"
                db_user.session.commit()
                flash('User id : ' + userid + ' is Deactivated !.', category='success')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            else :
                flash('User id : ' + userid + ' is not found !', category='danger')
                return render_template("admin.html", userid=session['userid'], status=session['status'])

        #### Change the user Status to Active ##########
        elif str == 'user_activate':
            userid = request.form['user']
            usr = User.query.filter_by(userid=userid).all()
            if userid == '':
                flash('Please enter an User id !', category='warning')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            elif usr:
                initializie_db_user()
                usr[0].status = "Active"
                db_user.session.commit()
                flash('User id : ' + userid + ' is Activated !.', category='success')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            else:
                flash('User id : ' + userid + ' is not found !', category='danger')
                return render_template("admin.html", userid=session['userid'], status=session['status'])

        #### Promoted a user Status to Admin ##########
        elif str == 'admin':
            userid = request.form['user']
            usr = User.query.filter_by(userid=userid).all()
            if userid == '':
                flash('Please enter an User id !', category='warning')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            elif usr:
                initializie_db_user()
                usr[0].status = "Admin"
                db_user.session.commit()
                flash('User id : ' + userid + ' is promoted to Admin !.', category='success')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            else:
                flash('User id : ' + userid + ' is not found !', category='danger')
                return render_template("admin.html", userid=session['userid'], status=session['status'])

        #### Delete the user   ##########
        elif str == 'user_delete':
            userid = request.form['user']
            if userid == '':
                flash('Please enter an User id !', category='warning')
                return render_template("admin.html", userid=session['userid'], status=session['status'])

            flag=delete_user(userid)
            return render_template("admin.html", userid=session['userid'], status=session['status'])

        #### Delete the given Post ##########
        elif str == 'post':
            postid = request.form['postid']
            if postid == '':
                flash('Please enter a Post id !', category='warning')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            flag = delete_post(postid)
            return render_template("admin.html", userid=session['userid'], status=session['status'])

        #### Delete the given comment ##########
        elif str == 'comment':
            commentid = request.form['commentid']
            if commentid == '':
                flash('Please enter a Comment id !', category='warning')
                return render_template("admin.html", userid=session['userid'], status=session['status'])
            flag = delete_comment(commentid)
            return render_template("admin.html", userid=session['userid'], status=session['status'])
    else:
        return render_template("admin.html", userid=session['userid'], status=session['status'])

@app.route('/posts_details/')
def posts_details():
    error = ''
    if 'username' not in session:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    elif session['status'] != 'Admin':
        flash('You are not Admin !', category='warning')
        return redirect(url_for('index'))

    string = '  Post-id  ||  Comments ||   Likes  ||   Dislikes  ||   Writer \n  '
    list = []
    i = 0
    try:
        post = Post.query.all()

        for p in post:
            string=string+ str(p.postid)+" --------- "

            # comment count
            cmt = Comment.query.filter_by(postid=p.postid)
            count_comment = 0
            if cmt:
                for c in cmt:
                    count_comment = count_comment + 1

            else:
                count_comment = 0
            string = string + str(count_comment) + " ----------- "
            # likes and dislike
            likes = 0
            dislikes = 0
            l1 = Likes.query.filter_by(status='like', postid=p.postid).all()
            l2 = Likes.query.filter_by(status='dislike', postid=p.postid).all()
            if l1:
                for l in l1:
                    likes = likes + 1
            else:
                likes = 0
            if l2:
                for l in l2:
                    dislikes = dislikes + 1
            else:
                dislikes = 0
            string = string + str(likes) + " --------- "
            string = string + str(dislikes) + " ----------- "
            string = string + str(p.writer) + "\n  "

        return render_template("information.html", userid=session['userid'] ,status=session['status']  , title=' Posts Details',
                               subheading=' Posts Details', name="posts_details", string=string)

    except Exception as e:
        return render_template("500.html", userid=session['userid'] ,status=session['status'], error=e)

@app.route('/comments_details/')
def comments_details():
        error = ''
        if 'username' not in session:
            flash('You need to Logged-in first !', category='warning')
            return redirect(url_for('index'))
        elif session['status'] != 'Admin':
            flash('You are not Admin !', category='warning')
            return redirect(url_for('index'))

        string ='  Id  ||  Post-id  ||   User-id    ||\t  Content\t\t\t\t\t\t\t\t\t   \n  '
        list = []
        i = 0
        try:
            cmt = Comment.query.all()

            for c in cmt:
                string = string + str(c.id) + " ----- "
                string = string + str(c.postid) + " ------- "
                string = string + str(c.userid) + " -------- "
                string = string + str(c.content) + " \n  "

            return render_template("information.html", userid=session['userid'] ,status=session['status'], title=' Comments Details',
                                   subheading=' Comments Details', string=string)

        except Exception as e:
            return render_template("500.html", userid=session['userid'] ,status=session['status'] , error=e)

@app.route('/display_users/')
def display_users():
        error = ''
        if 'username' not in session:
            flash('You need to Logged-in first !', category='warning')
            return redirect(url_for('index'))
        elif session['status'] != 'Admin':
            flash('You are not Admin !', category='warning')
            return redirect(url_for('index'))

        string ='  Id  ||  Username  ||   User-id    ||   Status  ||     Mobile      ||     Email   \n  '
        list = []
        i = 0
        try:
            usr = User.query.all()

            for u in usr:
                string = string + str(u.id) + " ----- "
                string = string + str(u.username) + " ------- "
                string = string + str(u.userid) + " ------- "
                string = string + str(u.status) + " ------- "
                string = string + str(u.mobile) + " ------- "
                string = string + str(u.email) + " \n  "

            return render_template("information.html", userid=session['userid'] ,status=session['status'] , title=' Users Details',
                                   subheading=' Users Details',  string=string)

        except Exception as e:
            return render_template("500.html", userid=session['userid'] ,status=session['status'] , error=e)

@app.route('/contact_details/')
def contact_details():
    error = ''
    if 'username' not in session:
        flash('You need to Logged-in first !', category='warning')
        return redirect(url_for('index'))
    elif session['status'] != 'Admin':
        flash('You are not Admin !', category='warning')
        return redirect(url_for('index'))

    try:
        string=file_read()
        return render_template("information.html", userid=session['userid'],title=' Contact Details',subheading=' Contact Details',name='conatct_datails',string=string)
    except Exception as e:
        return render_template("500.html", userid=session['userid'], error=e)

@app.route('/about/')
def about():
    if 'userid' in session:
        userid = session['userid']
        status = session['status']
    else:
        userid = "@none@"
        status = "@none@"

    return render_template("about.html", userid=userid ,status=status)


@app.route('/contact/', methods=["POST", "GET"])
def contact():
    if 'userid' in session:
        userid = session['userid']
        status = session['status']
    else:
        userid = "@none@"
        status = "@none@"

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        country = request.form['country']
        phone = request.form['phone']
        city = request.form['city']
        message = request.form['message']
        address = request.form['address']
        #Storing data on Contact_record.text
        str = '\n-----------------------------------------\n   First Name : ' + first_name + '\n   Last Name : ' + last_name + '\n   Email : ' + email + '\n   Country : ' + country + '\n   Phone : ' + phone + '\n   City : ' + city + '\n   Address : ' + address+ '\n   Message : ' + message
        file_write(str)
        flash('Congratulations your message is successfully send !', category='success')
        return redirect(url_for('index'))

    else:
        return render_template("contact.html", userid=userid ,status=status)


@app.errorhandler(404)
def page_not_found(e):
    if 'userid' in session:
        userid = session['userid']
        status = session['status']
    else:
        userid = "@none@"
        status = "@none@"

    return render_template("404.html", userid=userid ,status=status, error=e)





######### Function Body   ###########

def audio_creater(post):
    file = 'C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\\audio\\' + post.postid + '.mp4'
    try:
        os.rename(file,file)
        #webbrowser.open(file)
        return True
    except:
        tts = gTTS(text= post.title +"  ..  This blog is Posted by " + post.writer + ". .. " +  post.content,
                   lang='en', slow=False)
        file = 'C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\\audio\\' + post.postid + '.mp4'
        tts.save(file)

        return False




# to write contact details
def file_write(data):
    file_object = open('Contact_record.text', 'a+')
    file_object.write(data)
    file_object.close()
# to read contact details
def file_read():
    file_object = open('Contact_record.text','r')
    str = file_object.read()
    file_object.close()
    return str


### counting comments for a given post ###
def count_comments(postid):
    cmt = Comment.query.filter_by(postid=postid)
    count_comment = 0
    if cmt:
        for c in cmt:
            count_comment = count_comment + 1

    else:
        count_comment = 0

    return count_comment

### counting likes for a given post ###
def count_likes(postid):
    likes = 0
    lk = Likes.query.filter_by(status='like', postid=postid).all()
    if lk:
        for l in lk:
            likes = likes + 1
    else:
        likes = 0

    return likes

### counting dislikes for a given post ###
def count_dislikes(postid):
    dislikes = 0
    dlk = Likes.query.filter_by(status='dislike', postid=postid).all()
    if dlk:
        for l in dlk:
            dislikes = dislikes + 1
    else:
        dislikes = 0

    return dislikes

### delete the given user ###
def delete_user(userid):
    user = User.query.filter_by(userid=userid).all()
    if user:
        initializie_db_user()
        db_user.session.delete(user[0])
        os.remove("C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\img\profile\\"+ userid + ".jpg")
        db_user.session.commit()
        ### Also we need to delete all the posts and comments and like/dislike by that user###
        post = Post.query.filter_by(writer=userid).all()
        if post:
            initializie_db_post()
            db_post.session.delete(post[0])
            os.remove("C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\img\posts\\" + post[0].postid + ".jpg")
            db_post.session.commit()

        cmt = Comment.query.filter_by(userid=userid).all()
        if cmt:
            initializie_db_comment()
            for c in cmt:
                db_comment.session.delete(c)
            db_comment.session.commit()

        like = Likes.query.filter_by(userid=userid).all()
        if like:
            initializie_db_likes()
            for c in like:
                db_likes.session.delete(c)
            db_likes.session.commit()
        ################################################################
        flash(' User is Successfully Deleted !.', category='success')
        return True
    else:
        flash(' User Deletion  is failed !', category='danger')
        return  False


### delete the given post ###
def delete_post(postid):
    post = Post.query.filter_by(postid=postid).all()
    if post:
        initializie_db_post()
        db_post.session.delete(post[0])
        os.remove("C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\img\posts\\" + postid + ".jpg")
        os.remove("C:\\Users\hitesh\AppData\Local\Programs\Python\Python35\Flask Projects\TechBlog\static\\audio\\" + postid + ".mp4")
        db_post.session.commit()
        ### Also we need to delete all the comments and like/dislike ###
        cmt = Comment.query.filter_by(postid=postid).all()
        if cmt:
            initializie_db_comment()
            for c in cmt:
                db_comment.session.delete(c)
            db_comment.session.commit()
        like = Likes.query.filter_by(postid=postid).all()
        if like:
            initializie_db_likes()
            for c in like:
                db_likes.session.delete(c)
            db_likes.session.commit()
        ################################################################
        flash(' Post is Successfully Deleted !.', category='success')
        return True
    else:
        flash(' Post Deletion  is failed ! ', category='danger')
        return  False


### delete the given comment ###
def delete_comment(commentid):
    cmt = Comment.query.filter_by(id=commentid).all()
    if cmt:
        initializie_db_post()
        for c in cmt:
            pass
        db_comment.session.delete(c)
        db_comment.session.commit()
        flash(' Comment is Successfully Deleted !.', category='success')
        return True
    else:
        flash(' Comment Deletion  is failed ! ', category='danger')
        return False


def months(m):
    if m == 1:
        month = "January"
    elif m == 2:
        month = "February"
    elif m == 3:
        month = "March"
    elif m == 4:
        month = "April"
    elif m == 5:
        month = "May"
    elif m == 6:
        month = "June"
    elif m == 7:
        month = "July"
    elif m == 8:
        month = "August"
    elif m == 9:
        month = "September"
    elif m == 10:
        month = "October"
    elif m == 11:
        month = "November"
    else:
        month = "December"
    return month


def post_id_generator(category, m_cid):
    if category == 'General':
        cid = 'Gr'
    elif category == 'Education':
        cid = 'Ed'
    elif category == 'Technology':
        cid = 'Tc'
    elif category == 'Gamming':
        cid = 'Gm'
    else:
        cid = 'En'
    m_cid = str(m_cid)
    cid = cid + '-' + m_cid
    return cid




def category_finder(cid):
    if cid == 'Gr':
        category = 'General'
    elif cid == 'Ed':
        category = 'Education'
    elif cid == 'Tc':
        category = 'Technology'
    elif cid == 'Gm':
        category = 'Gamming'
    else:
        category = 'Entertainment'
    return category


def max_id_post(posts):
    m = 0
    for p in posts:
        m = max(int(p.postid[3:]), m)
    return p.postid[:3] + str(m)


# to find posted time
def posted_time(p):
    t = time.localtime()
    # same day
    if t.tm_mday - p.date.day == 0 and t.tm_mon - p.date.month == 0 and t.tm_year - p.date.year == 0 and t.tm_hour - p.date.hour == 0:
        return str(t.tm_min - p.date.minute) + ' Minutes ago'
    # same day
    elif t.tm_mday - p.date.day == 0 and t.tm_mon - p.date.month == 0 and t.tm_year - p.date.year == 0:
        return str(t.tm_hour - p.date.hour) + ' Hours ago'
    # same month
    elif t.tm_mon - p.date.month == 0 and t.tm_year - p.date.year == 0:
        return str(t.tm_mday - p.date.day) + ' Days ago '
    # same year
    elif t.tm_year - p.date.year == 0:
        return str(t.tm_mon - p.date.month) + ' Months ago '

    else:
        return str(t.tm_year - p.date.year) + ' Years ago '


def verify_mobile(mobile):
    c = 0
    for i in mobile:
        c = c + 1
    if c != 10:
        return True
    try:
        if int(mobile) / 10:
            return False
    except Exception as e:
        return True

def verify_email(email):
    if (email.find('@'))==-1  or (email.find('.com'))==-1:
        return True
    if email.index('@')+3 <email.index('.') and email.index('@')>3:
        return False
    else :
        return True


#####################################


if __name__ == '__main__':

    app.run(debug=True)