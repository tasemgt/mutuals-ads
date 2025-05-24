from django.db import models
import jsonfield
# from django.contrib.auth.models import AbstractUser  # Optional, for auth

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class SubGroup(models.Model):
    subgroup_id = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='subgroups')
    name = models.CharField(max_length=100)
    event = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "subgroup_id")

    def __str__(self):
        return f"{self.name} (Group: {self.group.name})"

class User(models.Model):
    name = models.CharField(max_length=100)
    user_id = models.CharField(unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    budget = models.FloatField()
    age = models.IntegerField()
    age_range = models.CharField(max_length=20)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    subgroup = models.ForeignKey(SubGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    interests = models.ManyToManyField(Interest, related_name='users')

    def __str__(self):
        return self.name

class Event(models.Model):
    event_id = models.IntegerField(unique=True)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    location = models.CharField(max_length=100)
    ticket_price = models.FloatField()
    venue_id = models.IntegerField()
    tags = jsonfield.JSONField()  # Stores tags as a list

    def __str__(self):
        return self.event_name
