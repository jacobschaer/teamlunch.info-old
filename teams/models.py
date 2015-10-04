from django.db import models

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name