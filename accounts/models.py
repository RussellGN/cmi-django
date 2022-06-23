from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class CustomUser(AbstractUser):
    location = models.CharField(max_length=30)
    about = models.TextField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    shortlist = models.ManyToManyField('app.Offer',related_name='shortlisted', blank=True)
    enquired = models.ManyToManyField('app.Offer', related_name='enquiries' ,blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    display_photo = models.ImageField(default='default.jpg', blank=True)

    account_type_choices = (
        ('NU', 'Normal User'),
        ('DA', 'Dealership Account'),
    )
    account_type = models.CharField(max_length=2, choices=account_type_choices)
    
    notification_inbox_choices = (
        ('E', 'Email'),
        ('S', 'SMS'),
        ('B', 'Both')
    )
    notification_inbox = models.CharField(max_length=1, choices=notification_inbox_choices, default='E', blank=True)

    def __str__(self) -> str:
        return self.username
    
    def get_absolute_url(self):
        return reverse('account', kwargs={'slug': self.slug})
 
class Notification(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=40)
    body = models.TextField(max_length=1000)
    view_count = models.IntegerField(default=0, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    icon_choices = (
        ('E', 'bi bi-envelope'),
        ('I', 'bi bi-info-circle'),
        ('ET', 'bi bi-exclamation-triangle'),
        ('S', 'bi bi-star'),
    )
    icon = models.CharField(max_length=2, choices=icon_choices)

    class Meta:
        ordering = ['-date']

    def __str__(self) -> str:
        return self.title



