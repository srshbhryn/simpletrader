from django.db import models

class Country(models.IntegerChoices):
    USA = 1
    GERMANY = 2
    UK = 3
    FRANCE = 4
    CHINA = 5
    INDIA = 6
