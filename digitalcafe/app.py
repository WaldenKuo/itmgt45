from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import ordermanagement as om
import logging

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)
    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    if session.get("cart") is None:
        session["cart"] = {}

    cart = session["cart"]
    if code in cart:
        cart[code]["qty"] += 1  
        cart[code]["subtotal"] = cart[code]["qty"] * product["price"]  
    else:
        item = {
            "qty": 1,
            "name": product["name"],
            "subtotal": product["price"]  
        }
        cart[code] = item 
    session["cart"] = cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods=['POST'])
def update_cart():
    if 'cart' not in session or not session['cart']:
        return redirect('/cart')  
    cart = session['cart']
    total_price = 0 
    for code, item in cart.items():
        qty_key = 'qty_' + str(code)
        if qty_key in request.form:
            new_qty = int(request.form[qty_key])
            if new_qty >= 1:
                item['qty'] = new_qty
                product = db.get_product(int(code))
                item['subtotal'] = product['price'] * new_qty  
                total_price += item['subtotal']  
    session['cart'] = cart  
    session['total_price'] = total_price  
    return redirect('/cart')  

@app.route('/removefromcart', methods=['GET', 'POST'])
def remove_from_cart():
    if 'cart' not in session or not session['cart']:
        return redirect('/cart')
    cart = session['cart']
    code_to_remove = request.args.get('code')
    if code_to_remove in cart:
        del cart[code_to_remove]
    session['cart'] = cart
    if not cart:
        session.pop('cart', None)
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches') 
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/pastorders')
def past_orders():
    if 'user' not in session:
        return redirect('/login')
    past_orders = db.get_past_orders(session['user']['username'])
    return render_template('pastorders.html', past_orders=past_orders)

@app.route('/changepassword', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            error = "Please fill in all fields."
            return render_template('change_password.html', error=error)
        
        user = db.get_user(session['user']['username'])
        if user['password'] != old_password:
            error = "Old password is incorrect."
            return render_template('change_password.html', error=error)
        
        if new_password != confirm_password:
            error = "New password and confirm password do not match."
            return render_template('change_password.html', error=error)
        
        db.update_password(session['user']['username'], new_password)
        return redirect('/')

    return render_template('changepassword.html')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response(dumps(db.get_products()))
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp
