""" Main application and routing logic for TwitOff. """
import os
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():
    """ Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #app.config['ENV'] = config['ENV']
    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title="Home", users=users)

    # @app.route('/update')

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None):
        message = ''
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = 'User {} successfully added!'.format(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']
        predictions = predict_user(user1, user2, tweet_text)
        return render_template('compare.html', title='Prediction',
                                tweet_text=tweet_text, predictions=predictions,
                                user1=user1, user2=user2)

    @app.route('/reset') # remove for production
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset', users=[])

    return app
