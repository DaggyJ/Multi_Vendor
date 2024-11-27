
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):


    def __str__(self):
        return self.name

class Contact(models.Model):
    # contact_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    phonenumber=models.IntegerField(max_length=10)
    email=models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    desc=models.TextField(max_length=500)
   

    def __int__(self):
        return self.id



class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.TextField(max_length=250, default='')
    image = models.ImageField(upload_to='upload/product', null=True, blank=True)
    # Add this line if you want a category field
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ManyToManyField(Cart)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def order_total(self):
        total = sum([item.total_price() for item in self.cart.all()])
        return total

class OrderUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='updates')
    update_desc = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for Order {self.order.id} at {self.timestamp}"
