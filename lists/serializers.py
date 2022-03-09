from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers

class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class IdeaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = '__all__'     


class WishlistAdminSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserAdminSerializer(many=False)
    contributors = UserAdminSerializer(many=True)
    idea_set = IdeaAdminSerializer(many=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'name', 'creation_date', 'creator', 'contributors', 'idea_set', 'is_active']