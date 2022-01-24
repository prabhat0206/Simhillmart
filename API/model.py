from . import db

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    address = db.relationship('Address', backref='address',cascade="all, delete-orphan")
    cart = db.relationship('Cart', backref='cart',cascade="all, delete-orphan")
    wishlist = db.relationship('Product', backref='wishlist',cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='order_by', cascade="all, delete-orphan")
    coupons = db.relationship('Coupon', backref='redeemed', cascade="all, delete-orphan")


class Address(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
    name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    address_1 = db.Column(db.String, nullable=False)
    address_2 = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    telephone = db.Column(db.String)
    state = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)


# class Delivery(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     deliver_id = db.Column(db.String, unique=True)
#     orders = db.relationship('Order', backref='deliver')
    # deliver_status = db.Column(db.String)

class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey('product.product_id', ondelete="CASCADE"))
    quantity = db.Column(db.Integer, default=1)

class Order(db.Model):
    oid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    payment_id = db.Column(db.String)
    order_id = db.Column(db.String)
    address_id = db.Column(db.String, nullable=False)
    total_price = db.Column(db.Integer)
    status = db.Column(db.String, default="Order placed")
    products = db.relationship('mid_order_table', backref='ordered_products', cascade="all, delete-orphan")
    token = db.Column(db.String)
    payment_method = db.Column(db.String)
    coupon_id = db.Column(db.String)
    # delivery_by = db.Column(db.Integer, db.ForeignKey('delivery.id'))


class mid_order_table(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer)
    oid = db.Column(db.Integer, db.ForeignKey('order.oid'), nullable=False)
    quantity = db.Column(db.Integer)
    quantity_init = db.Column(db.String)


class Category(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    products = db.relationship('Product', backref='products', cascade="all, delete-orphan")
    name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)


class Brand(db.Model):
    bid = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    product = db.relationship('Product', backref='branding', cascade="all, delete-orphan")


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=True)
    product_name = db.Column(db.String, nullable=False)
    image_urls = db.Column(db.String, nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('category.cid'), nullable=False)
    brand = db.Column(db.Integer, db.ForeignKey('brand.bid'), nullable=False)
    isMostSelling = db.Column(db.Integer, default=0)
    isFeatured = db.Column(db.Integer, default=0)
    isTopSelling = db.Column(db.Integer, default=0)
    description = db.Column(db.String)
    actual_price = db.Column(db.String)
    sale_price = db.Column(db.Integer)
    in_stock = db.Column(db.Integer)
    quantity = db.Column(db.String)


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"))
    coupon_id = db.Column(db.String, unique=True)
    percentage = db.Column(db.String)
    valid_till = db.Column(db.Date)
    date = db.Column(db.Date)
