from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from .models import *
from .permissions import *
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import IdeaForm, WishlistForm, BookIdeaForm, VoteForm
from django.db.models import Q
################################### IMPORTS REST Framework ####################################
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from . import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework import status

# Create your views here.
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'lists/index.html'
    context_object_name = 'latest_lists'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Wishlist.objects.all()
        return Wishlist.objects.filter(Q(contributors=self.request.user) | Q(creator=self.request.user)).distinct().order_by('-creation_date')[:10]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        num_visits = self.request.session.get('num_visits', 0)
        print(num_visits)
        context['num_visits'] = num_visits + 1
        context['latest_lists'] = self.get_queryset()
        self.request.session['num_visits'] = num_visits + 1
        return context

############################################################## WISHLIST ##############################################
class WishlistCreateView(LoginRequiredMixin, CreateView):
    model = Wishlist
    template_name = 'lists/create/wishlist.html'
    form_class = WishlistForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.creator = self.request.user
        instance.save()
        return super().form_valid(form)


class WishlistUpdateView(LoginRequiredMixin, UpdateView):
    model = Wishlist
    template_name = 'lists/update/wishlist.html'
    form_class = WishlistForm

    def get_object(self, *args, **kwargs):
        obj = super(WishlistUpdateView, self).get_object(*args, **kwargs)
        print(obj.creator)
        print(obj.contributors)
        print(self.request.user)
        if not self.request.user == obj.creator and not len(obj.contributors.filter(pk=self.request.user.id))>0 and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas le droit d'acc??der ?? cette liste.")
        return obj

    def form_valid(self, form):
        print(self.request.user.is_staff)
        if not self.object.creator == self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas le droit de mettre ?? jour les informations de cette liste.")
        return super().form_valid(form)

class WishlistDeleteView(LoginRequiredMixin, DeleteView):
    model = Wishlist
    success_url = reverse_lazy('lists:index')

############################################################## IDEA ##############################################
class IdeaCreateView(LoginRequiredMixin, CreateView):
    model = Idea
    template_name = 'lists/create/idea.html'
    form_class = IdeaForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        wishlist = get_object_or_404(Wishlist, pk=self.kwargs['wishlist_id'])
        instance.wishlist = wishlist
        instance.creator = self.request.user
        if not wishlist.can_add_idea(self.request.user):
            raise PermissionDenied("Vous n'??tes pas autoris?? ?? ajouter une id??e ?? cette liste.")
        instance.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs): # pour passer la wishlist ?? la view, et savoir comment cr??er la nouvelle id??e
        wishlist = get_object_or_404(Wishlist, pk=self.kwargs['wishlist_id']) 
        if not wishlist.can_add_idea(self.request.user): # on ne permet pas l'acc??s ?? la view si l'utilisateur n'a pas les droits
            raise PermissionDenied("Vous n'??tes pas autoris?? ?? ajouter une id??e ?? cette liste.")
        context = super().get_context_data(**kwargs)
        context["wishlist"] = wishlist
        return context

class IdeaUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Idea
    template_name = 'lists/update/idea.html'
    form_class = IdeaForm

    def get_object(self, queryset=None, *args, **kwargs):
        """override pour v??rifier que l'utilisateur a le droit de modifier cette id??e"""
        idea = super(IdeaUpdateView, self).get_object(*args, **kwargs)
        print(idea)
        if not idea.can_update(self.request.user):
            raise PermissionDenied("Vous n'??tes pas autoris?? ?? modifier cette id??e.")
        return idea

class IdeaDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Idea

    def get_object(self, queryset=None):
        """pour v??rifier que l'utilisateur a le droit de supprimer cette id??e"""
        idea = super(IdeaDeleteView, self).get_object()
        if not idea.can_update(self.request.user):
            raise PermissionDenied("Vous n'??tes pas propri??taire de la liste, ni cr??ateur de l'id??e !")
        return idea

    def get_success_url(self):
        idea = self.get_object()
        return reverse_lazy('lists:wishlist-update', kwargs={'pk': idea.wishlist.id})

    template_name = 'lists/delete/idea_confirm_delete.html'


class VoteView(LoginRequiredMixin, generic.DetailView):
    model = Vote
    template_name = 'lists/vote.html'

############################################################## VOTE ##############################################

