from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS login
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        con.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students', methods=['POST', 'GET'])
def redirect():
    return render_template('students.html')

@app.route('/display', methods=['POST', 'GET'])
def display():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM login")
        records = cur.fetchall()
    return render_template('display.html', records=records)

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        msg = ""
        try:
            username = request.form['username']
            password = request.form['password']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO login (username, password) VALUES (?, ?)", (username, password))
                con.commit()
                msg = "Record successfully added"
        except sqlite3.IntegrityError:
            msg = "Username already exists"
        except Exception as e:
            msg = f"Error in insert operation: {str(e)}"
        finally:
            return render_template('result.html', msg=msg)
    return render_template('result2.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        msg = ""
        try:
            username = request.form['username']
            password = request.form['password']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM login WHERE username = ? AND password = ?", (username, password))
                records = cur.fetchall()
                if records:
                    msg = "Login successful"
                else:
                    msg = "Login failed"
        except Exception as e:
            msg = f"Error in login: {str(e)}"
        finally:
            return render_template('result.html', msg=msg)
    return render_template('login.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)