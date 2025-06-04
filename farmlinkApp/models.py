from django.db import models

# Create your models here.
class Farmer(models.Model):
    farmer_name = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    AREAS = (
        ('Hindi', 'Hindi'),
        ('Sabasaba', 'Sabasaba'),
        ('Kiongoni', 'Kiongoni'),
        ('Matengeni', 'Matengeni'),
        ('Safirisi', 'Safirisi'),
    )
    area_of_residence = models.CharField(max_length=100, choices=AREAS)
    password = models.CharField(max_length=100)
    profile_image = models.URLField(max_length=200, blank=True, null=True, default='https://res.cloudinary.com/dc68huvjj/image/upload/v1748119193/zzy3zwrius3kjrzp4ifc.png')
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer_name} ({self.area_of_residence})"


class Notification(models.Model):
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.id} for {self.farmer_id.name}"