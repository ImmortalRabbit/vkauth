from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
db = SQLAlchemy(app)

vk_id = '7069242'
vk_secret = '0HGWyQwWskHkoyR9f2dz'
vk_url = 'https://vkauth-web.herokuapp.com/profile.html'


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200))

    def __repr__(self):
        return self.token


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        access_code_url = 'https://oauth.vk.com/authorize?client_id='+ vk_id \
                          + '&display=page&redirect_uri='+ vk_url\
                          + '&scope=friends&response_type=code'
        return redirect(access_code_url)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
