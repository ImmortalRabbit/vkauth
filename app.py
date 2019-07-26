from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from json import decoder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
db = SQLAlchemy(app)

vk_id = '7069242'
vk_secret = '0HGWyQwWskHkoyR9f2dz'
vk_url = 'https://vkauth-web.herokuapp.com/profile/'


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200))

    def __repr__(self):
        return self.token


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        access_code_url = 'https://oauth.vk.com/authorize?client_id=' + vk_id \
                          + '&display=page&redirect_uri=' + vk_url\
                          + '&scope=friends&response_type=code&v=5.52'
        print("access_code_url")
        print(access_code_url)
        return redirect(access_code_url)
    else:
        return render_template('index.html')


@app.route('/profile/', methods=['POST', 'GET'])
def profile():
    access_code = request.args['code']
    access_token_url = 'https://oauth.vk.com/access_token?client_id=' + vk_id \
                      + '&redirect_uri=' + vk_url \
                      + '&client_secret=' + vk_secret + '&code=' + access_code\

    print(access_token_url)
    # user_id = request.args['user_id']
    # print(user_id)
    data = requests.get(access_token_url).json()
    access_token = data['access_token']
    user_id = data['user_id']
    access_data_url = 'https://api.vk.com/method/users.get?user_id='\
                      + str(user_id) + '&access_token=' + str(access_token)\
                      + '&fields=first_name,last_name' + '&v=5.52'
    user_data = requests.get(access_data_url).content
    return user_data
    # print(user_data['first_name'])
    # print(user_data['last_name'])

    return render_template('profile.html')


if __name__ == '__main__':
    app.run()
