from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories",views.categories, name="categories"),
    path("new_category",views.new_category, name="new_category"),
    path("watchlist",views.watchlist, name="watchlist"),
    path("listing/<int:id>/edit_watchlist", views.edit_watchlist, name="edit_watchlist"),
    path("create_listing",views.create_listing, name="create_listing"),
    path("listing/<int:id>",views.listing,name="listing"),
    path("listing/<int:id>/close_bidding",views.close_bidding,name="close_bidding"),
    path("listing/<int:id>/add_comment",views.add_comment, name="add_comment"),
    path("<str:category_name>/category_items",views.category_items,name="category_items")
]
