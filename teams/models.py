from django.db import models

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name="member")
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    coordinator = models.ManyToManyField(Team)

    def __str__(self):
        return self.name