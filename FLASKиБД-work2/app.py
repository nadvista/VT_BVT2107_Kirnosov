import settings

import requests
import sys

from flask import Flask, render_template, request, make_response

import psycopg2
from werkzeug.utils import redirect

app = Flask(__name__)
conn = psycopg2.connect(database=settings.database, user=settings.user, password=settings.password, host=settings.host, port=settings.port)
cursor = conn.cursor()

@app.route('/', methods=['GET'])
def indexGET():
    return redirect('/login/')

@app.route('/login/', methods=['GET'])
def loginGET():
    login = request.cookies.get('login')
    password = request.cookies.get('password')
    answer = try_login(login,password)
    if (answer != 'ERROR'):
        return answer
    return render_template('login.html')

@app.route('/login/', methods=['POST'])
def loginPOST():
    if(request.form['submit'] == 'Login'):
        login = request.form.get('login')
        password = request.form.get('password')
        answer = try_login(login,password)
        return answer
    elif(request.form['submit'] == 'Register'):
        return redirect('/register/')

@app.route('/register/', methods=['GET'])
def registerGET():
    return render_template('register.html')

@app.route('/register/', methods=['POST'])
def registerPOST():
     login = request.form.get('login')
     username = request.form.get('username')
     password = request.form.get('password')
     confirmPassword = request.form.get('confirmPassword')


     if (password != confirmPassword or not verify_login(login) or not password.strip()):
         return "REGERROR"
     else:
         cursor.execute("INSERT INTO service.users (full_name, login, password) VALUES (%s,%s, %s);", (str(username),str(login),str(password)))
         conn.commit()
         resp = make_response(redirect('/login/'))
         resp.set_cookie('login',login)
         resp.set_cookie('password',password)
         return resp

@app.route('/account/', methods=['GET'])
def accountGET(name,login):
    return render_template('account.html', username = name,login=login)


def verify_login(login):
    if(not(login and login.strip())):
        return False
    cursor.execute("SELECT * FROM service.users WHERE login='"+(str(login))+"'")
    records = (cursor.fetchall())
    return (len(records) == 0)
def try_login(login,password):
    cursor.execute("SELECT * FROM service.users WHERE login=%s AND password=%s", (str(login), str(password)))
    records = list(cursor.fetchall())
    if (len(records) > 0):
        username = records[0][1]
        login = records[0][2]
        return accountGET(username,login)
    else:
        return 'ERROR'