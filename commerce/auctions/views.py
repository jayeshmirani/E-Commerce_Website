from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from .models import User,Category,Listing,Bid,Comment,Watchlist

class NewComment(forms.Form):
    comment= forms.CharField(label="Add a comment", widget= forms.Textarea())

class NewBid(forms.Form):
    bid= forms.IntegerField(label="Your Bid in $")

def category_choices():
    categories= Category.objects.all()
    names=[('No Category Listed','')]
    for cat in categories:
        name=cat.category_name
        names.append((name,name))
    return names

class NewListing(forms.Form):
    title= forms.CharField(label="Title")
    description= forms.CharField(label="Description", widget=forms.Textarea())
    starting_bid= forms.IntegerField(label="Starting Bid(in $)", min_value=1)
    image_url= forms.URLField(label="URL for any image on the listing", required=False)
    names=category_choices()
    #print(categories)
    #category= forms.CharField(label="Category", widget=forms.Select(choices=names), required=False)
    category= forms.ChoiceField(label="Category",choices= names, required=False)

class NewCategory(forms.Form):
    name= forms.CharField(label="Category Name")

def index(request):
    listings= Listing.objects.all()
    if not listings:
        return render(request,"auctions/index.html",{
            "heading":"Active Listings",
            "footer_msg": "Sorry, No active listings available." 
        })
    active_listings=[]
    for i in range(len(listings)):
        active_listings.append((listings[i],Bid.objects.get(listing_id= listings[i].id)))
    return render(request, "auctions/index.html" ,{
        "heading":"Active Listings",
        "active_listings":active_listings
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "username": username,
                "password" : password
            })
    else:
        return render(request, "auctions/login.html")

