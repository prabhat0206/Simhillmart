from flask import Blueprint, request, abort
from flask_restful import Resource, Api
from functools import wraps
from werkzeug.http import parse_authorization_header
from .model import Order, Product, Category, Brand, User, Coupon
from . import get_model_dict, db
from datetime import datetime, timedelta
from .config import ADMIN_EMAIL, ADMIN_PASSWORD

admin = Blueprint('admin', __name__)
api = Api(admin)


def admin_required(next):
    @wraps(next)
    def check_admin(*args, **kwargs):
        if request.headers.get('Authorization'):
            credentails = parse_authorization_header(
                request.headers.get('Authorization')
            )
            if credentails.password and credentails.username is not None:
                if credentails.username == ADMIN_EMAIL and credentails.password == ADMIN_PASSWORD:
                    return next(*args, **kwargs)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)
    return check_admin


class ChangeCondition(Resource):
    def post(self):
        data = request.args
        product = Product.query.filter_by(product_id=int(data['product_id'])).first()
        if 'is_most_sell' in data:
            product.isMostSelling = int(data.get('is_most_sell'))
        if 'is_top_sell' in data:
            product.isTopSelling = int(data.get('is_top_sell'))
        if 'is_featured' in data:
            product.isFeatured = int(data.get('is_featured'))
        
        db.session.commit()

        return {"Success": True, "message": "Product updated successfully"}


class ProductHandler(Resource):

    @admin_required
    def get(self):
        if 'product_id' in request.args:
            product = Product.query.filter_by(product_id=int(request.args['product_id'])).first()
            new_product = get_model_dict(product)
            del new_product['uid'], new_product['quantity']
            new_product['quantity_per_pack'] = product.quantity
            return {"Success": True, "Product": new_product}
        products = Product.query.order_by(Product.product_id.desc()).all()
        all_products = []
        for product in products:
            new_product = get_model_dict(product)
            del new_product['uid'], new_product['quantity']
            new_product['quantity_per_pack'] = product.quantity
            all_products.append(new_product)
        return {"Success": True, "products": all_products}
    
    @admin_required
    def post(self):
        try:
            data = request.get_json()
            name = data.get('product_name')
            image = data.get('image_urls')
            cid = data.get('cid')
            bid = data.get('bid')
            isMostSelling = int(data.get('is_most_sell'))
            isFeatured = int(data.get('is_featured'))
            isTopSelling = int(data.get('is_top_sell'))
            description = data.get('description')
            actual_price = data.get('actual_price')
            sale_price = int(data.get('sale_price'))
            in_stock = int(data.get('in_stock'))
            quantity = data.get('quantity_per_pack')
            category = Category.query.filter_by(cid=cid).first()

            if not category:
                return {"Success": False, "message": "Category not found"}

            brand = Brand.query.filter_by(bid=bid).first()
            if not brand:
                return {"Success": False, "message": "Brand not found"}
            
            new_Product = Product(
                product_name=name,
                image_urls=image,
                category=category.cid,
                brand=brand.bid,
                isMostSelling=isMostSelling,
                isFeatured=isFeatured,
                isTopSelling=isTopSelling,
                description=description,
                actual_price=actual_price,
                sale_price=sale_price,
                in_stock=in_stock,
                quantity=quantity
            )
            db.session.add(new_Product)
            db.session.commit()
            return {"Success": True, "message": "Product added successfully"}
        except Exception as error:
            return {"Success": False, "Error": error}

    @admin_required
    def delete(self):
        try:
            data = request.args
            product = Product.query.filter_by(product_id=int(data["product_id"])).first()
            db.session.delete(product)
            db.session.commit()
            return {"Success": False, "message": "Product deleted successfully"}
        except:
            return {"Success": False, "message": "Something went wrong"}
    
    @admin_required
    def put(self):
        try:
            data = request.get_json()
            name = data.get('product_name')
            cid = int(data.get('cid'))
            bid = int(data.get('bid'))
            description = data.get('description')
            actual_price = data.get('actual_price')
            sale_price = int(data.get('sale_price'))
            in_stock = int(data.get('in_stock'))
            quantity = data.get('quantity_per_pack')
            product_id = data.get('product_id')

            product = Product.query.filter_by(product_id=product_id).first()
            product.product_name = name
            product.cid = cid
            product.bid = bid
            product.description=description
            product.actual_price=actual_price
            product.sale_price=sale_price
            product.in_stock=in_stock
            product.quantity=quantity

            if "image_urls" in data:
                image = data['image_urls']
                product.image_urls = image
            db.session.commit()

            return {"Success": True, "message": "Product successfully updated"}
        except Exception as error:
            return {"Success": False, "Error": error}


