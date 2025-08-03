from flask import Flask, render_template, request

app = Flask(__name__)

# The name of the file where we'll save the data
DATA_FILE = 'logins.txt'

# This function shows the HTML form when a user visits the site
@app.route('/')
def home():
    return render_template('register.html')

# This function handles the data when the user submits the form
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    # --- SECURITY WARNING ---
    # This part saves the data to a plain text file.
    # This is very insecure and only for a simple local test.
    try:
        with open(DATA_FILE, 'a') as f: # 'a' is for append mode
            f.write(f"Email: {email}, Password: {password}\n")
    except Exception as e:
        print(f"Error writing to file: {e}")
        return "An error occurred."

    return "Registration data saved! Check your logins.txt file."

# This starts the web server
if __name__ == '__main__':
    app.run(debug=True)