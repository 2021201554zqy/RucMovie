# notes
## push my change to [github](https://github.com/2021201554zqy/RucMovie)
```bash
git add .
git commit -m "my message"
git push
```
# Watchlist Homework
## working enviroment
- windows 11
- terminal: powershell
- 

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

## initial Database setup
- use ChatGpt help to convert MySQL sql into SQLite.
- database created in local file `movie.db`. Copy it to chapter 05 ever since.

## Charpter 03
>  Tip: There are .env or .flaskenv files present. Do "`pip install python-dotenv`" to use them.

## screeshots
### login
![login](screeshots/login_state.png)

<img src="screeshots/login_state.png"></img>