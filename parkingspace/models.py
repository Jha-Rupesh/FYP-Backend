from django.db import models

from user.models import User


# Create your models here.
class ParkingSlot(models.Model):
    slot_name = models.CharField("Slot", max_length=10)
    status = models.BooleanField()  # True: Available, False: Occupied

    def __str__(self):
        return self.slot_name + " - " + ("Available" if self.status else "Occupied")


class VehicleDetails(models.Model):
    type = [("two", "two"), ("four", "four")]
    vehicle_type = models.CharField(choices=type, max_length=5)
    vehicle_number = models.CharField(max_length=10)


class Parking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(
        ParkingSlot, related_name="parked_car", on_delete=models.CASCADE
    )
    parking_time = models.DateTimeField()
    vehicle = models.ForeignKey(VehicleDetails, on_delete=models.CASCADE)
    parking_status = models.BooleanField(default=True)
    check_out = models.BooleanField(default=False)
    check_out_time = models.DateTimeField(null=True, blank=True)


class ParkingPrice(models.Model):
    two_wheeler_price = models.DecimalField(max_digits=6, decimal_places=2)
    four_wheeler_price = models.DecimalField(max_digits=6, decimal_places=2)


class Comments(models.Model):
    parking = models.ForeignKey(
        Parking, related_name="comments", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Reply(models.Model):
    comment = models.ForeignKey(
        Comments, related_name="replies", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
