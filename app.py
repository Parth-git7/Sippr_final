from flask import Flask, render_template, request, redirect, session, jsonify , url_for, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session handling
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Create the database
with app.app_context():
    db.create_all()

from flask import Flask, render_template

# app = Flask(__name__)
# app.secret_key = 'asdfghjklzxcvbnm'  # Set the secret key here

@app.route('/')
def bookstore():
    books = [
        "Hyperfocus",
        "Ratan Tata",
        "Harry Potter and the Philosopher's Stone",
        "Winterling",
        "The Lord of Rings",
        "The Monk who sold his Ferrari",
        "Bhagwad Gita",
        "Ghosts of the Silent hills" ,
        "Start living again" ,
        "Elon Musk" , 
        "Deep Work" , 
        "It ends with us" 
    ]
    return render_template('bookstore.html', books=books)





@app.route('/fiction')
def fiction():
    return render_template('/fiction.html')

@app.route('/nonfiction')
def nonfiction():
    return render_template('nonfiction.html')

@app.route('/horror')
def horror():
    return render_template('horror.html')

@app.route('/religious')
def religious():
    return render_template('religious.html')

@app.route('/romance')
def romance():
    return render_template('romance.html')

@app.route('/selfhelp')
def selfhelp():
    return render_template('selfhelp.html')

@app.route('/sellbooks')
def sellbooks():
    return render_template('sellbooks.html')

@app.route('/subscriptions')
def subscriptions():
    return render_template('subscriptions.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/toonify')
def toonify():
    if 'username' in session:
        return render_template('toonify.html')
    else:
        # Optional: redirect to login or bookstore
        return redirect('/bookstore/login')



@app.route('/submit_book', methods=['POST'])
def submit_book():
    # handle your form data here
    return "Book submitted!"  # or redirect, or flash message


# Example for initializing Sippr money in session (if not already set)
@app.before_request
def before_request():
    if 'sippr_money' not in session:
        session['sippr_money'] = 5000  # Initial balance



@app.route('/payments', methods=['GET', 'POST'])
def payments():
    cart = session.get('cart', [])
    total_price = sum(float(item['price']) for item in cart)

    remaining_balance = session.get('sippr_money', 5000)

    if request.method == 'POST' and 'sippr_money' in request.form:
        if remaining_balance >= total_price:
            session['sippr_money'] -= total_price
            session['cart'] = []  # ✅ Clear the cart after payment
            session.modified = True
            flash('Payment successful!', 'success')
            return jsonify({'success': True})  # ✅ AJAX response for frontend
        else:
            return jsonify({'success': False, 'message': 'Not enough Sippr money.'})

    return render_template('payments.html', total_price=total_price, remaining_balance=remaining_balance)




# @app.route('/cart')
# def cart():
#     cart_items = session.get('cart', [])
#     return render_template('cart.html', cart=cart_items)
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(float(item['price']) for item in cart_items)
    return render_template('cart.html', cart=cart_items, total_price=total_price)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    book_id = request.form.get('book_id')
    title = request.form.get('title')
    price = request.form.get('price')
    image = request.form.get('image')

    if not all([book_id, title, price, image]):
        return jsonify({"error": "Missing data"}), 400

    cart = session.get('cart', [])
    cart.append({
        "id": book_id,
        "title": title,
        "price": price,
        "image": image
    })
    session['cart'] = cart
    session.modified = True

    return jsonify({"message": "Item added to cart!", "cart": cart})

@app.route('/remove_from_cart/<int:book_id>', methods=['GET'])
def remove_from_cart(book_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if int(item['id']) != book_id]
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.name 
            session.permanent = True 
            return redirect('/')
        else:
            return "Invalid email or password!", 401

    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            return "All fields are required!", 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered!", 400

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/signin')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
