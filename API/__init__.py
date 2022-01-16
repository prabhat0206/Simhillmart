from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
import razorpay

app = Flask(__name__)
app.config.from_pyfile('config.py')
api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
auth = HTTPTokenAuth()
CORS(app)

db.init_app(app)
migrate.init_app(app, db)

client = razorpay.Client(auth=("rzp_test_VUcw251Tkcl3sR", "Clml3v4ZxdCi7hmvGAsVkfDR"))


def get_model_dict(model):
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns)


from .admin import admin
from .products import product_api
from .Account import account_api
from .model import User
from .order import order_api
from .payment import payment_api

@auth.verify_token
def verify_token(token):
    user = User.query.filter_by(token=token).first()
    if user is not None:
        return user.uid
    else:
        return False


app.register_blueprint(product_api, url_prefix="/")
app.register_blueprint(account_api, url_prefix="/")
app.register_blueprint(payment_api, url_prefix="/")
app.register_blueprint(order_api, url_prefix="/")
app.register_blueprint(admin, url_prefix="/admin")

