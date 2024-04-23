from django.contrib import admin
from .models import Comments, Parking, ParkingPrice, ParkingSlot, VehicleDetails, Reply

# Register your models here.
admin.site.register([ParkingSlot, VehicleDetails,Parking, ParkingPrice, Comments, Reply])
