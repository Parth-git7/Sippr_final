from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt

# Initialize Sippr money for new sessions
def init_sippr_money(request):
    if 'sippr_money' not in request.session:
        request.session['sippr_money'] = 5000

# Home / Bookstore view
def bookstore(request):
    init_sippr_money(request)
    books = [
        "Hyperfocus", "Ratan Tata", "Harry Potter and the Philosopher's Stone",
        "Winterling", "The Lord of Rings", "The Monk who sold his Ferrari",
        "Bhagwad Gita", "Ghosts of the Silent hills", "Start living again",
        "Elon Musk", "Deep Work", "It ends with us"
    ]
    return render(request, 'bookstore.html', {'books': books})

def fiction(request):
    return render(request, 'fiction.html')

def nonfiction(request):
    return render(request, 'nonfiction.html')

def horror(request):
    return render(request, 'horror.html')

def religious(request):
    return render(request, 'religious.html')

def romance(request):
    return render(request, 'romance.html')

def selfhelp(request):
    return render(request, 'selfhelp.html')

def sellbooks(request):
    return render(request, 'sellbooks.html')

def subscriptions(request):
    return render(request, 'subscriptions.html')

def index(request):
    return render(request, 'index.html')

def toonify(request):
    if request.session.get('username'):
        return render(request, 'toonify.html')
    return redirect('signin')

@csrf_exempt
def submit_book(request):
    if request.method == 'POST':
        # Handle form submission here
        return HttpResponse("Book submitted!")

def payments(request):
    cart = request.session.get('cart', [])
    total_price = sum(float(item['price']) for item in cart)
    remaining_balance = request.session.get('sippr_money', 5000)

    if request.method == 'POST':
        if remaining_balance >= total_price:
            request.session['sippr_money'] -= total_price
            request.session['cart'] = []
            request.session.modified = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Not enough Sippr money.'})

    return render(request, 'payments.html', {
        'total_price': total_price,
        'remaining_balance': remaining_balance
    })

def cart(request):
    cart_items = request.session.get('cart', [])
    total_price = sum(float(item['price']) for item in cart_items)
    return render(request, 'cart.html', {'cart': cart_items, 'total_price': total_price})

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        title = request.POST.get('title')
        price = request.POST.get('price')
        image = request.POST.get('image')

        if not all([book_id, title, price, image]):
            return JsonResponse({"error": "Missing data"}, status=400)

        cart = request.session.get('cart', [])
        cart.append({"id": book_id, "title": title, "price": price, "image": image})
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({"message": "Item added to cart!", "cart": cart})

def remove_from_cart(request, book_id):
    cart = request.session.get('cart', [])
    cart = [item for item in cart if int(item['id']) != book_id]
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')

@csrf_exempt
def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([name, email, password]):
            return HttpResponse("All fields are required!", status=400)

        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already registered!", status=400)

        hashed_pw = make_password(password)
        User.objects.create(name=name, email=email, password=hashed_pw)
        return redirect('signin')

    return render(request, 'signup.html')

@csrf_exempt
def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['username'] = user.name
                request.session.set_expiry(0)
                return redirect('bookstore')
            else:
                return HttpResponse("Invalid email or password!", status=401)
        except User.DoesNotExist:
            return HttpResponse("Invalid email or password!", status=401)

    return render(request, 'signin.html')

def logout_view(request):
    request.session.flush()
    return redirect('bookstore')
