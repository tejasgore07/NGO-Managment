from flask import Flask, render_template, request, redirect, url_for,flash, jsonify, send_file, session
from flask_mysqldb import MySQL
import qrcode
import io
import pandas as pd
from flask import send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import timedelta

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.permanent_session_lifetime = timedelta(minutes=15)

app.secret_key='supersecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='tejasdataset'
app.config['MYSQL_DB'] = 'donation'

mysql = MySQL(app) 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/news')
def news():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM news ORDER BY date DESC")
    news_items = cur.fetchall()
    cur.close()
    return render_template('news.html', news=news_items)

@app.route('/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    if 'email' in session and session['email'] == 'admin@gmail.com':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM news WHERE id = %s", (news_id,))
        mysql.connection.commit()
        cur.close()
        flash("News deleted successfully!", "success")
    return redirect(url_for('news'))

@app.route('/gallery')
def gallery():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM gallery ORDER BY uploaded_at DESC")
    images = cur.fetchall()
    cur.close()
    return render_template('gallery.html', images=images)

@app.route('/add_gallery_image', methods=['POST'])
def add_gallery_image():
    if 'email' in session and session['email'] == 'admin@gmail.com':
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join('static/gallery-img', filename))

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO gallery (filename) VALUES (%s)", (filename,))
            mysql.connection.commit()
            cur.close()

            flash("Image uploaded successfully!", "success")
    return redirect(url_for('gallery'))

@app.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM gallery WHERE id = %s", (image_id,))
    image = cur.fetchone()
    if image:
        image_path = os.path.join('static', 'gallery-img', image[0])
        if os.path.exists(image_path):
            os.remove(image_path)
        cur.execute("DELETE FROM gallery WHERE id = %s", (image_id,))
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('gallery'))



@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            stored_password = user[3]  # Assuming 0:name, 1:email, 2:password
            if check_password_hash(stored_password, password):
                session.permanent = True
                session['logged_in'] = True
                session['username'] = user[1]
                session['email'] = user[2] 
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Email not found. Please sign up.', 'warning')
            return redirect(url_for('signup'))
     return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('login'))
    return render_template('profile.html', username=session['username'])

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'email' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))

    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    email = session['email']

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE email = %s", (email,))
    result = cur.fetchone()

    if result:
        stored_password = result[0]

        if not check_password_hash(stored_password, old_password):
            flash('Old password is incorrect.', 'error')
            return redirect(url_for('profile'))

        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('profile'))

        # All checks passed, update password
        hashed_new_password = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_new_password, email))
        mysql.connection.commit()
        cur.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))

    flash('Something went wrong. Try again.', 'error')
    return redirect(url_for('profile'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('logged_in') and session.get('email') == 'admin@gmail.com':
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('home'))
    
    
@app.route('/add_news', methods=['POST'])
def add_news():
    if 'email' in session and session['email'] == 'admin@gmail.com':
        title = request.form['title']
        content = request.form['content']
        image_file = request.files['image']
        image_filename = ''

        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO news (title, content, image, date) VALUES (%s, %s, %s, NOW())",
                    (title, content, image_filename))
        mysql.connection.commit()
        cur.close()

        flash("News added successfully!", "success")
    return redirect(url_for('news'))

@app.route('/admin/upload_photo', methods=['POST'])
def upload_photo():
    return redirect(url_for('admin_dashboard'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
   if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash("Signup successful! Please login.")
        return redirect(url_for("login"))
   return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    flash("You have been logged out!", "info")
    return redirect(url_for('login'))

@app.route('/add_donor', methods=['POST'])
def add_donor():
    
    if request.method == 'POST':
       
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        amount = request.form['amount']
        transaction_id = request.form['transaction_id']

        
        cur = mysql.connection.cursor()
        query = '''
            INSERT INTO donors (first_name, last_name, mobile, email, address, amount, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        cur.execute(query, (first_name, last_name, mobile, email, address, amount, transaction_id))
        mysql.connection.commit()
        cur.close()

# 2. Save to Excel
        excel_path = 'static/donor_data.xlsx'
        new_data = pd.DataFrame([{
            'First Name': first_name,
            'Last Name': last_name,
            'Mobile': mobile,
            'Email': email,
            'Address': address,
            'Amount': amount,
            'Transaction ID': transaction_id
        }])

        # If file exists, append, else create
        if os.path.exists(excel_path):
            existing_data = pd.read_excel(excel_path)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            updated_data.to_excel(excel_path, index=False)
        else:
            new_data.to_excel(excel_path, index=False)
        
        flash("Donation Successful")
        return render_template('donate.html')
    
@app.route('/generate_upi_link', methods=['POST'])
def generate_upi_link():
    amount = request.form.get('amount')
    upi_id = "8669014136@ybl" 
    
    upi_link = f"upi://pay?pa={upi_id}&pn=Helping%20Hands%20NGO&am={amount}&cu=INR&tn=Donation"
    
    return redirect(upi_link)
@app.route("/generate_qr")
def generate_qr():
    upi_id = "8669014136@ybl"
    amount = request.args.get("amount", "100")  
    upi_link = f"upi://pay?pa={upi_id}&pn=Helping%20Hands%20NGO&am={amount}&cu=INR&tn=Donation"

    qr = qrcode.make(upi_link)
    qr_io = io.BytesIO()
    qr.save(qr_io, format="PNG")
    qr_io.seek(0)
    return send_file(qr_io, mimetype="image/png")

if __name__ == '__main__':
    app.run(debug=True)
