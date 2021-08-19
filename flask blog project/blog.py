from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

class RegisterForm(Form):
    name= StringField(label="Name Surname", validators=[validators.length(min=3,max=15)])
    username= StringField(label="Username",validators=[validators.length(min=5,max=22)])
    email= StringField(label="Email Adress",validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz")])
    password= PasswordField(label="Password",validators=[validators.DataRequired(message="Lütfen bir parola giriniz"),validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor")])
    confirm= PasswordField(label="Password Confirm")


class LoginForm(Form):
    username= StringField(label="Username")
    password= PasswordField(label="Password")


class ArticleForm(Form):
    title=StringField(label="Title",validators=[validators.length(min=3,max=100)])
    content= TextAreaField(label="Article Content")


app = Flask(__name__)
app.secret_key="aliko"

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="blog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("UNAUTHORIZED","danger")
            return redirect(url_for("login"))
    return decorated_function
    

@app.route("/")
def index():
   
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    
    if request.method == "POST" and form.validate():
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password= sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        
        sorgu = "Insert into users(name,username,email,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,username,email,password))

        mysql.connection.commit()
        
        cursor.close()

        flash("SUCCESFULL LOGIN","success")

        return redirect(url_for("login"))
    elif request.method == "POST" :
        flash("Form not valid","danger")
        return render_template("register.html", form = form)
    else:
        return render_template("register.html", form = form)
 
@app.route("/login", methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method == "POST":

        username= form.username.data
        password= form.password.data

        cursor= mysql.connection.cursor()
        sorgu= "Select * from users where username= %s"
        result = cursor.execute(sorgu,(username,))
        if result>0 :
            data = cursor.fetchone()
            realpassword=data["password"]
            if sha256_crypt.verify(password,realpassword):
                flash("Successful Login","success")
                session["logged_in"]=True
                session["username"]= username
                return redirect(url_for("index"))
            else:
                flash("Wrong Password", "danger")
                return redirect(url_for("login"))
     
        else:
            flash("Username doesn't exist", "danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html",form=form)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
@app.route("/dashboard")
@login_required
def dashboard():
    cursor= mysql.connection.cursor()
    sorgu= "Select * from articles where author= %s"
    result= cursor.execute(sorgu,(session["username"],))
    if result>0:
        articles= cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")


@app.route("/addarticle",methods=["GET","POST"])
def addarticle():
    form=ArticleForm(request.form)
    if request.method=="POST":
        title=form.title.data
        content=form.content.data
        author= session["username"]
        cursor=mysql.connection.cursor()
        sorgu="Insert into articles(title,author,content) Values(%s,%s,%s)"
        cursor.execute(sorgu,(title,author,content))
        mysql.connection.commit()
        cursor.close()
        flash("Article Added","Succes")
        return redirect(url_for("dashboard"))

    
    else:
        return render_template("addarticle.html",form=form)

@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu= "Select * from articles"
    result= cursor.execute(sorgu)
    if result>0:
        articles= cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")

@app.route("/article/<string:id>")
def article(id):
    cursor= mysql.connection.cursor()
    sorgu="Select * from articles where id= %s"
    result= cursor.execute(sorgu,(id,))
    if result>0:
        article=cursor.fetchone()
        return render_template("article.html", article=article)
    else:
        return render_template("article.html")


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where id= %s"
    result= cursor.execute(sorgu,(id,))
    if result>0:
        article = cursor.fetchone()
        if article["author"]==session["username"]:
            sorgu="Delete from articles where id= %s"
            cursor.execute(sorgu,(article["id"],))
            mysql.connection.commit()
            cursor.close()
            flash("ARTICLE DELETED","success")
            return redirect(url_for("dashboard"))
        else :
            flash("UNAUTHORIZED","danger")
            return redirect(url_for("dashboard"))
    else:
        flash("There is no article has that id.","danger")
        return redirect(url_for("dashboard"))

@app.route("/edit/<string:id>", methods=["GET","POST"])
@login_required
def update(id):
    if request.method=="GET":
        cursor= mysql.connection.cursor()
        sorgu="Select * from articles where id= %s and author= %s"
        result= cursor.execute(sorgu,(id,session["username"]))
        if result>0 :
            article= cursor.fetchone()
            form=ArticleForm()
            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html",form=form)
        else :
            flash("UNAUTHORIZED or there is no article has that id.","danger")
            return redirect(url_for("dashboard"))
    else:
        form= ArticleForm(request.form)
        newtitle=form.title.data
        newcontent=form.content.data
        cursor= mysql.connection.cursor()
        sorgu="Update articles Set title= %s, content= %s where id= %s"
        cursor.execute(sorgu,(newtitle,newcontent,id))
        mysql.connection.commit()
        cursor.close()
        flash("ARTICLE UPDATED","success")
        return redirect(url_for("dashboard"))

@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("articles"))
    else:
        keyword = request.form.get("keyword")
        cursor= mysql.connection.cursor()
        sorgu="Select * from articles where title like '%" + keyword + "%'"
        result= cursor.execute(sorgu)
        if result>0:
            articles = cursor.fetchall()
            return render_template("articles.html",articles=articles)
        else :
            flash("There is no article like that","warning")
            return redirect(url_for("dashboard"))







if __name__ == "__main__":
    app.run(debug=True)
    