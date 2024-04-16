import pandas as pd
from flask import Flask, render_template, request
import mysql.connector
from flask import render_template, request, redirect, url_for, session
from flask import flash
from flask import jsonify
from flask import render_template, flash

# Import predict_loan_approval function from loan.py
from loan import predict_loan_approval
from flask import render_template, flash, get_flashed_messages
from flask import jsonify
# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="",
    database="sports",
)
cursor = conn.cursor()

# Load the dataset
loan_data = pd.read_csv('loan_prediction.csv')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/loan_applications')
def loan_applications():
    # Fetch data from the loan_applications table
    cursor.execute("SELECT * FROM loan_applications")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]  # Get column names

    return render_template('loan_applications.html', data=data, columns=columns)


@app.route('/update_status', methods=['POST'])
def update_status():
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('status_'):
                loan_id = key.split('_')[1]
                new_status = value
                # Update the status in the database
                cursor.execute("UPDATE loan_applications SET status = %s WHERE id = %s", (new_status, loan_id))
                conn.commit()
        flash('Status updated successfully', 'success')
        return redirect('/loan_applications')
    flash('Invalid request', 'error')
    return redirect('/loan_applications')


@app.route('/predict', methods=['POST'])
def predict():
    # Get user input from the form
    account_number = request.form['account_number']
    gender = request.form['gender']
    married = request.form['married']
    dependents = request.form['dependents']
    education = request.form['education']
    self_employed = request.form['self_employed']
    applicant_income = float(request.form['applicant_income'])
    coapplicant_income = float(request.form['coapplicant_income'])
    loan_amount = float(request.form['loan_amount'])
    loan_amount_term = float(request.form['loan_amount_term'])
    credit_history = float(request.form['credit_history'])
    property_area = request.form['property_area']

    # Make prediction using loan.py
    prediction = predict_loan_approval(account_number, gender, married, dependents, education, self_employed,
                                       applicant_income,
                                       coapplicant_income, loan_amount, loan_amount_term, credit_history, property_area)

    # Check if the predicted status is 'Y' in the dataset for approval
    if prediction == 1:  # 1 represents 'Y' in the dataset
        message = 'Congratulations! Your loan is approved.'
    else:
        message = 'Sorry, your loan application is not approved.'

    # Store the submitted data into the MySQL database
    try:
        cursor = conn.cursor()
        # SQL query to insert data into the table
        sql = "INSERT INTO loan_applications (account_number, gender, married, dependents, education, self_employed, applicant_income, coapplicant_income, loan_amount, loan_amount_term, credit_history, property_area, status, mlpredict) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Execute the SQL query
        cursor.execute(sql, (
        account_number, gender, married, dependents, education, self_employed, applicant_income, coapplicant_income,
        loan_amount, loan_amount_term, credit_history, property_area, 'pending', message))

        # Commit changes to the database
        conn.commit()

        # Flash a success message
        flash('Your loan application has been submitted successfully!', 'success')

    except Exception as e:
        # Rollback in case of any error
        conn.rollback()
        raise e
    finally:
        # Close the cursor
        cursor.close()

    return render_template('index.html')

def register_customer(account_number, mobile_number):
    try:
        # SQL query to insert customer data into the table
        sql = "INSERT INTO customer (Account_Number, Mobile_Number) VALUES (%s, %s)"
        values = (account_number, mobile_number)

        # Execute the SQL query
        cursor.execute(sql, values)

        # Commit the transaction
        conn.commit()

        return True, None
    except Exception as e:
        return False, str(e)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the account number and mobile number from the form submission
        account_number = request.form['account_number']
        mobile_number = request.form['mobile_number']

        # Call the register_customer function to insert data into the database
        success, message = register_customer(account_number, mobile_number)

        # Check if registration was successful
        if success:
            flash('Registration successful!', 'success')  # Flash success message
            return redirect(url_for('register'))  # Redirect to the registration page
        else:
            flash(f'Registration failed: {message}', 'danger')  # Flash failure message
            return redirect(url_for('register'))  # Redirect to the registration page
    else:
        return render_template('customer_registration.html')



@app.route('/log')
def log():
    return render_template('login.html')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    account_number = request.form['account_number']

    # Check if the account number exists in the database
    cursor.execute("SELECT * FROM customer WHERE Account_Number = %s", (account_number,))
    result = cursor.fetchone()

    if result:
        # Account number exists, store it in the session and redirect to the bank page
        session['account_number'] = account_number
        return redirect(url_for('bank'))
    else:
        # Account number doesn't exist, display an error message
        flash('Invalid account number', 'error')
        return redirect(url_for('log'))


@app.route('/bank')
def bank():
    # Check if the user is logged in (i.e., if the account number is stored in the session)
    if 'account_number' in session:
        return render_template('bank.html')
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('log'))

@app.route('/loan_status')
def loan_status():
    if 'account_number' in session:
        account_number = session['account_number']
        cursor.execute("SELECT id, account_number, gender, married, dependents, education, self_employed, applicant_income, coapplicant_income, loan_amount, loan_amount_term, credit_history, property_area, status FROM loan_applications WHERE account_number = %s", (account_number,))
        loan_data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return render_template('loan_status.html', data=loan_data, columns=columns)
    else:
        flash('Please log in to view loan status.', 'error')
        return redirect(url_for('log'))




if __name__ == '__main__':
    app.run(debug=True)
