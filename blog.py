from sqlite3 import Cursor
from flask import Flask,render_template,flash,redirect,url_for,request,session,logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators, TextAreaField
from passlib.hash import sha256_crypt
from functools import wraps
#kullanıcı login decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):    # decoratorler neden kullanılır ?
        if "logged_in" in session:              # cevap=bu sayfada decoratori yapmamdaki amaç kullanıcı girişi olmadan web site sayfasının linkini kullanarak hirişi engellemek  
            return f(*args, **kwargs)
        else:
            flash("bu sayfayı görmek istiyorsanız siteye giriş yapmanız gerekmetedir ","danger")
            return redirect(url_for("login"))  #eğer siteye giriş yoksa url_forla giriş yap kısmına gider
    return decorated_function


#kullanıcı kayıt formu 
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[validators.Length(min=3, max=30)])  # site üzerinde kayıt formunda yazılanların karakter sayıları için class registorform sınıfı kuruldu
    username = StringField("Kullanıcı Adı", validators=[validators.Length(min=8, max=30)])
    email = StringField("E-mail", validators=[validators.Email(message="Lütfen E-mail adresinizi doğru bir şekilde yazdığınızdan emin olun")])
    password = PasswordField("Şifre", validators=[
        validators.DataRequired(message="Lütfen parolayı giriniz"),
        validators.EqualTo(fieldname="confirm", message="Parolanız uyuşmuyor..")
    ])
    confirm = PasswordField("Parolayı Doğrula")


