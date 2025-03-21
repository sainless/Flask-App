from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import traceback

app = Flask(__name__)

# Основная база данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
# Дополнительные базы данных
app.config['SQLALCHEMY_BINDS'] = {
    'blog': 'sqlite:///blog.db',
    'users': 'sqlite:///users.db'
}






db = SQLAlchemy(app)

class Article(db.Model):
    __bind_key__ = 'blog'  # Привязка к базе данных blog.db
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Article % r>' % self.id


class Users(db.Model):
    __bind_key__ = 'users'  # Привязка к базе данных users.db
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(13), nullable=False)
    
    def __repr__(self):
        return "<User % r>" % self.id

# Создание всех таблиц
with app.app_context():
    # Создаем таблицы для основной базы данных (если есть модели без __bind_key__)
    db.create_all()

    # Создаем таблицы для базы данных blog
    db.create_all(bind_key='blog')

    # Создаем таблицы для базы данных users
    db.create_all(bind_key='users')

@app.route("/")
@app.route("/new")
def hello_world():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        
        article = Article(title=title, intro=intro, text=text)
        
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template('create-article.html')

@app.route("/posts")
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)

@app.route("/posts/<int:id>")
def posts_show_if(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route("/posts/<int:id>/delete")
def delete_post(id):
    article = Article.query.get_or_404(id)
    
    try:
        
        db.session.delete(article)
        db.session.commit()
        return redirect("/posts")
        
    except:
        return "При удалении  статьи произошла ошибка"

@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def update_post(id):
    article = Article.query.get(id)

    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']
                
        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "При редактировании статьи произошла ошибка"
    else:
        article = Article.query.get(id)

        return render_template('post_update.html', article=article)


@app.route("/users")
def users():
    users = Users.query.all()
    
    return render_template("users.html", users=users)
    

@app.route("/user/<int:id>")
def user(id):    
    user = Users.query.get(id)

    return render_template("user.html", user=user)





@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        print(f"E-mail: {email}\nPassword: {password}")
        
        # Проверяем, существует ли пользователь с таким email
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            return "Пользователь с таким email уже существует!"
        
        user = Users(email=email, password=password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/posts')
        except Exception as e:
            # Логируем ошибку
            print(f"Ошибка: {e}")
            traceback.print_exc()  # Печатаем traceback
            return "Произошла ошибка с БАЗОЙ ДАННЫХ!"
    
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)