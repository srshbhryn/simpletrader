from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=32)

class Website(models.Model):
    host = models.CharField(max_length=64)

# class Proxy(models.Model):
#     Country

class SearchConfig(models.Model):
    country = models.CharField(max_length=32)
    website = models.CharField(max_length=64, null=True)


