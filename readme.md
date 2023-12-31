
# Watchlist Homework
## working enviroment
- windows 11
- terminal: powershell
- anaconda environment
- flask

## 初始化数据库
- 先利用SQL语言建立数据库，再将其转为SQLlite方式
- 建立本地的数据库 `movie.db`.将程序直接连接该数据库

## 网页建立
-参考flask-tutorial教材搭建网页、实现与本地数据库的连接、建立表单并实现了用户的登录、登出，在不同页面间的跳转
-在此基础上，又建立了actor页面记录演员信息
-在使用书中给定的数据库的基础上通过了全部测试

## 网页展示

### 未登录状态
未登录看到的状态
![未登录看到的状态](./screenshots/logout.png)

### 登录界面
登录状态
![登录状态](./screenshots/login.png)

### 登录后状态
登录进去看到的状态
![登录进去看到的状态](./screenshots/login_state.png)

### 演员界面
展示演员信息
![展示演员信息](./screenshots/actor_state.png)

### 编辑界面
点编辑按钮之后
![点编辑按钮之后](./screenshots/edit1.png)
编辑后的效果
![编辑后的效果](./screenshots/edit2.png)

### 删除操作
点删除按钮之后
![点删除按钮之后](./screenshots/delete.png)
哪吒已删的效果
![哪吒已删的效果](./screenshots/delete2.png)

### 新增内容功能
输入电影信息点添加钮之后
![输入电影信息点添加钮之后](./screenshots/add1.png)
点新建按钮之后
![点新建按钮之后](./screenshots/add2.png)

同理，也可以新增演员
![输入演员信息点添加钮之后](./screenshots/add_actor1.png)
点新建按钮之后之后
![点新建按钮之后之后](./screenshots/add_actor2.png)
### 电影详情界面
在movie界面下点Details按钮（单表查询）
![在movie界面下点Details按钮（单表查询）](./screenshots/movie_details.png)

### 演员详情界面
在actor界面下点Details按钮（单表查询）
![在actor界面下点Details按钮（单表查询）](./screenshots/actor_details.png)

### 搜索功能
#### 常规搜索
在搜索栏中输入电影名的一部分，点击搜索，就会返回包含这部分的电影（演员同理）
输入电影名（的一部分）
![输入电影名（的一部分)](./screenshots/search1.png)
点击搜索后（出现包含输入字符的部分）
![点击搜索后（出现包含输入字符的部分）](./screenshots/search2.png)
同理，也可以搜索演员
输入演员名（的一部分）
![输入演员名（的一部分）](./screenshots/search_actor1.png)
#### 条件搜索
除了通过名字搜索电影之外，还可以通过条件查询的方式搜索电影。比如，我们可以查询类型为战争或喜剧或剧情，中国拍的，上映年份为2018年的电影，结果如下。
选择要查询的类型、上映的国家、和上映年份（不选默认从所有的里面查询）
![条件搜索1](./screenshots/condition_search1.png)
查询到的结果
![条件搜索2](./screenshots/condition_search2.png)

### 票房分析
#### 进入票房分析界面，可以看出每个电影的相关信息，也可以按照票房对电影进行排名
![条件搜索1](./screenshots/box_analysis.png)
#### 还可以对所用电影、按照类型、年份划分的电影票房的可视化
![条件搜索1](./screenshots/box_visualization.png)
#### 还有演员的票房分析
![条件搜索1](./screenshots/actor_analysis.png)
#### 还可以对所用电影、按照类型、年份划分的电影票房的可视化
![条件搜索1](./screenshots/actor_visualization.png)

### 票房预测
#### 进入票房预测界面，可以看出每个电影的预测票房与实际票房，并看出两者之间的差异百分比
![条件搜索1](./screenshots/box_prediction.png)

### 设置状态
![改变用户名等](./screenshots/settings.png)



## Installation:
- download [python windows](https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe) then install. `Add Python to environment variables`, open powershell and input `python --version` to check.
- enviroment setup:
```bash
# open pwoershell as admin
Set-ExecutionPolicy RemoteSigned
mkdir watchlist
cd watchlist
python -m venv env
env\Scripts\activate
pip install flask flask_sqlalchemy
# output: (env) PS D:\code\flask-mysql\watchlist>
```

# notes
## push my change to [github](https://github.com/2021201554zqy/RucMovie)
```bash
git add .
git commit -m "my message"
git push
```