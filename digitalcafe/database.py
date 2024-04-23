import pymongo

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

myclient = pymongo.MongoClient("mongodb+srv://WaldenKuo:jwb8vr5HAbWXai9N@digitalcafe.04etxbm.mongodb.net/?retryWrites=true&w=majority&appName=DigitalCafe")


products_db = myclient["products"]
order_management_db = myclient["order_management"]


def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def get_branch(code):
    branches_coll = products_db["branches"]
    branch = branches_coll.find_one({"code":code})
    return branch

def get_branches():
    branch_list = []
    branches_coll = products_db["branches"]
    for p in branches_coll.find({}):
        branch_list.append(p)
    return branch_list

def get_product(code):
    products_coll = products_db["products"]
    product = products_coll.find_one({"code":code},{"_id":0})
    return product

def get_products():
    product_list = []
    products_coll = products_db["products"]
    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)
    return product_list

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert_one(order)

def get_past_orders(username):
    orders_coll = order_management_db['orders']
    past_orders = list(orders_coll.find({'username': username}))
    return past_orders

def update_password(username, new_password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({'username': username}, {'$set': {'password': new_password}})
