from flask import Blueprint, request
from flask_restful import Api, Resource
from . import auth, client


payment_api = Blueprint('payment_api', __name__)
api = Api(payment_api)


class MakePayment(Resource):
    @auth.login_required()
    def get(self):
        data = request.args
        order = client.order.create({
            "amount": int(data["amount"]) * 100,
            "currency": "INR",
            "receipt": "#1receipt",
            "notes": {
                "note1": "payment"
            }
        })
        return {'success': True, "order_id": order['id']}


api.add_resource(MakePayment, '/payment')

