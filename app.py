from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
import random
import string
import hashlib
import binascii


app = Flask(__name__)


app.config['SECRET_KEY'] = '123QQ'

app_info = {'db_file' : r"C:\Users\Laptop-D\Documents\Dokumenty\Python\Flask\CRUD\data\tododb.db",
            'db_user' : r"C:\Users\Laptop-D\Documents\Dokumenty\Python\Flask\CRUD\data\user.db"}


class UserPass:
    
    def __init__(self, user='', password='',email=''):
        self.user = user
        self.password = password
        self.email = email
        self.is_valid = False
        self.is_admin = False

    def hash_password(self):
        os_urandom_static = b"ID_\x12p:\x8d\xe7&\xcb\xf0=H1\xc1\x16\xac\xe5BX\xd7\xd6j\xe3i\x11\xbe\xaa\x05\xccc\xc2\xe8K\xcf\xf1\xac\x9bFy(\xfbn.`\xe9\xcd\xdd'\xdf`~vm\xae\xf2\x93WD\x04"
        salt = hashlib.sha256(os_urandom_static).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', self.password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')
    
    def verify_password(self, stored_password, provided_password): 
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password
    
    def get_random_user_pasword(self):
        random_user = ''.join(random.choice(string.ascii_lowercase)for i in range(3))
        self.user = random_user 
        password_characters = string.ascii_letters #+ string.digits + string.punctuation
        random_password = ''.join(random.choice(password_characters)for i in range(3))
        self.password = random_password


    def login_user(self):
        db_u = get_db()
        sql_statement = 'select id, name, email, password, is_active, is_admin from users where name=?;'
        cur = db_u.execute(sql_statement, [self.user])
        user_record = cur.fetchone()

        if user_record != None and self.verify_password(user_record['password'], self.password):
            return user_record
        else:
            self.user = None
            self.password = None
            return None
    
    def get_user_info(self):
        db_u = get_db()
        sql_statement = 'select name, email, is_active, is_admin from users where name=?'
        cur = db_u.execute(sql_statement, [self.user])
        db_user = cur.fetchone()

        if db_user == None:
            self.is_valid = False
            self.is_admin = False
            self.email = ''
        elif db_user['is_active'] !=1:
            self.is_valid = False
            self.is_admin = False
            self.email = db_user['email']
        else:
            self.is_valid = True
            self.is_admin = db_user['is_admin']
            self.email = db_user['email']


def get_db():
    if not hasattr(g, 'sqlite_db'): 
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
        return g.sqlite_db
    db = getattr(g, 'sqlite_db', None)
    if db is None:
        db = g.sqlite_db = sqlite3.connect(app_info['db_file'])
    return db

