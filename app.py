from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)

# todos = [{'task': "sample todo", 'done': False}]

app.config['SECRET_KEY'] = '123QQ'

app_info = {'db_file' : r"C:\Users\Laptop-D\Documents\Dokumenty\Python\Flask\CRUD\data\tododb.db" }

def get_db():
    if not hasattr(g, 'sqlite_db'): 
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
        return g.sqlite_db
    
@app.teardown_appcontext 
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()





@app.route('/')
def index():
    db = get_db()
    sql_command = 'select * from list_1;'
    cur = db.execute(sql_command)
    todos = cur.fetchall()
    return render_template('index.html', todos=todos)


@app.route('/add', methods=['POST'])
def add():
    todo = request.form['todo']
        
    db = get_db()
    sql_command = 'insert into list_1(area) values(?);'
    db.execute(sql_command, [todo])
    db.commit()


    return redirect(url_for('index'))


@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if request.method == 'POST':
        todo = request.form['todo']

        db = get_db()
        sql_command = "update list_1 set area=? where id = ?;"
        db.execute(sql_command, [todo, index])
        db.commit()
        return redirect(url_for('index'))
    else:
        db = get_db()
        sql_command = 'select * from list_1 where id = ?;'
        cur = db.execute(sql_command, [index])
        todo = cur.fetchone()
        return render_template("edit.html", todo=todo, index=index)
    

# @app.route("/check/<int:index>")
# def check(index):
#     todos[index]['done'] = not todos [index]['done']
#     return redirect(url_for("index"))


@app.route("/delete/<int:index>")
def delete(index):
    db = get_db()
    sql_command = 'delete from list_1 where id = ?;'
    db.execute(sql_command, [index])
    db.commit()

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()   