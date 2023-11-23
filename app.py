from flask import Flask, render_template
from markupsafe import escape

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import func
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy # 导入扩展类
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required, logout_user
from flask_login import login_required, current_user

import os
import sys
import click
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'movie.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'
# app.app_context().push()

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id)) # 用 ID 作为 User 模型的主键查询对应的用户
    return user # 返回用户对象  
# many to many relation
movie_actor_association = db.Table(
    'movie_actor_association',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie_info.movie_id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor_info.actor_id')),
)

movie_director_association = db.Table(
    'movie_director_association',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie_info.movie_id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor_info.actor_id')),
)

class Movie(db.Model):
    __tablename__ = 'movie_info'

    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_name = db.Column(db.String(20))
    release_date = db.Column(db.String(15))
    country = db.Column(db.String(20))
    movie_type = db.Column(db.String(10))
    release_year = db.Column(db.Integer)
    
    moviebox = db.relationship('MovieBox', back_populates='movies', uselist=False, cascade='all, delete-orphan')
    actors = db.relationship('Actor', secondary=movie_actor_association, back_populates='movie_actors')
    directors = db.relationship('Actor', secondary=movie_director_association, back_populates='movie_directs')
    
    def __init__(self, movie_name, release_date, country, movie_type, release_year):
        self.movie_name = movie_name
        self.release_date = release_date
        self.country = country
        self.movie_type = movie_type
        self.release_year = release_year

    def __repr__(self):
        return f'<Movie {self.movie_name}>' 

class Actor(db.Model):
    __tablename__ = 'actor_info'

    actor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_name = db.Column(db.String(20))
    gender = db.Column(db.String(2))
    country = db.Column(db.String(20))
    
    movie_actors = db.relationship('Movie', secondary=movie_actor_association)
    movie_directs = db.relationship('Movie', secondary=movie_director_association)
    def __init__(self, actor_name, gender, country):
        self.actor_name = actor_name
        self.gender = gender
        self.country = country   
    def __repr__(self):
        return f'<Actor {self.actor_name}>'    
    
# one to one relation
class MovieBox(db.Model):
    __tablename__ = 'movie_box'
    box_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'))
    movie_box = db.Column(db.Float)
    movies = db.relationship('Movie', back_populates='moviebox')

# # many to many relation
# movie_actor_association = db.Table(
#     'movie_actor_association',
#     db.Column('movie_id', db.Integer, db.ForeignKey('movie_info.movie_id')),
#     db.Column('actor_id', db.Integer, db.ForeignKey('actor_info.actor_id')),
# )
# # class User(db.Model, UserMixin):
class User(db.Model,UserMixin):
    # __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值

    def set_password(self, password): # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password) #将生成的密码保持到对应字段

    def validate_password(self, password): # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)



# 在执行数据库查询之前手动推送应用上下文
with app.app_context():
    movies = Movie.query.all()
    actors = Actor.query.all()

@app.cli.command()
@click.option('--username', prompt=True, help='The username usedto login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()
    
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password) # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password) # 设置密码
        db.session.add(user)
    db.session.commit() # 提交数据库会话
    click.echo('Done.')



@app.route('/')
@app.route('/index')
@app.route('/movie')
def index():
    if request.method == 'POST': # 判断是否是 POST 请求
        if not current_user.is_authenticated: # 如果当前用户未认证
            return redirect(url_for('index')) # 重定向到主页
        # 获取表单数据
        title = request.form.get('title') # 传入表单对应输入字段的name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title)> 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库会话
        db.session.commit() # 提交数据库会话
        flash('Item created.') # 显示成功创建的提示
    user = User.query.first() # 读取用户记录
    movies = Movie.query.all()
    return render_template('index.html', movies=movies,user=user)

@app.route('/actor')
def actor():
    user = User.query.first() # 读取用户记录
    actors = Actor.query.all()   
    return render_template('actor.html', actors=actors,user=user)
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user=None
    if request.method == 'POST':
        name = request.form['name']
    
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
    
        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html',user=user)


