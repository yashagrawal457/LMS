from flask import Flask, render_template, request, redirect, session
from flaskext.mysql import MySQL
import os

app = Flask(__name__)

mysql = MySQL(app)
app.secret_key = "super secret key"
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'lms'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def index():
    if 'username' not in session:
        session['username'] = None
    return render_template('index.html',user = session['username'])

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        post_user = request.form['username']
        post_email = request.form['email']
        post_password = request.form['password']

        conn = mysql.connect()
        cursor =conn.cursor()
        cursor.execute("INSERT INTO Users VALUES (%s, %s, %s)", (post_user, post_email,post_password))
        conn.commit()
        return redirect('/')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        post_user = request.form['username']
        post_password = request.form['password']
        conn = mysql.connect()
        cursor =conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE UserName =%s AND Password = %s", [post_user,post_password])
        if cursor is not None:
            data = cursor.fetchone()
            if data is not None:
                session['username'] = post_user
                return render_template('index.html',user = post_user)
            else:
                error = 'Invalid Username or Password !!'
                return render_template('login.html',error=error)    
    else:
        return render_template('login.html')

@app.route('/books')
def book():
    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("SELECT * FROM Books")
    if cursor is not None: 
        books = cursor.fetchall() 
        return render_template('books.html',books = books,user = session['username'])

@app.route('/mybooks')
def mybooks():
    conn = mysql.connect()
    cursor =conn.cursor()
    user_id = session['username']
    cursor.execute("Select Books.Book, Issued.* from Books , Issued  where Books.book_id=Issued.book_id and Issued.user_name =%s", [user_id])
    if cursor is not None: 
        books = cursor.fetchall() 
        return render_template('mybooks.html',books = books,user = session['username'])

    

@app.route('/add', methods=['GET','POST'])
def add():
    if 'username' not in session or session['username'] != "yash57":
        return redirect('/')
    if request.method == 'POST':
        book_id = request.form['id']
        book_title = request.form['title']
        book_author = request.form['author']
        file = request.files['file']
        file_name = book_id + ".jpg"
        file.save(os.path.join("static/images", file_name))
        conn = mysql.connect()
        cursor =conn.cursor()
        cursor.execute("INSERT INTO Books(Book_id, Book, Author) VALUES (%s, %s, %s)", (book_id, book_title,book_author))
        conn.commit()
        return redirect('/',user = session['username'])
    else:
        return render_template('add.html',user = session['username'])

@app.route('/books/<book_id>')
def checkout(book_id):
    user_id = session['username']
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "INSERT INTO Issued(user_name,book_id,date) VALUES ('" + user_id + "','" + book_id + "', now())"
    print(query)
    cursor.execute(query)
    conn.commit()
    return redirect('/mybooks')

@app.route('/issued')
def issuedbooks():
    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("Select Books.Book, Issued.* from Books , Issued  where Books.book_id=Issued.book_id")
    if cursor is not None: 
        books = cursor.fetchall() 
        print(books)
        return render_template('mybooks.html',books = books,user = session['username'])

@app.route('/return/<book_id>')
def return_book(book_id):
    user_id = session['username']
    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute("DELETE from Issued where user_name = %s and book_id = %s", (user_id, book_id))
    conn.commit()
    return redirect('/mybooks')




@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')


if __name__ == "__main__":
    
    app.run(debug = True)
