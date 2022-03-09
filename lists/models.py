from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.db import transaction


# Create your models here.
class Wishlist(models.Model):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contributors = models.ManyToManyField(User, related_name='contributors')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def can_add_idea(self, user):
        if self.is_active:
            return len(self.contributors.filter(id=user.id)) > 0 or self.creator.id == user.id or user.is_staff
        return self.is_active

    def alert_contributor(self, contributors_emails):
        # Todo : envoyer un email à chaque utilisateur listé ici
        pass

    def can_update(self, user):
        return self.creator == user or user.is_staff

    def get_absolute_url(self):
        return reverse('lists:wishlist-update', kwargs={'pk': self.pk})


class Idea(models.Model):
    name = models.CharField(max_length=200)
    image_url = models.CharField(max_length=2000)
    price = models.FloatField()
    status = models.IntegerField(default=0)  # 0 = stockée, 1 = réservée, 2 = achetée, 3= annulée
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booked_by')

    def __str__(self):
        return self.name

    def can_vote(self, voter):
        if self.status < 2:
            return (len(self.vote_set.filter(idea=self, voter=voter)) == 0 and (
                        self.wishlist.creator != voter or len(self.wishlist.contributors.filter(id=voter.id)) > 0))
        return False

    def can_update(self, user):
        return self.creator == user or user.is_staff

    def can_see(self, user):
        return ((self.creator == user) or (
                    len((self.wishlist.contributors.filter(id=user.id))) > 0 and self.wishlist.creator != user))

    def update_status(self, status_id):
        if status_id < 0 or status_id > 3:
            raise ValueError("The new status must be between 0 and 3 !")
        self.status = status_id
        self.save()

    def get_absolute_url(self):
        return reverse('lists:idea-update', kwargs={'pk': self.pk})

    @transaction.atomic
    def book(self, user): #               len(self.wishlist.contributors.filter(id=user.id)) > 0 => user pas dans la liste des contributeurs
        if self.booked_by is not None and len(self.wishlist.contributors.filter(id=user.id)) > 0 or not user.is_staff:
            raise PermissionDenied("Vous n'êtes pas autorisé à réserver cette idée")
        self.booked_by = user
        self.save()
        return self


class Vote(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    good_idea = models.BooleanField(default=True)
    voter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.idea.name + " is a good idea : " + str(self.good_idea)

    def get_absolute_url(self):
        return reverse('lists:vote-update', kwargs={'pk': self.pk})
