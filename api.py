import flask
from flask import request
from flask import send_file
import sqlite3
import hashlib
import service
import random
import datetime
import os

CONST_TIME_LIVE = 40
app = flask.Flask(__name__)
app.config["DEBUG"] = False


@app.route('/api/userauth/', methods=['GET'])
def authorization_user():
    if 'login' in request.args and 'password' in request.args:
        login = request.args['login']
        password = request.args['password']
        code = request.args['code']
        connection = sqlite3.connect('db.sqlite3')
        pwd = hashlib.md5(password.encode('utf-8')).hexdigest()
        query = 'SELECT EXISTS(SELECT id FROM user WHERE tg_name=\'{0}\' AND password=\'{1}\')'.format(login, pwd)
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchone()[0]
        if data == 1:
            query = 'SELECT EXISTS(SELECT username FROM temp_tg WHERE username=\'{0}\'' \
                    ' AND code=\'{1}\' order by date_send DESC)'.format(login, code)
            cursor.execute(query)
            data_exist = cursor.fetchone()[0]
            if data_exist == 1:
                query = 'DELETE FROM temp_tg WHERE username=\'{0}\' AND code=\'{1}\''.format(login, code)
                cursor.execute(query)
                connection.commit()
                count = 0
                password_string = ''
                while count < 31:
                    password_string += service.DICTIONARY_STRING[random.randint(0, len(service.DICTIONARY_STRING) - 1)]
                    count += 1
                temp_pwd = hashlib.md5(password_string.encode('utf-8')).hexdigest()
                query = 'SELECT id FROM user WHERE tg_name=\'{0}\' AND password=\'{1}\''.format(login, pwd)
                cursor.execute(query)
                id_user = cursor.fetchone()[0]
                query = 'INSERT INTO temp_password(password,date_password,id_user)' \
                        ' VALUES(\'{0}\', \'{1}\', \'{2}\')'.format(temp_pwd, datetime.datetime.now(), str(id_user))
                cursor.execute(query)
                connection.commit()
                cursor.close()
                connection.close()
                return {'status': data, 'temp_password': temp_pwd, 'id_user': str(id_user)}
            else:
                return {'error': data}
        return {'status': data}
    else:
        return {'error': 'BAD REQUEST: not find login or password value'}


@app.route('/api/addcategoryuser/', methods=['GET'])
def add_category_user():
    if 'name' in request.args:
        name = request.args['name']
        connection = sqlite3.connect('db.sqlite3')
        query = 'INSERT INTO category_user(name) VALUES(\'{0}\')'.format(name)
        try:
            connection.execute(query)
            connection.commit()
            connection.close()
        except Exception as e:
            connection.close()
            return {'error': 'this category exists in database'}
        return {'status': 'success'}

    else:
        return {'error': 'BAD REQUEST: not find category name'}


@app.route('/api/adduser/', methods=['GET'])
def add_user():
    if 'login' in request.args and 'password' in request.args:
        login = request.args['login']
        password = request.args['password']
        pwd = hashlib.md5(password.encode('utf-8')).hexdigest()
        connection = sqlite3.connect('db.sqlite3')
        query = 'INSERT INTO user(login, password) VALUES(\'{0}\', \'{1}\')'.format(login, pwd)
        try:
            connection.execute(query)
            connection.commit()
            connection.close()
            return {'status': 'success'}
        except Exception as e:
            return {'error': 'FAILED ADDING USER: user with this params exists'}
    else:
        return {'error': 'BAD REQUEST: not find login or password value'}



@app.route('/api/getallfilesinfo/', methods=['GET'])
def get_all_info():
    path_f = []
    for d, dirs, files in os.walk('files'):
        for f in files:
            path = os.path.join(d, f)  # формирование адреса
            path_f.append(path)
    return {'list_file': path_f}


@app.route('/api/filesize/', methods=['GET'])
def filesize():
    filename = request.args['filename']
    file_size = os.path.getsize(filename)
    return {'size': str(file_size / 1024)}


@app.route('/api/filetype/', methods=['GET'])
def get_files_with_type():
    type = request.args['type']
    type = str(type).lower()
    path_f = []
    for d, dirs, files in os.walk('files'):
        for f in files:
            if f.find('.{0}'.format(type)) > -1:
                path = os.path.join(d, f)  # формирование адреса
                path_f.append(path)
    return {'list_file': path_f}


@app.route('/api/getfile/', methods=['GET'])
def get_cookies():
    filename = request.args['filename']
    return send_file(filename)


@app.route('/api/isliveuser/', methods=['GET'])
def is_live_user():
    tmp_pass = request.args['temp_password']
    id_user = request.args['id_user']
    connection = sqlite3.connect('db.sqlite3')
    query = 'SELECT date_password FROM temp_password WHERE password=\'{0}\' AND id_user=\'{1}\''.format(tmp_pass,
                                                                                                        id_user)
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchone()[0]
    date_last = data
    print(date_last)
    #2020-10-31 12:11:55.322477
    date_last = datetime.datetime.strptime(date_last, '%Y-%m-%d %H:%M:%S.%f')
    if date_last + datetime.timedelta(seconds=CONST_TIME_LIVE) > datetime.datetime.now():
        query_update = 'UPDATE temp_password SET date_password=\'{0}\' WHERE id_user=\'{1}\'' \
                       ' AND date_password=\'{2}\''.format(datetime.datetime.now(), id_user, data)
        cursor.execute(query_update)
        connection.commit()
        cursor.close()
        connection.close()
        return {'status': 0}
    else:
        cursor.close()
        connection.close()
        return {'status': 1}


@app.route('/api/postcode/', methods=['GET'])
def post_code_for_user():
    username_tg = request.args['username']
    connection = sqlite3.connect('db.sqlite3')
    cursor = connection.cursor()
    rand_code = random.randint(1000, 9999)
    query = 'INSERT INTO temp_tg(username, code, date_send)' \
            ' VALUES(\'{0}\', \'{1}\', \'{2}\')'.format(username_tg, str(rand_code), datetime.datetime.now())
    connection.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return {'code': str(rand_code)}

app.run()