# connetction to user_db
def get_db_user():
    if not hasattr(g, 'sqlite_db'): 
        conn = sqlite3.connect(app_info['db_user'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
        return g.sqlite_db


@app.teardown_appcontext 
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def welcome():
    login = UserPass(session.get('user'))
    login.get_user_info()

    return render_template('welcome.html', login=login)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html', active_menu='login')
    else:
        user_name = '' if 'user_name' not in request.form else request.form['user_name']
        user_pass = '' if 'user_pass' not in request.form else request.form['user_pass']

        login = UserPass(user_name, user_pass)
        login_record = login.login_user()

        if login_record != None:    
            session['user'] = user_name
            flash('Login succesfull, welcome {}'.format(user_name))
            return redirect(url_for('index'))
        else:
            flash('Login failed, try again')
            return render_template('login.html', active_menu='login')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    
    db = get_db()
    message = None
    user = {}

    if request.method =='GET':
        return render_template('registration.html', active_menu='users', user=user)
    else:
        user['user_name'] = '' if not 'user_name' in request.form else request.form['user_name']
        user['email'] = '' if not 'email' in request.form else request.form['email']
        user['user_pass'] = '' if not 'user_pass' in request.form else request.form['user_pass']
        user['user_pass_again'] = '' if not'user_pass_again' in request.form else request.form['user_pass_again']

        cursor = db.execute('select count(*) as cnt from users where name = ?', [user['user_name']])
        record = cursor.fetchone()
        is_user_name_unique = (record['cnt'] == 0)
        cursor = db.execute('select count(*) as cnt from users where email = ?', [user['email']])
        record = cursor.fetchone()
        is_user_email_unique = (record['cnt'] == 0)
        
        if user['user_name'] == '':
            message = 'Name cannot be empty'
        elif user['email'] == '':
            message = 'email cannot be empty'
        elif user['user_pass'] == '':
            message = 'Password cannot be empty'
        elif user['user_pass'] != user['user_pass_again']:
            message = 'Passwords must be same'
        elif not is_user_name_unique:
            message = 'User with the name {} already exists'.format(user['user_name'])
        elif not is_user_email_unique:
            message = 'User with the email {} alresdy exists'.format(user['email'])

        if not message:
            user_pass = UserPass(user['user_name'], user['user_pass'])
            password_hash = user_pass.hash_password()
            sql_statement = '''insert into users(name, email, password, is_active, is_admin) values(?,?,?, True, False);'''
            db.execute(sql_statement, [user['user_name'], user['email'], password_hash])
            db.commit()
            # Create table for user
            sql_statement = f"CREATE TABLE '{user['user_name']}' (id INTEGER PRIMARY KEY autoincrement, area varchat(25) NOT NULL);"
            db.execute(sql_statement)
            db.commit()
            flash('User {} created'.format(user['user_name']))
            return redirect(url_for('index'))
        else:
            flash('Correct error: {}'.format(message))
            return render_template('registration.html', active_menu='users', user=user)


@app.route('/logout')
def logout():

    if 'user' in session:
        session.pop('user', None)
        flash('You are logged out')
    return redirect(url_for('login'))


@app.route('/index')
def index():
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    db = get_db()
    sql_command = f"select * from '{login.user}';"
    cur = db.execute(sql_command)
    todos = cur.fetchall()
    
    # Pobranie drugiej listy
    sql_command = f"select * from '{login.user}' LIMIT 1;"
    cur = db.execute(sql_command)
    table = cur.fetchone()
    
    if table != None:
        sql_command = f"select * from '{login.user+table[1]}'"
        cur = db.execute(sql_command)
        todos_side = cur.fetchall()
        action = table[1]
    else:
        action = None
        todos_side = None
    
    return render_template('index.html', todos=todos, todos_side=todos_side, action=action, login=login)
   

# app.py – init route and function
@app.route('/init_app')
def init_app():
    # check if there are users defined (at least one active admin required)
    db = get_db()
    sql_statement = 'select count(*) as cnt from users where is_active and is_admin;'
    cur = db.execute(sql_statement)
    active_admins = cur.fetchone()
    if active_admins!=None and active_admins['cnt']>0:
        flash('Application is already set-up. Nothing to do')
        return redirect(url_for('index')) # if not - create/update admin account with a new password and admin privileges, display random username
    user_pass = UserPass()
    user_pass.get_random_user_pasword()
    sql_statement = '''insert into users(name, email, password, is_active, is_admin) values(?,?,?,True, True);'''
    db.execute(sql_statement, [user_pass.user, 'noone@nowhere.no', user_pass.hash_password()])
    db.commit()
    flash('User {} with password {} has been created'.format(user_pass.user, user_pass.password))
    return redirect(url_for('index'))


# Metody dla głównej listy
@app.route('/add', methods=['POST'])
def add():
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    todo = request.form['todo']
    if todo.strip() == '':
        return redirect(url_for('index')), flash('Pole nie może być puste')
    db = get_db()
    sql_command = f"insert into '{login.user}' (area) values(?);"
    db.execute(sql_command, [todo])
    db.commit()
    sql_command = f"CREATE TABLE IF NOT EXISTS '{login.user+todo}'(id INTEGER PRIMARY KEY autoincrement, action varchat(40) NOT NULL, done BOOLEAN);"
    db.execute(sql_command)
    db.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:index>/<old_todo>', methods=['GET', 'POST'])
def edit(index, old_todo):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    

    if request.method == 'POST':
        old_todo = old_todo
        todo = request.form['todo']

        db = get_db()
        
        sql_command = f"ALTER TABLE '{login.user+old_todo}' RENAME TO {login.user+todo};"
        db.execute(sql_command)
        db.commit()

        sql_command = f"update '{login.user}' set area=? where id = ?;"
        db.execute(sql_command, [todo, index])
        db.commit()

        return redirect(url_for('choose', action=todo, login=login ))
    else:
        db = get_db()
        sql_command = f"select * from '{login.user}' where id = ?;"
        cur = db.execute(sql_command, [index])
        todo = cur.fetchone()
        return render_template("edit.html", todo=todo, index=index, old_todo=old_todo, login=login)


@app.route("/delete/<int:index>")
def delete(index):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    db = get_db()
    sql_command = f"select * from '{login.user}' where id = ?;"
    cur = db.execute(sql_command, [index])
    todo = cur.fetchone()
    sql_command = f"DROP TABLE '{login.user+todo[1]}';"
    db.execute(sql_command)
    db.commit()
    sql_command = f"delete from '{login.user}' where id = ?;"
    db.execute(sql_command, [index])
    db.commit()

    return redirect(url_for("index", login=login))


@app.route("/choosen/<action>")
def choose(action):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    db = get_db()

    # Pobranie drugiej listy
    sql_command = f"select * from '{login.user}' where area = ?;"
    cur = db.execute(sql_command, [action])
    table = cur.fetchone()
    sql_command = f"select * from '{login.user+action}'"
    cur = db.execute(sql_command)
    todos_side = cur.fetchall()

    # Pobranie głównej listy
    sql_command = f"select * from '{login.user}';"
    cur = db.execute(sql_command)
    todos = cur.fetchall()
    return render_template('index.html', todos=todos, todos_side=todos_side, action=action, login=login)


# Metody dla pobocznych list
@app.route('/add_side/<todo_side>', methods=['POST'])
def add_side(todo_side):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    todo = request.form['todo_side']
    db = get_db()
    sql_command = f"insert into '{login.user+todo_side}' (action, done) values(?,?);"
    db.execute(sql_command, [todo, False])
    db.commit()

    return redirect(url_for('choose', action=todo_side, login=login))


@app.route('/<action>/edit_side/<int:index>', methods=['GET', 'POST'])
def edit_side(action, index):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        todo = request.form['todo']

        db = get_db()
        sql_command = f"update '{login.user+action}' set action=? where id = ?;"
        db.execute(sql_command, [todo, index])
        db.commit()
        return redirect(url_for('choose', action=action, login=login ))
    else:
        db = get_db()
        sql_command = f"select * from '{login.user+action}' where id = ?;"
        cur = db.execute(sql_command, [index])
        todo = cur.fetchone()

        return render_template("edit_side.html", todo=todo, index=index, action=action, login=login)


@app.route('/delete_side/<todo_side>/<int:index>')
def delete_side(todo_side, index):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    db = get_db()
    command_sql = f"DELETE FROM '{login.user+todo_side}' WHERE id = ?;"
    db.execute(command_sql, [index])
    db.commit()

    return redirect(url_for('choose', action=todo_side, login=login))


@app.route('/done/<action>/<int:index>')
def done(action, index):
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login'))
    
    db = get_db()
    command_sql = f"select done from '{login.user+action}' where id = ?;"
    cur = db.execute(command_sql, [index])
    done = cur.fetchone()

    if done[0] == True:
        command_sql = f"update '{login.user+action}' set done=? where id = ?;"
        db.execute(command_sql, [False, index])
        db.commit()
    else:
        command_sql = f"update '{login.user+action}' set done=? where id = ?;"
        db.execute(command_sql, [True, index])
        db.commit()
    
    return redirect(url_for('choose', action=action, login=login))


if __name__ == '__main__':
    app.run()   