from django.shortcuts import render,redirect
from django.http import JsonResponse
from foodapp.models import Contact,Product,OrderUpdate,Order,Cart
from django.views import View
from . import models
from django.contrib import messages
from math import ceil
from .models import Order, OrderUpdate


# Create your views here.
def index(request):

   # allProds = []
    #catprods = Product.objects.values('category','id')
    #print(catprods)
   # cats = {item['category'] for item in catprods}
    #for cat in cats:
      #  prod= Product.objects.filter(category=cat)
      #  n=len(prod)
        #nSlides = n // 4 + ceil((n / 4) - (n // 4))
       # allProds.append([prod, range(1, nSlides), nSlides])

    #params= {'allProds':allProds}

    return render(request,"index.html") #,params


def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")



def cart_view(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    else:
        cart_items = Cart.objects.filter(user=request.user)
        total_amount = sum([item.total_price() for item in cart_items])

        return render(request, 'cart.html', {'cart_items': cart_items, 'total_amount': total_amount})



def checkout_view(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        if not address or not phone:
            messages.error(request, "Please fill in all the details.")
            return redirect('checkout')

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect('cart')

        # Create order
        order = Order.objects.create(user=request.user, address=address, phone=phone)
        order.cart.set(cart_items)
        order.save()

        # Clear the cart after placing the order
        cart_items.delete()

        messages.success(request, "Your order has been placed!")
        return redirect('order_confirmation.html', order_id=order.id)

    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum([item.total_price() for item in cart_items])
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})


def order_details(request, order_id):
    try:
        # Fetch the order and its updates
        order = Order.objects.get(id=order_id, user=request.user)
        updates = OrderUpdate.objects.filter(order=order).order_by('-timestamp')
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('profile')

    return render(request, 'order_details.html', {'order': order, 'updates': updates})


def update_order_status(request, order_id):
    if request.method == 'POST':
        update_desc = request.POST.get('update_desc')
        order = Order.objects.get(id=order_id)

        # Create a new order update
        OrderUpdate.objects.create(order=order, update_desc=update_desc)

        messages.success(request, 'Order status updated successfully.')
        return redirect('order_details', order_id=order_id)




def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    # Use the current user object instead of username
    currentuser = request.user  
    items = Order.objects.filter(user=currentuser)  # Filter by user

    if not items.exists():
        messages.info(request, "No orders found for your account.")
        return render(request, "profile.html", {"items": items, "status": []})

    # Prepare to store order IDs and their statuses
    order_ids = []
    for order in items:
        print(order.oid)
        # Assuming oid is in the format "ShopyCart<id>"
        rid = order.oid.replace("ShopyCart", "")
        if rid.isdigit():  # Ensure it's a digit before converting
            order_ids.append(int(rid))

    # Fetch status for each order ID
    status = []
    if order_ids:
        status = OrderUpdate.objects.filter(order_id__in=order_ids)

    # Print the updates for debugging
    for update in status:
        print(update.update_desc)

    context = {"items": items, "status": status}
    return render(request, "profile.html", context)



def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity

        request.session['cart'] = cart
        return JsonResponse({'message': 'Item added to cart', 'cart_count': len(cart)})

    return JsonResponse({'error': 'Invalid request'}, status=400)