@login_required(login_url = "/login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation or len(password)<8:
            message=""
            if(len(password)<8):
                message="Password must be at least 8 characters long."
            else:
                message="Passwords must match."
            return render(request, "auctions/register.html", {
                "message": message,
                "username": username,
                "email" : email,
                "password" : password,
                "confirmation" : confirmation
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken. Please use a different username.",
                "username": username,
                "email" : email,
                "password" : password,
                "confirmation" : confirmation
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url = "/login")
def new_category(request):
    if request.method=="POST":
        categories= Category.objects.all()
        form = NewCategory(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            name = data["name"]
            for category in categories:
                if name == category.category_name:
                    return render(request,"auctions/new_category.html",{
                        "message":"Category with this name already exists!",
                        "new_cat_form":NewCategory(data)
                    })
            cat = Category(category_name=name)
            cat.save()
            return render(request,"auctions/categories.html",{
                    "message":"New Category added successfully!",
                    "categories":Category.objects.all()
                })
    return render(request,"auctions/new_category.html",{
        "new_cat_form":NewCategory()
    })

@login_required(login_url = "/login")
def categories(request):
    return render(request,"auctions/categories.html",{
        "categories": Category.objects.all()
    })

@login_required(login_url = "/login")
def category_items(request,category_name):
    listings= Listing.objects.filter(category= category_name)
    if not listings:
        return render(request,"auctions/index.html",{
        "heading":category_name,
        "footer_msg": "Sorry, No active listings available." 
        })
    active_listings=[]
    for i in range(len(listings)):
        active_listings.append((listings[i],Bid.objects.get(listing_id= listings[i].id)))
    return render(request, "auctions/index.html" ,{
        "active_listings":active_listings,
        "heading": category_name
    })

@login_required(login_url = "/login")
def create_listing(request):
    if request.method=="POST":
        form = NewListing(request.POST)
        if form.is_valid():
            data= form.cleaned_data
            listings = Listing.objects.all()
            for listing in listings:
                if data["title"] == listing.title:
                    return render(request,"auctions/create_listing.html",
                    {
                        "message":"A listing with this title already exists. Choose a different one.",
                        "newlisting_form":NewListing(data)    
                    })
            if(data["image_url"] == ""):
                data["image_url"] = "https://commercial.bunn.com/img/image-not-available.png"
            listing=Listing(title=data["title"], description=data["description"], category= data["category"], username=request.user.username, image_url=data["image_url"]) 
            listing.save()
            bid= Bid(listing_id= listing.id, current_bid=data["starting_bid"], bid_count=1, highest_bidder= request.user.username)
            bid.save()
            # if data["image_url"]:
            #     Listing.image_url.add(data["image_url"])
            return HttpResponseRedirect(reverse('index'))
    return render(request,"auctions/create_listing.html",{
        "newlisting_form": NewListing()
    })


@login_required(login_url = "/login")
def listing(request, id):
    listing = Listing.objects.get(id=id)
    bid= Bid.objects.get(listing_id = id)
    comments= listing.comments.all()
    #comments= Comment.objects.filter(listing_id=id)
    watchlist= Watchlist.objects.filter(username= request.user.username)
    in_watchlist=False
    for item in watchlist:
        if item.listing_id == id:
            in_watchlist=True
            break
    # for comment_obj in comment_objects:
    #     comments.append((comment_obj.username,comment_obj.comment))
    if request.method=="POST":
        form = NewBid(request.POST)
        if form.is_valid():
            new_bid= form.cleaned_data["bid"]
            current_bid = bid.current_bid
            if new_bid <= current_bid and (bid.bid_count !=1 or new_bid < current_bid):
                return render(request,"auctions/listing.html",{
                    "listing":listing,
                    "bid":bid,
                    "comments":comments,
                    "new_bid":NewBid(),
                    "new_comment":NewComment(),
                    "in_watchlist":in_watchlist,
                    "bid_message": "Error! Your Bid must be greater than the current bid."
                })
            bid.highest_bidder= request.user.username
            bid.current_bid= new_bid
            bid.bid_count +=1
            bid.save()
            return render(request,"auctions/listing.html",{
                "listing":listing,
                "bid": bid,
                "comments":comments,
                "new_bid":NewBid(),
                "new_comment":NewComment(),
                "in_watchlist":in_watchlist,
                "bid_message": "Your Bid is added Successfully."
            })
        # return render(request,"auctions/error.html",{
        #     "message": "Invalid form"
        # })
    return render(request,"auctions/listing.html",{
        "listing":listing,
        "bid": bid,
        "comments":comments,
        "new_bid":NewBid(),
        "in_watchlist":in_watchlist,
        "new_comment":NewComment()
    })

@login_required(login_url = "/login")
def close_bidding(request,id):
    listing= Listing.objects.get(id=id)
    if request.user.username == listing.username:
        listing.bid_open=False
        listing.save()
        # return render(request,"auctions/listing.html",{
        #         "listing":listing,
        #         "bid": Bid.objects.get(item= listing.title)
        #     }) 
        return HttpResponseRedirect(reverse('listing', kwargs={'id':id} ))
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url = "/login")
def watchlist(request):
    watchlist= Watchlist.objects.filter(username=request.user.username)
    if not watchlist:
        return render(request,"auctions/index.html",{
        "heading": "Your Watchlist",
        "footer_msg": "You haven't added anything to your Watchlist!" 
        })

    listings=[]
    for item in watchlist:
        listings.append(Listing.objects.get(pk=item.listing_id))

    active_listings=[]
    for i in range(len(listings)):
        active_listings.append((listings[i],Bid.objects.get(listing_id= listings[i].id)))

    return render(request, "auctions/index.html" ,{
        "active_listings":active_listings,
        "heading": "Your Watchlist"
    })
    # return render(request, "auctions/watchlist.html",{
    #     "listings": listings
    # })

@login_required(login_url = "/login")
def edit_watchlist(request,id):
    watchlist= Watchlist.objects.filter(username=request.user.username)
    for item in watchlist:
        if id==item.listing_id:
            item.delete()
            return HttpResponseRedirect(reverse('listing', kwargs={'id':id} ))
    new_item= Watchlist(listing_id= id, username=request.user.username)
    new_item.save()
    # return render(request,"auctions/listing.html",{
    #     "listing":listing,
    #     "bid": Bid.objects.get(item= listing.title),
    #     "new_bid":NewBid()
    # })
    return HttpResponseRedirect(reverse('listing', kwargs={'id':id} ))

@login_required(login_url = "/login")
def add_comment(request,id):
    listing= Listing.objects.get(id=id)
    if request.method == "POST":
        form= NewComment(request.POST)
        if form.is_valid():
            comment= Comment.objects.create(username= request.user.username, comment=form.cleaned_data["comment"])
            comment.listing_id.set(Listing.objects.filter(id=id))
            # return render(request,"auctions/listing.html",{
            #     "listing":listing,
            #     "bid": Bid.objects.get(item= listing.title),
            #     "new_bid":NewBid()
            # })
            return HttpResponseRedirect(reverse('listing', kwargs={'id':id} ))
    return render(request,"auctions/add_comment.html",{
        "listing": listing,
        "form": NewComment()
    })
