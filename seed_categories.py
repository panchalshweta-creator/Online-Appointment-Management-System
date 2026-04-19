import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from appointment.models import Category

categories = [
    ('Beauty & Wellness', 'fa-spa'),
    ('Dentist', 'fa-tooth'),
    ('Medical Clinic', 'fa-hospital'),
    ('Fitness Trainer', 'fa-dumbbell'),
    ('Spa', 'fa-hot-tub'),
    ('Tutor', 'fa-book-reader'),
]

for name, icon in categories:
    Category.objects.get_or_create(name=name, icon=icon)

print("Categories seeded successfully!")
