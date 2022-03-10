from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.SimpleRouter()
router.register('wishlist', views.AdminWishlistViewSet, basename='wishlist')
router.register('user', views.AdminUserViewSet, basename='user')
router.register('idea', views.AdminIdeaViewSet, basename='idea')

app_name = 'lists'
urlpatterns = [ #urls de mon application lists,
    path('', views.IndexView.as_view(), name='index'),
    path('wishlist/add/', views.WishlistCreateView.as_view(), name='wishlist-add'),
    path('wishlist/<int:pk>/', views.WishlistUpdateView.as_view(), name='wishlist-update'),
    path('wishlist<int:pk>/delete/', views.WishlistDeleteView.as_view(), name='wishlist-delete'),
    path('idea/<int:pk>/', views.IdeaUpdateView.as_view(), name='idea-update'),
    path('wishlist/<int:wishlist_id>/idea/add/', views.IdeaCreateView.as_view(), name='idea-add'),
    path('idea/<int:pk>/delete', views.IdeaDeleteView.as_view(), name='idea-delete'),
    path('idea/<int:idea_id>/vote/add', views.VoteCreateView.as_view(), name='vote-add'),
    path('vote/<int:pk>/', views.VoteUpdateView.as_view(), name='vote-update'),
    path('vote/<int:pk>/delete/', views.VoteDeleteView.as_view(), name='vote-delete'),
    path('vote/<int:pk>/results', views.VoteView.as_view(), name='view_vote'),
    path('api/', include(router.urls)),
    path('/api/users/', views.UserCreate.as_view(), name='account-create')

    #path(route='la route', view'la view.as_view()', kwargs='les arguments get', name='nom de la view')
]