class loginform(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("parola")
app = Flask(__name__)    # flask ile mysql arasında bağlantı kurmak için  
app.secret_key="ybblok"  # flash mesajlarını yayınlamak için app.secret_key olması gerek
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblok"
app.config["MYSQL_CURSORCLASS"] ="DictCursor"
mysql=MySQL(app)
@app.route("/")  #ben / bu adreses(rotaya) gitmek istiyorum
def index():
    #articles [
       # {"id":1, "title":"deneme1","content":"deneme1 içerik"},
       # {"id":2, "title":"deneme2","content":"deneme2 içerik"},   burası for döngüsünü çalıştırmak için yazdım
       # {"id":3, "title":"deneme3","content":"deneme3 içerik"}   ]
    #numbers=[1,2,3,4,5,6] 
    #işlem=1 gibide olabilir  burayı koşul if else yi çalıştırmak için yazdım
    return render_template("index.html") # index.html dosyasıyla blog.py dosyasını bağlayan render_templatedir
@app.route("/about")
def about():
    return render_template("about.html")
@app.route ("/contact")
def communation():
    return render_template("iletişim.html")
@app.route("/articles/<string:id>")
def detail(id):
    return "articles id"+ id   #flasktaki dinamik url fonksiyonu
@app.route ("/dashboard")
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    sorgu ="SELECT * FROM articles WHERE auther = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        articles= cursor.fetchall() # eğer makale varsa result birden büyük olur bizde cursor.fetchall() kullanarak sözlük yapısına çeviriyoruz
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")
@app.route("/article")
def article():
    cursor=mysql.connection.cursor()  #mysql ile bağlantı kurmak için 
    sorgu="Select * From articles"
    result=cursor.execute(sorgu)
    if result > 0 :
        articles= cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("article.html")
    
@app.route("/article/<string:id>")
def articles(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * From articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
       article=cursor.fetchone()
       return render_template("article.html",article=article)
    else:
        return render_template("article.html")

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
     # veri tabanına gönderme işlemleri
    if request.method=="POST" and form.validate(): #request methodunun post olma durumuna göre index sayfasına gider    form.valudete eğer formda true değer dönerse çalışır ve veri tabanına doğru yolculuk başlar
        name = form.name.data # name formda bulunan bir değer ve bu formdan datayla alınan bilgi sql den veri tabanına gelir
        username = form.username.data #aynı işlemler username email ve şifre içinde yapılır 
        email = form.email.data 
        password = sha256_crypt.encrypt(form.password.data) # bu şekilde parola veri tabanına gittikten sonra şifrelenmiş bir şekilde görülür
        cursor = mysql.connection.cursor() # mysql bağlantı kurmak için kullanılır
        sorgu = "Insert into users(name,username,email,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,username,email,password)) # cursor.execute demek bi tane sql sorgusunu çalıştırmak istediğimizi söylemiş oluyoruz        tek elemanlı bir demet vermek istenirse verilen elemanın sonuna virgül konur 
        # veri tabanında her hangi bir değişiklik yaptığımız zaman bunu commit le söylememiz gerekiyor
        mysql.connection.commit() # veri tabanında her hangi bir değişiklik yapılmak istenirse          
        cursor.close()
        flash("başarıyla kayıt oldunuz.....","success")
        return redirect(url_for("login"))  #kayıt ol butonuna bastıktan sonra buraya index yazarak index sayfasında gitmesini istedik
    else:
        return render_template("register.html",form=form) 

# login işlemi 
@app.route("/login",methods=["GET","POST"])   
def login():
    form = loginform(request.form)
    if request.method == "POST":
        username=form.username.data  # veri tabanında bulunan şifre ve username bilgilerini almak için username içinde form.username.data kullanılır veri tabanında giriş yapılmıs olur
        password_entered=form.password.data
        cursor = mysql.connection.cursor() # veri tabanında işlem yapmamızı sağlar 
        sorgu = "Select * From users where username = %s" # veri tabanında bulunan username ve parolaları sorgulayarak veri tabanınd aolup olmadığını karşılaştırıyor
        result=cursor.execute(sorgu,(username,)) #username yanına virgül bırakmaktaki amaç tek bir obje olunca sözlük olarak tanımlamaz
        if result>0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password_entered,real_password): #kayıt formunda girilen şifre ile veri tabanında bulunan şifreler arasında karşılaştırma yapılır ve bu sayede web site giriş sağlanır
                flash("başarıyla giriş yaptınız","success")
                session["logged_in"]=True 
                session["username"]=username
                return redirect(url_for("index")) # başarıyla giriş yaptıktan sonra return döngüsüyle ve redirect fonksiyonuyla url index sayfasına gelmesini istedik
            else:
                flash("parolanızı yanlış girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))
    return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
class articleForm(Form):
    title=StringField("makale başlığı",validators=[validators.length(min=5,max=100)])
    content=TextAreaField("makale içeriği",validators=[validators.length(min=10)])

#makale ekleme
@app.route("/addarticle",methods = ["GET","POST"])  
def addarticle():
    form=articleForm(request.form)
    if request.method=="POST" and form.validate():
        title  = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()
        sorgu = "INSERT INTO articles (title, auther, content) VALUES (%s, %s, %s)"
        cursor.execute(sorgu, (title, session["username"], content))
        mysql.connection.commit()
        cursor.close()
        flash("makale başarıyla eklendi","success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html",form=form)

# makale sil
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()    
    sorgu = "SELECT * FROM articles WHERE auther= %s AND id= %s"
    result = cursor.execute(sorgu,(session["username"],id))
    if result > 0:
        sorgu2 = "DELETE FROM articles WHERE id = %s"
        cursor.execute(sorgu2, (id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya bu işlemi gerçekleştirme yetkiniz yok.", "danger" )
        return redirect(url_for("index"))

# makale güncelleme 
@app.route("/edit/<string:id>",methods=["GET","POST"]) 
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu  = "Select * from articles where  auther= %s and id =%s "
        result=cursor.execute(sorgu,(session["username"],id))
        mysql.connection.commit()
        if result==0 :
            flash("böyle bir makale yok veya bu işleme yetkiniz yok ","danger")
            return redirect(url_for("index"))
        else:
            article=cursor.fetchone()
            form =articleForm()
            form.title.data=article["title"]
            form.content.data=article["content"]
            return render_template("update.html",form=form)
    else: 
        # post request
        form=  articleForm(request.form)
        newtitle=form.title.data
        newcontnet=form.content.data
        sorgu2="Update articles set title = %s ,content= %s where id=%s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newtitle,newcontnet,id))
        mysql.connection.commit()
        flash("makale başarıyla güncellendi","success" )
        return redirect(url_for("dashboard"))
if __name__ == "__main__":
    app.run(debug=True)  
