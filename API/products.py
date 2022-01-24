from flask import Blueprint, request
from flask_restful import Api, Resource
from .model import *
from . import get_model_dict, auth
from sqlalchemy import or_
import random
from datetime import date


product_api = Blueprint('product', __name__)
api = Api(product_api)


class CategoryAPI(Resource):

    def get(self):
        categories = Category.query.all()
        all_categories = []
        for category in categories:
            all_categories.append(get_model_dict(category))
        return {"Success": True, "Category": all_categories}


class CategoryProduct(Resource):

    def get(self, cid):
        category = Category.query.filter_by(cid=int(cid)).first()
        category_info = {}
        category_info['cid'] = category.cid
        category_info['name'] = category.name
        category_info['image'] = category.image_url
        products = []
        if len(category.products) > 0:
            for product in category.products:
                products.append(get_model_dict(product))
        category_info['products'] = products
        return {"Success": True, "Category": category_info}


class BrandAPI(Resource):

    def get(self):
        brands = Brand.query.all()
        all_brands = []
        for brand in brands:
            all_brands.append(get_model_dict(brand))
        return {"Success": True, "Brand": all_brands}

    def post(self):
        brand = Brand.query.filter_by(bid=int(request.get_json()['bid'])).first()
        brand_info = {}
        brand_info['name'] = brand.name
        brand_info['bid'] = brand.bid
        brand_info['image_url'] = brand.image_url
        products = []
        if len(brand.product) > 0:
            for product in brand.product:
                products.append(get_model_dict(product))
        brand_info['products'] = products
        return {"Success": True, "Brand": brand_info}



class ProductAPI(Resource):
    def get(self):
        products = Product.query.all()
        trending = []
        most_selling = []
        in_offer = []
        all_other = []
        for product in products:
            serlized_product = get_model_dict(product)
            del serlized_product['uid']
            del serlized_product['isFeatured']
            serlized_product['inOffer'] = product.isFeatured
            if product.isMostSelling == 1:
                most_selling.append(serlized_product)
            if product.isTopSelling == 1:
                trending.append(serlized_product)
            if product.isFeatured == 1:
                in_offer.append(serlized_product)
            all_other.append(serlized_product)
        
        random.shuffle(most_selling)
        random.shuffle(trending)
        random.shuffle(all_other)
        return {"Success": True, "in_offer": in_offer, "trending": trending, "best_deal": most_selling, "all_others": all_other}



class ProductDetailsAPi(Resource):

    def get(self, product_id):
        product = Product.query.filter_by(product_id=int(product_id)).first()
        brand = Brand.query.filter_by(bid=product.brand).first()
        category = Category.query.filter_by(cid=product.category).first()
        serlized_product = get_model_dict(product)
        del serlized_product['uid']
        serlized_product['brand'] = {
            "name": brand.name,
            "image_url": brand.image_url,
        }
        serlized_product['category'] = {
            "name": category.name,
            "image_url": category.image_url,
        }
        return {"Success": True, "Product": serlized_product}



class SearchProduct(Resource):

    def get(self, word):
        products = Product.query.filter(or_(
            Product.product_name.contains(word), 
            Product.description.contains(word), 
            Product.actual_price.contains(word)
        )).all()

        all_products = []
        for product in products:
            new_Product = get_model_dict(product)
            del new_Product['uid']
            all_products.append(new_Product)
        
        return {"Success": True, "Product": all_products}
        

class CouponAPI(Resource):

    @auth.login_required()
    def get(self, coupon_id):
        user = User.query.filter_by(uid=auth.current_user()).first()
        coupon = Coupon.query.filter_by(coupon_id=coupon_id).first()
        if coupon and user:
            if coupon in user.coupons:
                return {"Success": False, "error": "Coupon already redeemed"}
            new_Coupon = get_model_dict(coupon)
            del new_Coupon['uid'], new_Coupon['date'], new_Coupon['valid_till']
            new_Coupon['date'] = str(coupon.date)
            new_Coupon['valid_till'] = str(coupon.valid_till)
            return {"Success": True, "coupon": new_Coupon}
        else:
            return {"Success": False, "error": "Coupon not found"}
    

class CouponsAPI(Resource):
    @auth.login_required()
    def get(self):
        coupons = Coupon.query.order_by(Coupon.id.desc()).all()
        user = User.query.filter_by(uid=auth.current_user()).first()
        all_valid = []
        all_expired = []
        all_redeemed = []
        if user:
            for coupon in coupons:
                if coupon.valid_till > date.today():
                    if coupon in user.coupons:
                        new_Coupon = get_model_dict(coupon)
                        del new_Coupon['uid'], new_Coupon['date'], new_Coupon['valid_till']
                        new_Coupon['date'] = str(coupon.date)
                        new_Coupon['valid_till'] = str(coupon.valid_till)
                        all_valid.append(new_Coupon)
                    else:
                        new_Coupon = get_model_dict(coupon)
                        del new_Coupon['uid'], new_Coupon['date'], new_Coupon['valid_till']
                        new_Coupon['date'] = str(coupon.date)
                        new_Coupon['valid_till'] = str(coupon.valid_till)
                        all_redeemed.append(new_Coupon)
                else:
                    new_Coupon = get_model_dict(coupon)
                    del new_Coupon['uid'], new_Coupon['date'], new_Coupon['valid_till']
                    new_Coupon['date'] = str(coupon.date)
                    new_Coupon['valid_till'] = str(coupon.valid_till)
                    all_expired.append(new_Coupon)
            
            return {"Success": True, "coupons": {
                "valid": all_valid,
                "expired": all_expired,
                "redeemed": all_redeemed
            }}
        else:
            return {"Success": False, "error": "not found"}

        


api.add_resource(CategoryAPI, '/categories')
api.add_resource(CategoryProduct, '/category/<cid>')
api.add_resource(BrandAPI, '/brand')
api.add_resource(ProductAPI, '/product')
api.add_resource(SearchProduct, '/search/<word>')
api.add_resource(ProductDetailsAPi, "/product/<product_id>")
api.add_resource(CouponAPI, '/coupon/<coupon_id>')
api.add_resource(CouponsAPI, '/coupons')

