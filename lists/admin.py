from django.contrib import admin
from .models import Wishlist, Idea, Vote
# Register your models here.

admin.site.register(Wishlist)
admin.site.register(Idea)
admin.site.register(Vote)
