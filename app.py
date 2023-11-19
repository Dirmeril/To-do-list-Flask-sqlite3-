from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)


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

    # Pobranie drugiej listy
    sql_command = 'select * from list_1 LIMIT 1;'
    cur = db.execute(sql_command)
    table = cur.fetchone()
    sql_command = f'select * from {table[1]}'
    cur = db.execute(sql_command)
    todos_side = cur.fetchall()

    return render_template('index.html', todos=todos, todos_side=todos_side)

# Metody dla głównej listy
@app.route('/add', methods=['POST'])
def add():
    todo = request.form['todo']
    db = get_db()
    sql_command = 'insert into list_1(area) values(?);'
    db.execute(sql_command, [todo])
    db.commit()
    sql_command = f"CREATE TABLE IF NOT EXISTS '{todo}'(id INTEGER PRIMARY KEY autoincrement, action varchat(40));"
    db.execute(sql_command)
    db.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:index>/<old_todo>', methods=['GET', 'POST'])
def edit(index, old_todo):
    if request.method == 'POST':
        old_todo = old_todo
        todo = request.form['todo']

        db = get_db()
        
        sql_command = f"ALTER TABLE '{old_todo}' RENAME TO {todo};"
        db.execute(sql_command)
        db.commit()

        sql_command = "update list_1 set area=? where id = ?;"
        db.execute(sql_command, [todo, index])
        db.commit()

        return redirect(url_for('choose', action=todo ))
    else:
        db = get_db()
        sql_command = 'select * from list_1 where id = ?;'
        cur = db.execute(sql_command, [index])
        todo = cur.fetchone()
        return render_template("edit.html", todo=todo, index=index, old_todo=old_todo)


@app.route("/delete/<int:index>")
def delete(index):
    db = get_db()
    sql_command = 'select * from list_1 where id = ?;'
    cur = db.execute(sql_command, [index])
    todo = cur.fetchone()
    sql_command = f"DROP TABLE '{todo[1]}';"
    db.execute(sql_command)
    db.commit()
    sql_command = 'delete from list_1 where id = ?;'
    db.execute(sql_command, [index])
    db.commit()

    return redirect(url_for("index"))


@app.route("/<action>")
def choose(action):
    db = get_db()
    # Pobranie drugiej listy
    sql_command = 'select * from list_1 where area = ?;'
    cur = db.execute(sql_command, [action])
    table = cur.fetchone()
    sql_command = f"select * from '{table[1]}'"
    cur = db.execute(sql_command)
    todos_side = cur.fetchall()

    # Pobranie głównej listy
    sql_command = 'select * from list_1;'
    cur = db.execute(sql_command)
    todos = cur.fetchall()
    return render_template('index.html', todos=todos, todos_side=todos_side, action=action )


# Metody dla pobocznych list
@app.route('/add_side/<todo_side>', methods=['POST'])
def add_side(todo_side):
    todo = request.form['todo_side']
    db = get_db()
    sql_command = f"insert into '{todo_side}'(action) values(?);"
    db.execute(sql_command, [todo])
    db.commit()

    return redirect(url_for('choose', action=todo_side ))

@app.route('/<action>/edit_side/<int:index>', methods=['GET', 'POST'])
def edit_side(action, index):
    if request.method == 'POST':
        todo = request.form['todo']

        db = get_db()
        sql_command = f"update '{action}' set action=? where id = ?;"
        db.execute(sql_command, [todo, index])
        db.commit()
        return redirect(url_for('choose', action=action ))
    else:
        db = get_db()
        sql_command = f"select * from '{action}' where id = ?;"
        cur = db.execute(sql_command, [index])
        todo = cur.fetchone()

        return render_template("edit_side.html", todo=todo, index=index, action=action)

@app.route('/delete_side/<todo_side>/<int:index>')
def delete_side(todo_side, index):
    db = get_db()
    command_sql = f"DELETE FROM '{todo_side}' WHERE id = ?;"
    db.execute(command_sql, [index])
    db.commit()

    return redirect(url_for('choose', action=todo_side))

if __name__ == '__main__':
    app.run()   