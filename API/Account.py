from flask import Blueprint, request, abort
from flask_restful import Api, Resource
from functools import wraps
from . import db, get_model_dict, auth
from .model import User, Address

account_api = Blueprint('account_api', __name__)
api = Api(account_api)


class Login(Resource):

    def post(self):
        if request.headers.get('Authorization') is not None:
            token = request.headers.get('Authorization').replace("Bearer ", "")
            if token == "thisisnewtoken":
                data = request.get_json()
                ph_number = data['ph_number']
                token = data['token']
                user = User.query.filter_by(phone=ph_number).first()
                if user:
                    user.token = token
                    db.session.commit()
                    return {"Success": True, "Token": token, "isUser": True}
                return {"Success": False, "Error": "User not found", "isUser": False}
            else:
                abort(401)
        else:
            abort(401)


class Register(Resource):

    def post(self):
        if request.headers.get('Authorization') is not None:
            token = request.headers.get('Authorization').replace("Bearer ", "")
            if token == "thisisnewtoken":
                data = request.get_json()
                ph_number = data['ph_number']
                name = data['name']
                token = data['token']

                user = User.query.filter_by(phone=ph_number).first()
                if user:
                    return {"Success": False, "Error": "Phone number is already in use"}
                
                new_User = User(name=name, token=token, phone=ph_number)
                db.session.add(new_User)
                db.session.commit()
                return {"Success": True, "User": get_model_dict(new_User)}
            else:
                abort(401)
        else:
            abort(401)


class AddressAPI(Resource):

    @auth.login_required()
    def get(self):
        if request.get_json():
            data = request.get_json()
            address = Address.query.filter_by(address_id=data["address_id"]).first()
            return {"Success": True, "Address": get_model_dict(address)}
        
        addresses = Address.query.filter(Address.uid == auth.current_user()).all()
        all_addresses = []
        for address in addresses:
            all_addresses.append(get_model_dict(address))
        return {"Success": True, "Addresses": all_addresses}

    
    @auth.login_required()
    def post(self):
        data = request.get_json()
        name = data['name']
        country = "India"
        address_1 = data['address1']
        address_2 = data['address2']
        city = data['city']
        state = data['state']
        pin_code = int(data['pincode'])
        telephone = int(data['phone'])
        new_Address = Address(
            uid=auth.current_user(),
            name=name,
            country=country,
            address_1=address_1,
            address_2=address_2,
            city=city,
            state=state,
            pin_code=pin_code,
            telephone=telephone
        )
        db.session.add(new_Address)
        db.session.commit()
        return {"Success": True, "Address": get_model_dict(new_Address)}

    @auth.login_required()
    def delete(self):
        data = request.get_json()
        address = Address.query.filter_by(address_id=data["address_id"]).first()
        db.session.delete(address)
        db.session.commit()
        return {"Success": True, "message": "Address deleted"}

    @auth.login_required()
    def put(self):
        data = request.get_json()
        name = data['name']
        country = "India"
        address_1 = data['address1']
        address_2 = data['address2']
        city = data['city']
        state = data['state']
        pin_code = data['pincode']
        telephone = data['phone']
        address_id = data['address_id']

        address = Address.query.filter_by(address_id=address_id).first()
        
        address.name= name
        address.country= country
        address.address_1= address_1
        address.address_2=address_2
        address.city=city
        address.state=state
        address.pin_code=pin_code
        address.telephone=telephone

        db.session.commit()

        return {"Success": True, "message": "Address updated successfully"}


class GETUSERDATA(Resource):

    @auth.login_required()
    def get(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        return {"Success": True, "user": get_model_dict(user)}


api.add_resource(Login, "/auth/login")
api.add_resource(Register, "/auth/register")
api.add_resource(AddressAPI, "/profile/address")
api.add_resource(GETUSERDATA, "/profile")

