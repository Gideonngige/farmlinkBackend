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

class Question(models.Model):
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question {self.id} by {self.farmer_id.farmer_name}"

class Reply(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='replies')
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='replies')
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply {self.id} to Question {self.question.id} by {self.farmer_id.farmer_name}"

class Product(models.Model):
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='product')
    product_name = models.CharField(max_length=100)
    product_image = models.URLField(max_length=200, blank=True, null=True, default='https://res.cloudinary.com/dc68huvjj/image/upload/v1748119193/zzy3zwrius3kjrzp4ifc.png')
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} ksh{self.price} by {self.farmer_id.farmer_name}"