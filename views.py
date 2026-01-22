from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import Flower, Order, Profile, Cart


# ===================== LOGIN =====================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "shop/login.html")


# ===================== LOGOUT =====================
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("home")


# ===================== HOME =====================
@login_required(login_url="login")
def home(request):
    return render(request, "shop/home.html")


# ===================== PRODUCTS =====================
@login_required(login_url="login")
def flowers(request):
    flowers = Flower.objects.filter(category="flower")
    return render(request, "shop/flowers.html", {"flowers": flowers})


@login_required(login_url="login")
def shopplants(request):
    flowers = Flower.objects.filter(category="shopplant")
    return render(request, "shop/shopplants.html", {"flowers": flowers})


@login_required(login_url="login")
def weddings(request):
    flowers = Flower.objects.filter(category="wedding")
    return render(request, "shop/weddings.html", {"flowers": flowers})


@login_required(login_url="login")
def workshop(request):
    flowers = Flower.objects.filter(category="workshop")
    return render(request, "shop/workshop.html", {"flowers": flowers})

@login_required
def map(request):
    return render(request, "shop/map.html")

@login_required
def contact(request):
    return render(request, "shop/contact.html")


# ===================== REGISTER =====================
def register(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            password=request.POST.get("password"),
        )
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.save()

        Profile.objects.create(
            user=user,
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "shop/register.html")


# ===================== CART SYSTEM =====================
@login_required(login_url="login")
def add_to_cart(request, product_id):
    flower = get_object_or_404(Flower, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        flower=flower
    )

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()
    return redirect("cart")


@login_required(login_url="login")
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required(login_url="login")
def remove_from_cart(request, product_id):
    Cart.objects.filter(
        user=request.user,
        flower_id=product_id
    ).delete()

    return redirect("cart")


# ===================== CHECKOUT =====================
@login_required(login_url="login")
def checkout(request):

    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")

        # ❌ nothing selected
        if not selected_items:
            messages.warning(request, "Please select at least one item to checkout.")
            return redirect("cart")

        # ✅ save selected ids in session
        request.session["selected_cart_items"] = selected_items

        return redirect("payment")

    # safety fallback
    return redirect("cart")

# ===================== BUY NOW =====================
@login_required(login_url="login")
def buy_now(request, flower_id):
    Cart.objects.filter(user=request.user).delete()
    Cart.objects.create(user=request.user, flower_id=flower_id, quantity=1)
    return redirect("checkout")   # 🔥 FIXED FLOW


# ===================== PAYMENT =====================
@login_required(login_url="login")
def payment(request):

    selected_ids = request.session.get("selected_cart_items")

    if not selected_ids:
        messages.warning(request, "Please select items first.")
        return redirect("cart")

    cart_items = Cart.objects.filter(
        user=request.user,
        id__in=selected_ids
    )

    if not cart_items.exists():
        messages.warning(request, "Selected items not found.")
        return redirect("cart")

    total = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        order_type = request.POST.get("order_type")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        orders = []

        # ✅ save only selected items
        for item in cart_items:
            order = Order.objects.create(
                user=request.user,
                flower=item.flower,
                quantity=item.quantity,
                customer_name=name,
                phone=phone,
                email=email,
                address=address,
                order_type=order_type,
                payment_method=payment_method,
            )
            orders.append(order)

        # ✅ delete only paid items
        cart_items.delete()

        # ✅ store last order ids for success page
        request.session["last_orders"] = [o.id for o in orders]

        # ✅ clear selected cart session
        del request.session["selected_cart_items"]

        return redirect("payment_success")

    return render(request, "shop/payment.html", {
        "cart_items": cart_items,
        "total": total
    })

@login_required(login_url="login")
def payment_success(request):
    order_ids = request.session.get("last_orders", [])
    orders = Order.objects.filter(id__in=order_ids)

    return render(request, "shop/payment_success.html", {
        "orders": orders
    })

# ===================== ORDERS =====================
@login_required(login_url="login")
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    return render(request, "shop/orders.html", {"orders": orders})
