import json
import os

import requests
from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

vk_id = '7069242'
vk_secret = '0HGWyQwWskHkoyR9f2dz'
vk_url = 'https://vkauth-web.herokuapp.com/profile/'


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200))
    first_name = db.Column(db.String(200))
    sur_name = db.Column(db.String(200))
    first_friend_first_name = db.Column(db.String(200))
    first_friend_sur_name = db.Column(db.String(200))
    second_friend_first_name = db.Column(db.String(200))
    second_friend_sur_name = db.Column(db.String(200))
    third_friend_first_name = db.Column(db.String(200))
    third_friend_sur_name = db.Column(db.String(200))
    fourth_friend_first_name = db.Column(db.String(200))
    fourth_friend_sur_name = db.Column(db.String(200))
    fifth_friend_first_name = db.Column(db.String(200))
    fifth_friend_sur_name = db.Column(db.String(200))

    def __repr__(self):
        return self.user_id


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'user' in request.cookies:
        print(request.cookies['user'])
        return redirect('/profile/')

    if request.method == 'POST':
        access_code_url = 'https://oauth.vk.com/authorize?client_id=' + vk_id \
                          + '&display=page&redirect_uri=' + vk_url \
                          + '&scope=friends&response_type=code&v=5.52'

        return redirect(access_code_url)
    else:
        return render_template('index.html')


@app.route('/profile/', methods=['POST', 'GET'])
def profile():
    if 'user' in request.cookies:
        user_id = request.cookies['user']
    else:
        access_code = request.args['code']
        access_token_url = 'https://oauth.vk.com/access_token?client_id=' + vk_id \
                           + '&redirect_uri=' + vk_url \
                           + '&client_secret=' + vk_secret + '&code=' + access_code
        data = requests.get(access_token_url).json()
        access_token = data['access_token']
        user_id = data['user_id']
        expires_in = data['expires_in']

        access_data_url = 'https://api.vk.com/method/users.get?user_id=' \
                          + str(user_id) + '&access_token=' + str(access_token) \
                          + '&fields=first_name,last_name' + '&v=5.52'
        user_data = requests.get(access_data_url).content
        user_json = json.loads(user_data)
        user_id = user_json['response'][0]['id']
        user_first_name = user_json['response'][0]['first_name']
        user_last_name = user_json['response'][0]['last_name']

        access_friends_url = 'https://api.vk.com/method/friends.get?user_id=' \
                             + str(user_id) + '&access_token=' + str(access_token) \
                             + '&count=5&fields=first_name,last_name' + '&v=5.52'
        friends_data = requests.get(access_friends_url).content
        friends_json = json.loads(friends_data)
        friends_items = [[friend['first_name'], friend['last_name']] for friend in friends_json['response']['items']]

        check_user = db.session.query(Auth).filter_by(user_id=user_id).first()

        if check_user is None:
            new_user = Auth(user_id=user_id, first_name=user_first_name, sur_name=user_last_name,
                            first_friend_first_name=friends_items[0][0], first_friend_sur_name=friends_items[0][1],
                            second_friend_first_name=friends_items[1][0], second_friend_sur_name=friends_items[1][1],
                            third_friend_first_name=friends_items[2][0], third_friend_sur_name=friends_items[2][1],
                            fourth_friend_first_name=friends_items[3][0], fourth_friend_sur_name=friends_items[3][1],
                            fifth_friend_first_name=friends_items[4][0], fifth_friend_sur_name=friends_items[4][1])

            db.session.add(new_user)
            db.session.commit()

    get_user = db.session.query(Auth).filter_by(user_id=user_id).first()
    person = get_user.first_name + " " + get_user.sur_name
    friend_first = get_user.first_friend_first_name + " " + get_user.first_friend_sur_name
    friend_second = get_user.second_friend_first_name + " " + get_user.second_friend_sur_name
    friend_third = get_user.third_friend_first_name + " " + get_user.third_friend_sur_name
    friend_fourth = get_user.fourth_friend_first_name + " " + get_user.fourth_friend_sur_name
    friend_fifth = get_user.fifth_friend_first_name + " " + get_user.fifth_friend_sur_name

    resp = make_response(render_template('profile.html', person=person, friend_first=friend_first,
                                         friend_second=friend_second, friend_third=friend_third,
                                         friend_fourth=friend_fourth, friend_fifth=friend_fifth))

    if 'user' is not request.cookies:
        resp.set_cookie('user', get_user.user_id, max_age=expires_in)

    return resp


if __name__ == '__main__':
    app.run()