@app.route('/user/<name>')
def user_page(name):
    return dict(User=escape(name))

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    # movie = Movie.query.filter_by(movie_id=movie_id)
    movie = Movie.query.get_or_404(movie_id)
   
    
    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面
          # 解除与 MovieBox 的关联关系
        if movie.moviebox:
            movie.movie_name = title  # 更新标题
            movie.release_year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页
    user = User.query.first() # 读取用户记录
    return render_template('edit.html', movie=movie,user=user)  # 传入被编辑的电影记录




@app.route('/movie/details/<int:movie_id>', methods=['GET', 'POST'])
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    # if request.method == 'POST':  # 处理编辑表单的提交请求
    #     title = request.form['title']
    #     year = request.form['year']

    #     if not title or not year or len(year) != 4 or len(title) > 60:
    #         flash('Invalid input.')
    #         return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面
    #       # 解除与 MovieBox 的关联关系
    #     if movie.moviebox:
    #         movie.movie_name = title  # 更新标题
    #         movie.release_year = year  # 更新年份
    #     db.session.commit()  # 提交数据库会话
    #     flash('Item updated.')
    #     return redirect(url_for('index'))  # 重定向回主页
    # user = User.query.first() # 读取用户记录
    # return render_template('edit.html', movie=movie,user=user)  # 传入被编辑的电影记录

    # 根据电影 ID 从数据库中获取演员信息
    # actors = get_actors_by_movie_id(movie_id)
    directors = movie.directors
    actors = movie.actors
    user = User.query.first() # 读取用户记录
    return render_template('movie_details.html', directors = directors, movie=movie, actors=actors,user=user)

@app.route('/actor/details/<int:actor_id>', methods=['GET', 'POST'])
def actor_details(actor_id):
    actor = Actor.query.get_or_404(actor_id)
    # 找到给定演员主演的电影
    movies_actor = db.session.query(Movie).join(movie_actor_association).filter(movie_actor_association.c.actor_id == actor_id).all()
    # 找到给定演员导演过的电影
    movies_director = db.session.query(Movie).join(movie_director_association).filter(movie_director_association.c.actor_id == actor_id).all()
    user = User.query.first() # 读取用户记录
    return render_template('actor_details.html',  movies_director = movies_director, movies_actor=movies_actor, actor=actor,user=user)

@app.route('/actor/edit/<int:actor_id>', methods=['GET', 'POST'])
@login_required
def edit_actor(actor_id):
    actor = Actor.query.get_or_404(actor_id)
    
    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        gender = request.form['gender']
        country = request.form['country']
        if not title or not gender or not country:
            flash('Invalid input.')
            return redirect(url_for('edit_actor', actor_id=actor_id))  # 重定向回对应的编辑页面
          # 解除与 MovieBox 的关联关系
        # if movie.moviebox:
        #     movie.movie_name = title  # 更新标题
        #     movie.release_year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页
    user = User.query.first() # 读取用户记录
    return render_template('edit_actor.html', actor=actor,user=user)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    # Step 1: Retrieve the movie by its ID
    movie = Movie.query.get_or_404(movie_id)

    if movie:
        if len(movie.actors)>0:
            for actor in movie.actors:
                db.session.delete(actor)
        if len(movie.directors)>0:
            for director in movie.directors:
                db.session.delete(director)
        if movie.moviebox:
            db.session.delete(movie.moviebox)
        db.session.delete(movie)
    db.session.commit()
    print(f"Movie with ID {movie_id} has been deleted.")
        # except:
        #     db.session.rollback()
        #     print(f"Movie with ID {movie_id} not found.")
    flash('Item deleted.')
    # 在执行数据库查询之前手动推送应用上下文
    with app.app_context():
        movies = Movie.query.all()
        actors = Actor.query.all()
    return redirect(url_for('index'))


