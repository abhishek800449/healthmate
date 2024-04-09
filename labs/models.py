from django.db import models
from accounts.models import PatientProfile, City

# Create your models here.

class LabTest(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True)
    image = models.ImageField(blank=True, upload_to='lab_test_images')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class LabTestBooking(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    booking_date = models.DateField(auto_now_add=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    phone_number = models.CharField(max_length=12)
    remarks = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=20, default='pending')
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    zip_code = models.CharField(max_length=20)

    def order_id(self):
        try:
            from orders.models import Order
            order = Order.objects.get(lab=self)
            return order.id
        except:
            return 0


class PendingLabBooking(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    phone_number = models.CharField(max_length=12)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    zip_code = models.CharField(max_length=20)