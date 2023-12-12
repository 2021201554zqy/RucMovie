from flask import Flask, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as query_text
from sqlalchemy.sql import func
from helpers.echarts import hbar_option
import pandas as pd
import numpy as np
import os
import json
import plotly.express as px


# Create a Blueprint instance
blueprint_box = Blueprint('box', __name__)

# Define routes using the Blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'movie.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.app_context().push()
db = SQLAlchemy(app)

# movies = pd.read_sql('movie_info', db.engine)
# persons = pd.read_sql('actor_info', db.engine)
# associations = pd.read_sql('movie_actor_association', db.engine)

# movies['release_year'] = movies.release_year.fillna(0).astype(np.int64)

# movie_actor = {}

# for movie_id in associations.movie_id.unique():
#     movie_actor[movie_id] = associations.loc[associations.movie_id==movie_id, 'actor_id'].values.tolist()[:3]
# movie_actor = pd.DataFrame.from_dict(movie_actor, orient='index').stack().droplevel(-1).reset_index()
# movie_actor.columns = ['movie_id', 'actor_id']

# movie_name = movies.set_index('movie_id')['movie_name'].to_dict()
# movie_rate = movies.set_index('movie_id')['douban_rate'].to_dict()
# rate_count = movies.set_index('movie_id')['rating_count'].to_dict()
# person_group = movie_actor.groupby('actor_id')['movie_id']
# actors = pd.concat([
#     person_group.apply(lambda x: [mid for mid in x]),
#     person_group.apply(lambda x: [movie_name[mid] for mid in x]),
#     person_group.apply(lambda x: [movie_rate[mid] for mid in x]),
#     person_group.apply(lambda x: [rate_count[mid] for mid in x]),
#     person_group.apply(lambda x: '; '.join([f"{movie_name[mid]}（{movie_rate[mid]})" for mid in x])),
# ], keys =['movie_id', 'movie_name', 'movie_rate', 'rate_count', 'movies'], 
# axis=1).join(persons.set_index('actor_id'))
# actors['max_rate'] = actors.movie_rate.apply(max)
# actors['top_count'] = actors.movie_rate.apply(len)
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
    
    def __repr__(self):
        return f'<Actor {self.actor_name}>'    
    
# one to one relation
class MovieBox(db.Model):
    __tablename__ = 'movie_box'
    box_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'))
    movie_box = db.Column(db.Float)
    movies = db.relationship('Movie', back_populates='moviebox')

movies = Movie.query.all()

@blueprint_box.route('/')
@blueprint_box.route('/index')
@blueprint_box.route('/movies')
def movie_table():
    data = [[movie.movie_id, movie.movie_name, movie.country, movie.release_year,
     movie.movie_type, movie.moviebox.movie_box] 
    for movie in movies]
    vars = dict(data = data, ensure_ascii=True)
    return render_template('box/movie_list.html', vars=vars)

@blueprint_box.route('/movie_top10')
def movie_top10():
    vars = {}
    data = movies.loc[
        movies.country.str.contains('大陆'), ['movie_name', 'douban_rate']
    ].sort_values('douban_rate', ascending=False)[:10].set_index('movie_name')
    vars['echart_mainland'] = hbar_option("大陆电影高分榜", data.index.tolist(), data['douban_rate'].tolist())
    data = movies.loc[
        movies.country.str.contains('香港|台湾'), ['movie_name', 'douban_rate']
    ].sort_values('douban_rate', ascending=False)[:10].set_index('movie_name')
    vars['echart_hk'] = hbar_option("港台电影高分榜", data.index.tolist(), data['douban_rate'].tolist())

    data = movies.loc[
        ~movies.country.str.contains('大陆|香港|台湾'), ['movie_name', 'douban_rate']
    ].sort_values('douban_rate', ascending=False)[:10].set_index('movie_name')
    vars['echart_oversea'] = hbar_option("国外电影高分榜", data.index.tolist(), data['douban_rate'].tolist())

    return render_template('douban/movie_top10.html', vars=vars)

@blueprint_box.route('/actors')
def actor_table():
    cols = ['person_name', 'gender', 'birth_date', 'birth_place',  'max_rate', 'top_count', 'movies']
    vars = dict(data = actors[cols].values.tolist(), ensure_ascii=True)
    return render_template('douban/actor_list.html', vars=vars)

@blueprint_box.route('/actormap')
def actor_map():
    with open('helpers/china.json', encoding='utf8') as f:
        json_data = json.load(f)['features']
    provinces = pd.DataFrame.from_dict(
        data={p['properties']['name']:p['properties']['center'] for p in json_data if p['properties']['name']!=''},
        orient='index', columns=['lon', 'lat']
    )
    provinces.index = provinces.index.str.replace('市|省|自治区|壮族|回族|维吾尔', '', regex=True)
    provinces =  provinces.join(actors.loc[actors.birth_place.str.contains('中国'), 'birth_place'].str.split(',', expand=True)[1].value_counts())
    provinces = provinces.loc[provinces['count'].notna()]

    provinces['text'] = provinces.apply(lambda x: f"{x.name}: {x['count']:0.0f}", axis=1)

    px.set_mapbox_access_token('pk.eyJ1Ijoia2FyaWJ1bnlhaHVhIiwiYSI6ImNsYW0xcGp4dDBhdW8zcG1pcHcxdDR1OGsifQ.I3r8tCO7g08pzM1kFYUwfg')
    provinces = provinces.reset_index()
    df = px.data.carshare()
    fig = px.scatter_mapbox(provinces, lat="lat", lon="lon", size="count", hover_name='index', size_max=30, zoom=4)
    fig.update_layout(margin = dict(l = 0, r = 0, t = 0, b = 0), height=800)
    div_map = fig.to_html(full_html=False)
    return render_template('douban/actor_map.html', div_map=div_map)





