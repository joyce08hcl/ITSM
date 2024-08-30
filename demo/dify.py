# from flask import Flask, render_template
# from flask_wtf.csrf import CSRFProtect
# import secrets


# secret_key = secrets.token_hex(32)  # Generates a 64-character hexadecimal string
# print(secret_key)


# app = Flask(__name__)

# # Configure the secret key for CSRF protection
# app.config['SECRET_KEY'] = 'app-Vcxi8Fzi9OGgTGnAVQ3lFHMw'
# csrf = CSRFProtect(app)

# @app.route('/')
# def index():
#     return render_template('dify.html')

# if __name__ == '__main__':
#     app.run(debug=True, port=5002)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dify.html')

if __name__ == '__main__':
    app.run(debug=True, port=5006)