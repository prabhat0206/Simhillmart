from datetime import datetime
from flask import Blueprint, request
from . import auth, get_model_dict, db, auth, client
from flask_restful import Api, Resource
from .model import *


order_api = Blueprint('order_api', __name__)
api = Api(order_api)


class Wishlist(Resource):

    @auth.login_required()
    def get(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        wishlist = []
        for product in user.wishlist:
            new_product = get_model_dict(product)
            del new_product['uid']
            wishlist.append(new_product)
        
        return {"Success": True, "wishlist": wishlist}

    @auth.login_required()
    def post(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        data = request.get_json()
        product_id = data['product_id']
        product = Product.query.filter_by(product_id=product_id).first()
        if user and product:
            if product in user.wishlist:
                return {"Success": False, "wishlist": "product already in wishlist"}
            
            user.wishlist.append(product)
            db.session.commit()
            return {"Success": True, "wishlist": "product added to wishlist"}
        return {"Success": False, "error": "Something went wrong"}
    
    @auth.login_required()
    def delete(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        data = request.get_json()
        product_id = data['product_id']
        product = Product.query.filter_by(product_id=product_id).first()
        if user and product:
            if product in user.wishlist:
                user.wishlist.remove(product)
                db.session.commit()
                return {"Success": True, "message": "Product removed successfully"}
            return {"Success": False, "message": "Product not in wishlist"}
        return {"Success": False, "message": "Something went wrong"}


class CartAPI(Resource):
    
    @auth.login_required()
    def get(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        product_ids = []
        
        if user.cart:
            for product in user.cart:
                product_ids.append(product.pid)

            products = Product.query.filter(Product.product_id.in_(product_ids)).all()
            all_products = []
            total_price = 0
            for product in products:
                for pid in user.cart:
                    if product.product_id == pid.pid:
                        new_Product = get_model_dict(product)
                        del new_Product['uid']
                        total_price += int(product.sale_price) * int(pid.quantity)
                        all_products.append({
                            "product": new_Product,
                            "quantity": pid.quantity
                        })
            
            return {"Success": True, "cart_items": all_products, "total_price": total_price}
        return {"Success": False, "message": "Cart not found"}


    @auth.login_required()
    def post(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        data = request.get_json()
        product_id = data['product_id']
        quantity = data['quantity']

        if user.cart:
            for product in user.cart:
                if product_id == product.pid:
                    product.quantity = quantity
                    if product.quantity > 0:
                        db.session.commit()
                        return {"Success": True, "message": "Product added in cart"}
                    else:
                        db.session.delete(product)
                        db.session.commit()
                        return {"Success": True, "message": "Product removed from cart"}
                
            new_Cart = Cart(uid=auth.current_user(), pid=product_id, quantity=quantity)
            db.session.add(new_Cart)
            db.session.commit()
            return {"Success": True, "message": "Added product in cart"}
        else:
            new_Cart = Cart(uid=auth.current_user(), pid=product_id, quantity=quantity)
            db.session.add(new_Cart)
            db.session.commit()
            return {"Success": True, "message": "Added product in cart"}

    @auth.login_required()
    def delete(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        data = request.get_json()
        product_id = data['product_id']

        for product in user.cart:
            if product.pid == product_id:
                cart_item = Cart.query.filter_by(cart_id=product.cart_id).first()
                db.session.delete(cart_item)
                db.session.commit()
                return {"Success": True, "message": "Removed from cart"}

        return {"Success": False, "message": "Item not found in cart"}



class OrderAPI(Resource):

    @auth.login_required()
    def get(self):
        user = User.query.filter_by(uid=auth.current_user()).first()
        if request.get_json():
            data = request.get_json()
            order = Order.query.filter_by(oid=data['oid']).first()
            order_dic = get_model_dict(order)
            del order_dic['uid']
            del order_dic['date']
            del order_dic['delivery_by']
            del order_dic['address_id']
            new_Address = order.address_id.split(',')
            order_dic['phone'] = new_Address[0]
            order_dic['name'] = new_Address[1]
            order_dic['address1'] = new_Address[2]
            order_dic['address2'] = new_Address[3]
            order_dic['city'] = new_Address[4]
            order_dic['state'] = new_Address[5].split('-')[0]
            order_dic['pin_code'] = new_Address[5].split('-')[1]
            order_dic['date'] = str(order.date)
            dics_products = []
            for product in order.products:
                new_products = get_model_dict(product)
                del new_products['mid']
                dics_products.append(new_products)
            order_dic['products'] = dics_products
            return {"Success": True, "order": order_dic}

        orders = user.orders
        all_orders = []
        for order in orders:
            order_dic = get_model_dict(order)
            del order_dic['uid']
            del order_dic['date']
            del order_dic['delivery_by']
            del order_dic['address_id']
            new_Address = order.address_id.split(',')
            order_dic['phone'] = new_Address[0]
            order_dic['name'] = new_Address[1]
            order_dic['address1'] = new_Address[2]
            order_dic['address2'] = new_Address[3]
            order_dic['city'] = new_Address[4]
            order_dic['state'] = new_Address[5].split('-')[0]
            order_dic['pin_code'] = new_Address[5].split('-')[1]
            order_dic['date'] = str(order.date)
            dics_products = []
            for product in order.products:
                new_products = get_model_dict(product)
                del new_products['mid']
                dics_products.append(new_products)
            order_dic['products'] = dics_products
            all_orders.append(order_dic)
        return {"Success": True, "Orders": all_orders}

    @auth.login_required()
    def post(self):
        data = request.get_json()
        print(data)
        date = datetime.now().date()
        payment_mode = data['payment_mode']
        token = data['token']
        total_price = 0
        address_id = data['address_id']
        products = data['products']


        if payment_mode != "COD":
            order_id = data['orderid']
            signature = data['signature']
            payment_id = data['payment_id']

            orderss = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            if client.utility.verify_payment_signature(orderss) == False:
                return {'success': False, 'error': "Invalid payment signature"}

        for product in products:
            total_price += int(product['price']) * int(product['quantity'])
        
        user = User.query.filter_by(uid=auth.current_user()).first()
        address = Address.query.filter_by(address_id=address_id).first()
        full_address = f"{address.telephone}, {address.name}, {address.address_1}, {address.address_2}, {address.city}, {address.state}-{address.pin_code}"
        if user:
            new_order = Order(
                uid=user.uid,
                date=date,
                total_price=total_price,
                address_id=full_address,
                status="Order Placed",
                token=token,
                payment_method=payment_mode
            )
            db.session.add(new_order)
            db.session.commit()
            if payment_mode != "COD":
                new_order.payment_id = data['orderid']
                new_order.order_id = data['orderid']
                db.session.commit()

            if 'coupon_id' in data:
                new_order.coupon_id = data['coupon_id']
                db.session.commit()
            products_ids = []
            for product in products:
                products_ids.append(product['product_id'])
            products_db = Product.query.filter(Product.product_id.in_(products_ids)).all()
            for product in products:
                for detail in products_db:
                    if detail.product_id == product['product_id']:
                        mid_order = mid_order_table(
                            oid=new_order.oid,
                            product_id=product['product_id'],
                            quantity=product['quantity'],
                            image_url=detail.image_urls,
                            product_name=detail.product_name,
                            quantity_init=detail.quantity,
                            price=int(product['price']) * int(product['quantity'])
                        )
                        db.session.add(mid_order)
                        db.session.commit()
            return {'success': True, 'order_id': new_order.oid}
        else:
            return {'success': False}


class CancelOrder(Resource):

    @auth.login_required()
    def get(self):
        orders = Order.query.filter(Order.status == "canceled").all()
        all_orders = []
        for order in orders:
            all_orders.append(get_model_dict(order))
        return {"Success": True, "orders": all_orders}

    @auth.login_required()
    def post(self):
        data = request.get_json()
        oid = data['oid']
        status = "Canceled"
        order = Order.query.filter_by(oid=oid).first()
        if order:
            order.status = status
            db.session.commit()
            return {"Success": True, "message": "Order canceled"}
        else:
            return {"Success": False, "message": "Order not found"}


api.add_resource(Wishlist, "/profile/wishlist")
api.add_resource(CartAPI, "/profile/cart")
api.add_resource(OrderAPI, "/profile/order")
api.add_resource(CancelOrder, "/profile/cancel_order")
