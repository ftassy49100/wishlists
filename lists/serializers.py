from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class IdeaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = '__all__'     


class WishlistDetailSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserDetailSerializer(many=False)
    contributors = UserDetailSerializer(many=True)
    idea_set = IdeaDetailSerializer(many=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'name', 'creation_date', 'creator', 'contributors', 'idea_set', 'is_active']   