@app.route('/actor/delete/<int:actor_id>', methods=['POST'])
@login_required
def delete_actor(actor_id):
    # Step 1: Retrieve the movie by its ID
    actor = Actor.query.get_or_404(actor_id)

    if actor:
        db.session.delete(actor)
    db.session.commit()
    # print(f"Movie with ID {movie_id} has been deleted.")
        # except:
        #     db.session.rollback()
        #     print(f"Movie with ID {movie_id} not found.")
    flash('Item deleted.')
    # # 在执行数据库查询之前手动推送应用上下文
    with app.app_context():
        movies = Movie.query.all()
        actors = Actor.query.all()
    return redirect(url_for('actor'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = None  # 初始化 user 变量
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) # 登入用户
            flash('Login success.')
            return redirect(url_for('index')) # 重定向到主页    
        flash('Invalid username or password.') # 如果验证失败，显示错误消息
        return redirect(url_for('login')) # 重定向回登录页面
    return render_template('login.html',user=user)


@app.route('/logout')
@login_required # 用于视图保护，后面会详细介绍
def logout():
    logout_user() # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index')) # 重定向回首页                                                                  


@app.route('/add_movie', methods=['POST'])
def add_movie():
    title = request.form['title']
    year = request.form['year']

    # # 在这里可以执行其他操作，例如将数据存储到数据库中
    # # 为了演示，我们只将数据添加到 movies 列表中
    # movies.append({'movie_name': title, 'release_year': year})

    # 

    # new_movie = Movie(
    #     movie_name=title,
    #     release_date=movie_data['release_date'],
    #     country=movie_data['country'],
    #     movie_type=movie_data['movie_type'],
    #     release_year=movie_data['release_year']
    # )
    new_movie = Movie(title, '', '', '', year)   
    # Step 2: Add any associated records or relationships
    # # Add actors to the movie
    # actors_data = movie_data.get('actors', [])
    # for actor_data in actors_data:
    #     actor = Actor(**actor_data)
    #     new_movie.actors.append(actor)

    # # Add directors to the movie
    # directors_data = movie_data.get('directors', [])
    # for director_data in directors_data:
    #     director = Actor(**director_data)
    #     new_movie.directors.append(director)

    # # Add movie box details
    # movie_box_data = movie_data.get('movie_box', {})
    # if movie_box_data:
    #     movie_box = MovieBox(**movie_box_data)
    #     new_movie.moviebox = movie_box

    # Step 3: Add the movie to the database
    db.session.add(new_movie)
    db.session.commit()

    # print(f"Movie '{new_movie.movie_name}' has been added with ID {new_movie.movie_id}.")
    return redirect(url_for('index'))  # 重定向到主页


@app.route('/add_actor', methods=['POST'])
def add_actor():
    title = request.form['title']
    gender = request.form['gender']
    country= request.form['country']

    new_actor = Actor(title, gender,country)   
    db.session.add(new_actor)
    db.session.commit()

    # print(f"Movie '{new_movie.movie_name}' has been added with ID {new_movie.movie_id}.")
    return redirect(url_for('actor'))  # 重定向到主页

@app.route('/search_movie', methods=['GET'])
def search_movie():
    keyword = request.args.get('keyword', '')

    # 使用 ilike 进行模糊查询
    movies_searched = Movie.query.filter(Movie.movie_name.ilike(f'%{keyword}%')).all()
    user = User.query.first() # 读取用户记录
    return render_template('search_movie.html', keyword=keyword,movies_searched=movies_searched,user = user)

@app.route('/search_actor', methods=['GET'])
def search_actor():
    keyword = request.args.get('keyword', '')

    # 使用 ilike 进行模糊查询
    actors_searched = Actor.query.filter(Actor.actor_name.ilike(f'%{keyword}%')).all()
    print(actors_searched)
    user = User.query.first() # 读取用户记录
    return render_template('search_actor.html', keyword=keyword,actors_searched=actors_searched,user = user)