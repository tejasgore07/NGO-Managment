from flask import Flask, render_template, request, redirect, url_for,flash
from flask_mysqldb import MySQL
app = Flask(__name__)

app.secret_key='supersecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tejasdataset'
app.config['MYSQL_DB'] = 'donation'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('donate.html')

# Route to handle form submission
@app.route('/add_donor', methods=['POST'])
def add_donor():
    # Ensure the method is POST
    if request.method == 'POST':
        # Retrieve data from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        amount = request.form['amount']
        transaction_id = request.form['transaction_id']

        # Insert data into the MySQL database
        cur = mysql.connection.cursor()
        query = '''
            INSERT INTO donors (first_name, last_name, mobile, email, address, amount, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        cur.execute(query, (first_name, last_name, mobile, email, address, amount, transaction_id))
        mysql.connection.commit()
        cur.close()

        flash("Donation Successful")

        # Redirect to a confirmation page or back to the form (optional)
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
