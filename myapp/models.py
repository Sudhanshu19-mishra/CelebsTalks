from django.db import models

#class Admin(models.Model):

class Admin(models.Model):

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING   # default = Pending
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
 
class AdminToken(models.Model):
    admin = models.OneToOneField(Admin, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.name} - {self.token}"


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Influencer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    social_links = models.TextField(blank=True, null=True)

    price_per_min_chat = models.FloatField(default=0)
    price_per_min_audio = models.FloatField(default=0)
    price_per_min_video = models.FloatField(default=0)

    face_verified = models.BooleanField(default=False)
    commision_rate = models.FloatField(default=0)
    admin_approved = models.BooleanField(default=False)
    login_on_off = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name