class VoteCreateView(LoginRequiredMixin, CreateView):
    model = Vote
    template_name = 'lists/create/vote.html'
    form_class = VoteForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        print(self.kwargs['idea_id'])
        idea = get_object_or_404(Idea, pk=self.kwargs['idea_id'])
        instance.idea = idea
        instance.voter = self.request.user
        if not idea.can_vote(self.request.user):
            raise PermissionDenied("Vous n'??tes pas autoris?? ?? voter pour cette id??e.")
        instance.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs): # pour passer la wishlist ?? la view, et savoir comment cr??er la nouvelle id??e
        print(self.kwargs['idea_id'])
        idea = get_object_or_404(Idea, pk=self.kwargs['idea_id'])
        if not idea.can_see(self.request.user): # on ne permet pas l'acc??s ?? la view si l'utilisateur n'a pas les droits
            raise PermissionDenied("Vous n'??tes pas autoris?? ?? acc??der ?? cette id??e.")
        context = super().get_context_data(**kwargs)
        context["idea"] = idea
        return context

class VoteUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Vote
    template_name = 'lists/update/vote.html'
    form_class = VoteForm

    def get_object(self, queryset=None, *args, **kwargs):
        """override pour v??rifier que l'utilisateur a le droit de modifier cette id??e"""
        vote = super(VoteUpdateView, self).get_object(*args, **kwargs)
        print(vote)
        #if not vote.idea.can_vote(self.request.user):
        #    raise PermissionDenied("Vous n'??tes pas autoris?? ?? voter cette id??e.")
        return vote

class VoteDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Vote

    def get_object(self, queryset=None):
        """pour v??rifier que l'utilisateur a le droit de supprimer cette id??e"""
        idea = super(IdeaDeleteView, self).get_object()
        if not idea.can_update(self.request.user):
            raise PermissionDenied("Vous n'??tes pas propri??taire de la liste, ni cr??ateur de l'id??e !")
        return idea

    def get_success_url(self):
        idea = self.get_object()
        return reverse_lazy('lists:wishlist-update', kwargs={'pk': idea.wishlist.id})

    template_name = 'lists/delete/idea_confirm_delete.html'


class VoteView(LoginRequiredMixin, generic.DetailView):
    model = Vote
    template_name = 'lists/vote.html'

############################################################## REST API ##############################################

class AdminWishlistViewSet(ModelViewSet):
    serializer_class = serializers.WishlistAdminSerializer
    permission_classes = [IsAdminAuthenticated]

    def get_queryset(self):
        queryset = Wishlist.objects.all()
        user = self.request.user
        name = self.request.GET.get('name') #on r??cup??re le param get['name'] qu'on peut utiliser pour filtrer
        if name is not None:
            queryset = queryset.filter(name__icontains=name) #string__icontains est un LIKE case insensitive
            print(queryset)
        queryset = queryset.filter((Q(contributors=self.request.user) | Q(creator=self.request.user)), ).distinct().order_by('-creation_date')
        return queryset
        

class AdminIdeaViewSet(ModelViewSet):
    serializer_class = serializers.IdeaAdminSerializer
    permission_classes = [IsAdminAuthenticated]

    def get_queryset(self):
        return Idea.objects.all()

    @action(detail=True, methods=['post'])
    def book(self, request, pk):
        if request.user.is_authenticated:
            self.get_object().book(request.user)
        return Response()

    @action(detail=True, methods=['POST'])
    def vote(self, request, pk, *args, **kwargs):
        idea = self.get_object()
        if idea.can_vote(request.user) and request.data['good_idea'] is not None:
            vote = Vote.objects.get_or_create(idea=idea, voter=request.user, good_idea=request.data['good_idea'])
            print(vote)
            vote.save()
        return Response()

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk, *args, **kwargs):
        idea = self.get_object()
        idea.cancel(request.user)

    @action(detail=True, methods=['POST'])
    def buy(self, request, pk, *args, **kwargs):
        idea = self.get_object()
        idea.buy(request.user)

class AdminUserViewSet(ModelViewSet):
    serializer_class = serializers.UserAdminSerializer
    queryset = User.objects.all()
        
class UserCreate(APIView):
    """ 
    Creates the user. 
    """

    def post(self, request, format='json'):
        serializer = UserAdminSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)