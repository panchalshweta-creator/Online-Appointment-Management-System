from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('business', 'Business'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client')

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fa-spa)")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    business_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='businesses')
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True) # Business specific email
    business_hours = models.TextField(blank=True, help_text="e.g., Mon-Fri: 9am - 5pm")
    profile_image = models.ImageField(upload_to='business_images/', blank=True, null=True)
    is_approved = models.BooleanField(default=True) # Set to True for easier testing as per "visible to clients"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name if self.business_name else self.user.username

class Service(models.Model):
    service_provider = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AvailabilitySlot(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('service', 'date', 'start_time', 'end_time')
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.service.name} - {self.date} {self.start_time}-{self.end_time}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Reschedule Requested', 'Reschedule Requested'),
        ('Rescheduled', 'Rescheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    availability_slot = models.OneToOneField(AvailabilitySlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_slot')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    
    # Reschedule fields
    reschedule_date = models.DateField(null=True, blank=True)
    reschedule_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Appointment for {self.service.name} by {self.client.username}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
