from django.db import models
from auths.models import CustomUser

# Create your models here.

class String(models.Model):
    TYPE_CHOICES = (
        ("p","P"),
        ("w", "W")
    )
    string_name = models.CharField(max_length=250)
    type = models.CharField(max_length=250, choices=TYPE_CHOICES, default='p')
    gauge = models.DecimalField(max_digits=9, decimal_places=2)
    tension = models.DecimalField(max_digits=9, decimal_places=2)



class SetupStorage(models.Model):
    CHOICES = (
        ("guitar", "Guitar"),
        ("bass", "Bass")
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    setup_name = models.CharField(unique=True, null=True, blank=True)
    instrument_type = models.CharField(max_length=250, choices=CHOICES)
    total_strings = models.IntegerField()
    scale_sength = models.DecimalField(max_digits=9, decimal_places=2)
    is_multi_scale = models.BooleanField(db_default=True)
    string_type = models.CharField(max_length=250)
    selected_tuning = models.CharField(max_length=250) 

    total_tension = models.DecimalField(max_digits=9, decimal_places=2)
    strings = models.ManyToManyField(String, related_name="strings")

    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email}-----Setup ID{self.id}-----{self.setup_name}"



