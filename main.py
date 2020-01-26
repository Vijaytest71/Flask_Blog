from flask import Flask,render_template,request,session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from _datetime import datetime
from werkzeug import secure_filename
import json
import os
# plase create comment dynamicaly like post it available in Single.html

with open('config.json','r') as c:
 params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'supe-secret_key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)

mail =Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


db = SQLAlchemy(app)

class Contacts(db.Model):
    srno = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12),nullable=False)
    msg = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(12),nullable=True)
    email = db.Column(db.String(20) ,nullable=False)

class Comments(db.Model):
    srno = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12),nullable=False)
    message = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(12),nullable=True)
    email = db.Column(db.String(20) ,nullable=False)

class Posts(db.Model):
    srno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(120),nullable=False)
    content = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(12),nullable=True)
    img_file = db.Column(db.String(12), nullable=False)

# img not get store in location
@app.route("/uploader", methods=["GET", "POST"])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
    return "Uploaded Successfully"

#next and previous button work remain in post.html Video - 19
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params=params, post = post)

"""
@app.route("/post")
def post_route():
    posts = Posts.query.filter_by().all()
    return render_template('post.html', params=params, post = posts)
"""
#you can do this thing with single
#not working
@app.route("/getcomment", methods = ["GET"])
def getcomment():
    comments = Comments.query.filter_by().all()
    return render_template('single.html', params=params, comments = comments)

#not working
@app.route("/delete/<string:srno>", methods = ['GET','POST'])
def delete(srno):
          post = Posts.query.filter_by(srno =srno).first()
          db.session.delete(post)
          db.session.commit()
          #try to redirect dashboad page
          posts = Posts.query.all()
          return render_template('dashboard.html', params=params, posts=posts)



#not working
@app.route("/edit/<string:srno>", methods = ['GET','POST'])
def edit(srno):
  #this is not works #  if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if srno == '0':
             post = Posts(title=box_title, slug=slug, content= content, img_file = img_file, date = date)
             db.session.add(post)
             db.session.commit()
            else:
                post = Posts.query.filter_by(srno=srno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+srno)
        post = Posts.query.filter_by(srno=srno).first()
        return render_template('edit.html', params=params, post= post)

@app.route('/home')
def home():
    name1 = "Flask Home page"
    return render_template('home.html', params=params)

@app.route('/')
def login():
    name1 = "Flask Home page"
    return render_template('login.html', params=params)

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts = posts)

    if request.method == 'POST':
        username = request.form.get('username')
        userpass = request.form.get('password')
        if(username == params['admin_user'] and userpass == params['admin_password']):
           session['user'] = userpass
           posts = Posts.query.all()

           return render_template('dashboard.html', params=params, posts = posts)

    return render_template('login.html', params=params)

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/portfolio')
def portfolio():
    name1 = "Flask portfolio page"
    return render_template('portfolio.html', params=params)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    title = "Flask contact page"
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        entry = Contacts(name = name,phone_num= phone,msg=msg, date = datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('Hiii, New  Message From ' + name, sender = email, recipients = [params['gmail-user']],
                                body = msg + "\n"  + phone )
    return render_template('contact.html', params=params)


@app.route("/comment", methods=["GET", "POST"])
def comment():
    title = "Flask comment page"
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Comments(name = name,phone= phone,message= message, date = datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('Hiii, New  Comment From ' + name, sender = email, recipients = [params['gmail-user']],
                                body = message + "\n"  + phone )
    return render_template('single.html', params=params)


app.run(debug=True)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/first_flask_web'