class CategoryHandler(Resource):
    @admin_required
    def get(self):
        try:
            if request.args:
                category = Category.query.filter_by(cid=request.args['cid']).first()
                all_products = []
                for product in category.products:
                    new_product = get_model_dict(product)
                    del new_product['uid']
                    all_products.append(new_product)
                category = get_model_dict(category)
                category['products'] = all_products
                return {"Success": True, "Category": category}
            categories = Category.query.order_by(Category.cid.desc()).all()
            all_categories = []
            for category in categories:
                all_categories.append(get_model_dict(category))
            return {"Success": True, "categories": all_categories}
        except:
            return {"Success": False, "message": "Something went wrong"}

    @admin_required
    def post(self):
        try:
            data = request.get_json()
            name = data["name"]
            image = data['image_url']
            new_Category = Category(name=name, image_url=image)
            db.session.add(new_Category)
            db.session.commit()
            category = get_model_dict(new_Category)
            return {
                "Success": True, "category": category
            }
        except Exception as error:
            return {"Success": False, "message": error}

    @admin_required
    def delete(self):
        # try:
            cid = request.args.get('cid')
            category = Category.query.filter_by(cid=int(cid)).first()
            db.session.delete(category)
            db.session.commit()
            return {"Success": True, "message": "Category deleted successfully"}
        # except:
        #     return {"Success": False, "message": "Something went wrong"}

    @admin_required
    def put(self):
        try:
            data = request.get_json()
            name = data.get('name')
            category = Category.query.filter_by(cid=int(data.get('cid'))).first()
            category.name = name

            if 'image_url' in data:
                category.image_url =data['image_url']
            
            db.session.commit()

            return {"Success": True, "message": "Category updated successfully"}
        except:
            return {"Success": False, "message": "Something went wrong"}

class BrandHandler(Resource):
    @admin_required
    def get(self):
        try:
            if 'bid' in request.args:
                brand = Brand.query.filter_by(bid=int(request.args['bid'])).first()
                all_products = []
                for product in brand.product:
                    new_product = get_model_dict(product)
                    del new_product['uid']
                    all_products.append(new_product)
                brand = get_model_dict(product)
                brand['products'] = all_products
                return {"Success": True, "Brand": brand}

            brands = Brand.query.order_by(Brand.bid.desc()).all()
            all_brands = []
            for brand in brands:
                all_brands.append(get_model_dict(brand))
            return {"Success": True, "brands": all_brands}
        except:
            return {"Success": False, "message": "Something went wrong"}

    @admin_required
    def post(self):
        try:
            data = request.get_json()
            name = data.get('name')
            image = data['image_url']
            new_Brand = Brand(name=name, image_url=image)
            db.session.add(new_Brand)
            db.session.commit()
            return {"Success": True, "Brand": get_model_dict(new_Brand)}
        except Exception as error:
            return {"Success": False, "message": error}

    @admin_required
    def delete(self):
        try:
            data = request.args
            brand = Brand.query.filter_by(bid=int(data["bid"])).first()
            db.session.delete(brand)
            db.session.commit()
            return {"Success": True, "message": "Brand deleted successfully"}
        except:
            return {"Success": False, "message": "Something went wrong"}

    @admin_required
    def put(self):
        try:
            data = request.get_json()
            name = data["name"]
            brand = Brand.query.filter_by(bid=int(data["bid"])).first()
            brand.name = name

            if "image_url" in request.files:
                brand.image_url = data['image_url']

            db.session.commit()
            return {"Success": True, "message": "Brand updated successfully"}
        except:
            return {"Success": False, "message": "Something went wrong"}


class OrderHandler(Resource):
    
    @admin_required
    def get(self):
        if request.args:
            order = Order.query.filter_by(oid=request.args["oid"]).first()
            new_Order = get_model_dict(order)
            del new_Order['date']
            del new_Order['address_id']
            all_products = []
            new_Order['date'] = str(order.date)
            for product in order.products:
                ordered = get_model_dict(product)
                del ordered['mid']
                del ordered['quantity_init']
                ordered['quantity_per_pack'] = product.quantity_init
                all_products.append(ordered)
            addresses = order.address_id.split(',')
            new_Order['products'] = all_products
            new_Order['telephone'] = addresses[0]
            new_Order['address'] = ""
            for data in addresses[1:]:
                new_Order['address'] += data
            return {"Success": True, "order": new_Order}
        
        orders = Order.query.order_by(Order.oid.desc()).all()
        all_orders = []
        for order in orders:
            new_Order = get_model_dict(order)
            del new_Order['date']
            del new_Order['address_id']
            new_Order['date'] = str(order.date)
            all_products = []
            for product in order.products:
                ordered = get_model_dict(product)
                del ordered['mid']
                del ordered['quantity_init']
                ordered['quantity_per_pack'] = product.quantity_init
                all_products.append(ordered)
            addresses = order.address_id.split(',')
            new_Order['products'] = all_products
            new_Order['telephone'] = addresses[0]
            new_Order['address'] = ""
            for data in addresses[1:]:
                new_Order['address'] += data
            all_orders.append(new_Order)
        return {"Success": True, "Orders": all_orders}
    
    @admin_required
    def post(self):
        try:
            data = request.args
            status = data["status"]
            order = Order.query.filter_by(oid=int(data['oid'])).first()
            order.status = status
            db.session.commit()
            return {"Success": True, "message": "Order status updated successfully"}
        except Exception as error:
            return {"Success": False, "message": error}    


