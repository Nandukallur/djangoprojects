from django.shortcuts import render,redirect
from shop.models import Product
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from cart.models import Cart,Account,Order
@login_required()
def cartview(request):
    total = 0
    user = request.user
    try:
        cart = Cart.objects.filter(user=user)
        for i in cart:
            total += i.quantity * i.product.price

    except Cart.DoesNotExist:
        pass
    return render(request,'cartview.html',{'cart':cart,'total':total})

@login_required()
def add_to_cart(request,p):
    p = Product.objects.get(id=p)
    user = request.user
    try:
        cart = Cart.objects.get(user=user, product=p)
        if(cart.quantity<cart.product.stock):
            cart.quantity+=1
        cart.save()
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=user,product=p,quantity=1)
        cart.save()

    return redirect('cart:cartview')

@login_required()
def cart_remove(request,p):
    p = Product.objects.get(id=p)
    user = request.user
    try:
        cart = Cart.objects.get(user=user, product=p)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
        else:
            cart.delete()
    except Cart.DoesNotExist:
        pass

    return redirect('cart:cartview')

@login_required()
def full_remove(request,p):
    p = Product.objects.get(id=p)
    user = request.user
    try:
        cart = Cart.objects.get(user=user, product=p)
        cart.delete()
    except Cart.DoesNotExist:
        pass

    return redirect('cart:cartview')

@login_required()
def orderform(request):
    total = 0
    if(request.method=="POST"):
        a = request.POST['a']
        p = request.POST['p']
        n = request.POST['n']
        user = request.user
        cart = Cart.objects.filter(user=user)
        for i in cart:
            total += i.quantity * i.product.price
        ac = Account.objects.get(acctnumber=n)
        if(ac.amount >= total):
            ac.amount = ac.amount - total
            ac.save()
            for i in cart:
                o = Order.objects.create(user=user,product=i.product,address=a,phone=p,order_status="Paid",no_of_items=i.quantity)
                o.save()
                i.product.stock = i.product.stock - i.quantity
                i.product.save()
            cart.delete()
            msg = "Order placed succesfully"
            return render(request,'orderdetail.html',{'msg':msg})
        else:
            msg = "Insufficient Amount.You cannot place Order"
            return render(request,'orderdetail.html',{'msg':msg})

    return render(request,'orderform.html')

@login_required()
def orderview(request):
    u = request.user
    o = Order.objects.filter(user=u,order_status="Paid")
    return render(request,'orderview.html',{'o':o,'u':u.username})
