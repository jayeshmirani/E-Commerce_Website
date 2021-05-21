from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=20)

    def __str__(self):
        return self.category_name

class Listing(models.Model):
    username = models.CharField(max_length=60)
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=10000)
    image_url = models.URLField()
    category = models.CharField(max_length=60, default="No Category Listed")
    bid_open= models.BooleanField(default= True)

    def __str__(self):
        return str(self.id)

class Bid(models.Model):
    listing_id = models.IntegerField(default=0)
    current_bid = models.IntegerField()
    bid_count = models.IntegerField()
    highest_bidder= models.CharField(max_length=60)

    def __str__(self):
        return str(self.current_bid) 

class Comment(models.Model):
    listing_id = models.ManyToManyField(Listing, blank=True, related_name="comments")
    username = models.CharField(max_length=60)
    comment = models.CharField(max_length=60, default="")

    def __str__(self):
        return f"{self.username}^{self.comment}"

class Watchlist(models.Model):
    username= models.CharField(max_length=60)
    listing_id = models.IntegerField()

    def __str__ (self):
        return str(self.listing_id)