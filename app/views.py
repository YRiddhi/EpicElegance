from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from .models import Product, Cart, Order
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
import random
from django.conf import settings
from django.core.mail import send_mail

# Create your views here.
def index(request):
    allproducts=Product.objects.all()
    context={"allproducts": allproducts}
    return render(request, 'index.html', context)

class ProductRegister(CreateView):
    model=Product
    fields="__all__"
    success_url="/"

class ProductList(ListView):
    model=Product

class ProductRemove(DeleteView):
    model=Product
    success_url="/ProductList"

class ProductUpdate(UpdateView):
    model=Product
    template_name_suffix="_update_form"
    fields="__all__"
    success_url="/ProductList"

def signup(req):
    if req.method == "POST":
        uname = req.POST["uname"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        context = {}
        if uname == "" or upass == "" or ucpass == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "signup.html", context)
        elif upass != ucpass:
            context["errmsg"] = "Password and confirm password doesn't match"
            return render(req, "signup.html", context)
        else:
            try:
                userdata = User.objects.create(username=uname, password=upass)
                userdata.set_password(upass)
                userdata.save()
                return redirect("/signin")
            except:
                context["errmsg"] = "User Already exists"
                return render(req, "signup.html", context)
    else:
        context = {}
        context["errmsg"] = ""
        return render(req, "signup.html", context)

def signin(req):
    if req.method == "POST":
        uname = req.POST["uname"]
        upass = req.POST["upass"]
        context = {}
        if uname == "" or upass == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "signin.html", context)
        else:
            userdata = authenticate(username=uname, password=upass)
            if userdata is not None:
                login(req, userdata)
                return redirect("/")
            else:
                context["errmsg"] = "Invalid username and password"
                return render(req, "signin.html", context)
    else:
        return render(req, "signin.html")
    
def userlogout(req):
    logout(req)
    return redirect("/")

def mobileslist(req):
    if req.method=="GET":
        allproducts=Product.product_manager.mobiles_list()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    else:
        allproducts=Product.objects.all()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)

def clotheslist(req):
    if req.method=="GET":
        allproducts=Product.product_manager.clothes_list()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    else:
        allproducts=Product.objects.all()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    
def shoeslist(req):
    if req.method=="GET":
        allproducts=Product.product_manager.shoes_list()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    else:
        allproducts=Product.objects.all()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    
def electronicslist(req):
    if req.method=="GET":
        allproducts=Product.product_manager.electronics_list()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    else:
        allproducts=Product.objects.all()
        context={"allproducts": allproducts}
        return render(req, "index.html", context)
    
def showpricerange(req):
    if req.method=="GET":
        return render(req, "index.html")
    else:
        r1=req.POST.get("min")
        r2=req.POST.get("max")
        if r1 is not None and r2 is not None and r1.isdigit() and r2.isdigit():
            allproducts=Product.product_manager.pricerange(r1, r2)
            context={"allproducts": allproducts}
            return render(req, "index.html", context)
        else:
            allproducts=Product.objects.all()
            context={"allproducts": allproducts}
            return render(req, "index.html", context)
        
def sortproducts(req):
    sortoption=req.GET.get("sort")
    if sortoption=="low to high":
        allproducts=Product.objects.order_by("price")       # asc order
    elif sortoption=="high to low":
        allproducts=Product.objects.order_by("-price")       # asc order
    else:
        allproducts=Product.objects.all()
    context={"allproducts": allproducts}
    return render(req, "index.html", context)

def searchproducts(req):
    query=req.GET.get("q")
    errmsg=""
    if query:
        allproducts=Product.objects.filter(
            Q(productname__icontains=query)|
            Q(category__icontains=query)|
            Q(description__icontains=query)|
            Q(price__icontains=query)
        )
        if len(allproducts)==0:
            errmsg="No result found"
    else:
        allproducts=Product.objects.all()
    context={"allproducts": allproducts, "query":query, "errmsg":errmsg}
    return render(req, "index.html", context)

def show_cart(req):
    user=req.user
    allcarts=Cart.objects.filter(userid=user.id)
    totalamt=0
    for x in allcarts:
        totalamt+=x.productid.price*x.qty
    totalitems=len(allcarts)
    if req.user.is_authenticated:
        context={"allcarts": allcarts, "username": user, "totalamt": totalamt, "totalitems": totalitems}
    else:
        context={"allcarts": allcarts}
    return render(req, 'showcart.html', context)

def addcart(req, productid):
    if req.user.is_authenticated:
        user=req.user
    else:
        user=None
    allproducts=get_object_or_404(Product, productid=productid)
    cartitem, created=Cart.objects.get_or_create(productid=allproducts, userid=user)
    if not created:
        cartitem.qty+=1
    else:
        cartitem.qty=1
    cartitem.save()
    return redirect("/show_cart")

def removecart(req, productid):
    user=req.user
    cartitem=Cart.objects.get(productid=productid, userid=user.id)
    cartitem.delete()
    return redirect("/show_cart")

def updateqty(req, qv, productid):
    allcarts=Cart.objects.filter(productid=productid)
    if qv==1:
        total=allcarts[0].qty+1
        allcarts.update(qty=total)
    else:
        if allcarts[0].qty>1:
            total=allcarts[0].qty-1
            allcarts.update(qty=total)
        else:
            allcarts=Cart.objects.filter(productid=productid)
            allcarts.delete()
    return redirect("/show_cart")

def payment(req):
    if req.user.is_authenticated:
        user=req.user
        allcarts=Cart.objects.filter(userid=user.id)
        totalamt=0
        for x in allcarts:
            orderid=random.randrange(1000, 8000)
            orderdata=Order.objects.create(orderid=orderid, productid=x.productid, qty=x.qty, userid=x.userid)
            totalamt+=totalamt+x.qty*x.productid.price
            orderdata.save()
            x.delete()
        subject=f"EpicElegance-Payment Status for your order={orderid}"
        message=f"Hello {user}, Thank you for using our servive.\n Total Amount Paid:Rs.{totalamt}/-"
        emailfrom=settings.EMAIL_HOST_USER
        receiver=[user, user.email]
        send_mail(subject, message, emailfrom, receiver)
        return render(req, "payment.html")
    else:
        return redirect("/signin")