class UserHandler(Resource):

    @admin_required
    def get(self):
        users = User.query.all()
        all_users = []
        for user in users:
            user_dic = get_model_dict(user)
            all_users.append(user_dic)
        return {"Success": True, "users": all_users}


class Statistics(Resource):

    @admin_required
    def get(self):
        orders = Order.query.all()
        products = Product.query.all()
        users = User.query.all()
        total_earnings = 0
        total_pending_payment = 0
        total_orders_delivered = 0
        total_product_in_proccess = 0
        total_product_canceled = 0
        total_product_on_sale = len(products)

        for order in orders:
            if order.status == "delivered":
                total_earnings += int(order.total_price)
                total_orders_delivered += 1
            elif order.status == "canceled":
                total_product_canceled += 1
            else:
                total_pending_payment += int(order.total_price)
                total_product_in_proccess += 1

        statics = {
            "total_users": len(users),
            "total_earnings": total_earnings,
            "total_pending_payment": total_pending_payment,
            "total_orders_delivered": total_orders_delivered,
            "total_product_in_proccess": total_product_in_proccess,
            "total_product_canceled": total_product_canceled,
            "total_product_on_sale": total_product_on_sale
        }

        return statics


class GetOrderbyStatus(Resource):
    
    @admin_required
    def get(self, status):
        orders = Order.query.filter(Order.status == status).all()
        all_orders = []
        for order in orders:
            new_Order = get_model_dict(order)
            del new_Order['date']
            del new_Order['address_id']
            new_Order['date'] = str(order.date)
            all_products = []
            for product in order.products:
                all_products.append({
                    "product_name": product.product_name,
                    "quantity": product.quantity,
                    "price": product.price,
                    "weight": product.quantity,
                    "image_url": product.image_url,
                    "product_id": product.product_id,
                    "quantity_per_pack": product.quantity_init,
                })
            new_Order['products'] = all_products
            new_Order['address'] = order.address_id
            all_orders.append(new_Order)
        return {"Success": True, "orders": all_orders}
        

class CouponAdmin(Resource):

    @admin_required
    def get(self):
        if 'coupon_id' in request.args:
            coupon = Coupon.query.filter_by(coupon_id=request.args['coupon_id']).first()
            new_Coupon = get_model_dict(coupon)
            del new_Coupon['uid'], new_Coupon['date'], new_Coupon['valid_till']
            new_Coupon['date'] = str(coupon.date)
            new_Coupon['valid_till'] = str(coupon.valid_till)
            return {"Success": True, "Coupon": new_Coupon}

        coupons = Coupon.query.order_by(Coupon.id.desc()).all()
        all_coupons = []
        for coupon in coupons:
            new_Coupon = get_model_dict(coupon)
            del new_Coupon['uid'], new_Coupon['date'], new_Coupon['valid_till']
            new_Coupon['date'] = str(coupon.date)
            new_Coupon['valid_till'] = str(coupon.valid_till)
            all_coupons.append(new_Coupon)
        return {"Success": True, "Coupons": all_coupons}

    @admin_required
    def post(self):

        data = request.get_json()
        valid_days = timedelta(days=int(data['valid_till']))
        date = datetime.now()
        new_Coupon = Coupon(coupon_id=data['coupon_id'], percentage=data['percentage'], valid_till= date + valid_days, date=date)
        db.session.add(new_Coupon)
        db.session.commit()
        return {"Success": True}

    @admin_required
    def delete(self):
        coupon = Coupon.query.filter_by(coupon_id=request.args['coupon_id']).first()
        db.session.delete(coupon)
        db.session.commit()
        return {"Success": True}


api.add_resource(ProductHandler, '/product', endpoint="product")
api.add_resource(CategoryHandler, '/category', endpoint="category")
api.add_resource(BrandHandler, '/brand', endpoint="brand")
api.add_resource(OrderHandler, '/order', endpoint="order")
api.add_resource(UserHandler, '/users', endpoint="users")
api.add_resource(Statistics, '/statistics', endpoint="statistics")
api.add_resource(ChangeCondition, '/change_condition', endpoint="change_condition")
api.add_resource(CouponAdmin, '/coupons', endpoint="coupons")
api.add_resource(GetOrderbyStatus, '/get_order_by_status/<status>', endpoint="get_order_by")
