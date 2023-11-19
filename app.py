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


# db = SQLAlchemy(app) # 初始化扩展，传入程序实例 app


# many to many relation
movie_actor_association = db.Table(
    'movie_actor_association',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie_info.movie_id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor_info.actor_id')),
)
# class User(db.Model, UserMixin):
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

class Movie(db.Model):
    __tablename__ = 'movie_info'

    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_name = db.Column(db.String(20))
    release_date = db.Column(db.String(15))
    country = db.Column(db.String(20))
    movie_type = db.Column(db.String(10))
    release_year = db.Column(db.Integer)
    
    moviebox = db.relationship('MovieBox', back_populates='movies', uselist=False)
    actors = db.relationship('Actor', secondary=movie_actor_association, back_populates='movies')
    
    def __repr__(self):
        return f'<Movie {self.movie_name}>'
    
class Actor(db.Model):
    __tablename__ = 'actor_info'

    actor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_name = db.Column(db.String(20))
    gender = db.Column(db.String(2))
    country = db.Column(db.String(20))
    
    movies = db.relationship('Movie', secondary=movie_actor_association, back_populates='actors')
    
    def __repr__(self):
        return f'<Actor {self.actor_name}>'    
    
# one to one relation
class MovieBox(db.Model):
    __tablename__ = 'movie_box'
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'), unique=True, nullable=False, primary_key=True)
    movie_box = db.Column(db.Float)
    movies = db.relationship('Movie', back_populates='moviebox')

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
    return render_template('index.html', movies=movies,user=user)

@app.route('/actor')
def actor():

    user = User.query.first() # 读取用户记录
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

        movie.movie_name = title  # 更新标题
        movie.release_year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页
    user = User.query.first() # 读取用户记录
    return render_template('edit.html', movie=movie,user=user)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST']) #
@login_required # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie) # 删除对应的记录
    db.session.commit() # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页


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