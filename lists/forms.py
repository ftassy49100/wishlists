from django.forms import ModelForm
from lists.models import Idea, Wishlist, Vote

class IdeaForm(ModelForm):
    class Meta:
        model = Idea
        fields = ['name', 'image_url', 'price']

class BookIdeaForm(ModelForm):
    class Meta:
        model = Idea
        fields = ['booked_by']

class WishlistForm(ModelForm):
    class Meta:
        model = Wishlist
        fields = ['name', 'contributors']

class VoteForm(ModelForm):
    class Meta:
        model = Vote
        fields = ['good_idea']