from django.db import models
from django.urls import reverse
 
class Offer(models.Model):
    owner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, blank=True, null=True)
    vehicle_name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    price = models.IntegerField()
    mileage = models.IntegerField()
    
    vehicle_type_choices = (
        ('L', 'Light motor vehicle'),
        ('H', 'Heavy motor vehicle'),
        ('T', 'Two wheeled vehicle'),
        ('O', 'Other'),
    )
    vehicle_type = models.CharField(max_length=1, default='L', choices=vehicle_type_choices)
    
    date = models.DateTimeField(auto_now=True )
    extra_details = models.TextField(max_length=500, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True )

    image1 = models.ImageField()
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)
    image4 = models.ImageField(null=True, blank=True)
    image5 = models.ImageField(null=True, blank=True)
    image6 = models.ImageField(null=True, blank=True)
    image7 = models.ImageField(null=True, blank=True)
    
    image_count = models.IntegerField(default=1, blank=True)
    view_count = models.IntegerField(default=0, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self) -> str:
        return self.vehicle_name
    
    def get_absolute_url(self):
        return reverse('view-offer', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('delete-offer', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('edit-offer', kwargs={'slug': self.slug})

    def get_enquiry_url(self):
        return reverse('enquire', kwargs={'slug': self.slug})




