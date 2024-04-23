import datetime
from django.utils import timezone
import pytz
from rest_framework import serializers
from django.db.models import Sum

from parkingspace.models import Parking, VehicleDetails, ParkingSlot, ParkingPrice
from payment.models import Payments
from user.models import User


class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = ("id", "slot_name", "status")

class AdminParkingSlotSerializer(serializers.ModelSerializer):
    v_type = serializers.SerializerMethodField("get_vehicle")
    class Meta:
        model = ParkingSlot
        fields = ("id", "slot_name", "status", "v_type")

    def get_vehicle(self, obj):
        try:
            data = Parking.objects.get(parking_spot=obj,parking_status=True).vehicle.vehicle_type
            return data
        except:
            return None



class VehcileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDetails
        fields = ("vehicle_type", "vehicle_number")


class ParkingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField("get_name")
    parking_spot = ParkingSlotSerializer(read_only=True, many=False)
    vehicle = VehcileSerializer(read_only=True, many=False)
    price = serializers.SerializerMethodField("get_price")

    class Meta:
        model = Parking
        fields = (
            "id",
            "user_name",
            "parking_spot",
            "parking_time",
            "vehicle",
            "parking_status",
            "check_out",
            "price",
        )

    def get_name(self, obj):
        user = User.objects.get(id=obj.user.id)
        return user.name

    def get_price(self, obj):
        current_time = datetime.datetime.now()
        check_in_time_aware = timezone.make_naive(obj.parking_time)
        duration = current_time - check_in_time_aware
        hours, remainder = divmod(duration.seconds, 3600)
        vehicle_type = obj.vehicle.vehicle_type
        price = ParkingPrice.objects.all().first()
        if vehicle_type == "two":
            actual_price = price.two_wheeler_price
        else:
            actual_price = price.four_wheeler_price
        if hours == 0:
            hours = 1
        total_price = hours * actual_price
        return round(total_price, 2)


class CheckoutPriceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField("get_price")

    class Meta:
        model = Parking
        fields = ("price",)

    def get_price(self, obj):
        check_in_time_aware = timezone.make_naive(obj.parking_time)

        # Calculate the duration
        duration = obj.check_out_time - check_in_time_aware
        hours, remainder = divmod(duration.seconds, 3600)
        vehicle_type = obj.vehicle.vehicle_type
        price = ParkingPrice.objects.all().first()
        if vehicle_type == "two":
            actual_price = price.two_wheeler_price
        else:
            actual_price = price.four_wheeler_price
        if hours == 0:
            hours = 1
        total_price = hours * actual_price
        return round(total_price, 2)


class CheckOutAdminSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField("get_name")
    parking_spot = ParkingSlotSerializer(read_only=True, many=False)
    vehicle = VehcileSerializer(read_only=True, many=False)
    price = serializers.SerializerMethodField("get_price")
    payment = serializers.SerializerMethodField("get_payment")

    class Meta:
        model = Parking
        fields = (
            "id",
            "user_name",
            "parking_spot",
            "parking_time",
            "vehicle",
            "parking_status",
            "check_out",
            "check_out_time",
            "price",
            "payment",
        )

    def get_name(self, obj):
        user = User.objects.get(id=obj.user.id)
        return user.name

    def get_payment(self, obj):
        try:
            data = Payments.objects.get(service=obj)
            return data.payment_method
        except:
            return  None

    def get_price(self, obj):
        check_in_time_aware = obj.parking_time

        # Calculate the duration
        duration = obj.check_out_time - obj.parking_time
        hours, remainder = divmod(duration.seconds, 3600)
        vehicle_type = obj.vehicle.vehicle_type
        price = ParkingPrice.objects.all().first()
        if vehicle_type == "two":
            actual_price = price.two_wheeler_price
        else:
            actual_price = price.four_wheeler_price
        if hours == 0:
            hours = 1
        total_price = hours * actual_price
        return round(total_price, 2)


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPrice
        fields = ("two_wheeler_price", "four_wheeler_price")


class ParkingSlotAvailableSerializer(serializers.ModelSerializer):
    Two = serializers.SerializerMethodField("get_two")
    Four = serializers.SerializerMethodField("get_four")
    Available = serializers.SerializerMethodField("get_available")

    class Meta:
        model = ParkingSlot
        fields = ("Two", "Four", "Available")

    def get_two(self, obj):
        data = Parking.objects.filter(
            parking_status=True, vehicle__vehicle_type="two"
        ).count()
        return data

    def get_four(self, obj):
        data = Parking.objects.filter(
            parking_status=True, vehicle__vehicle_type="four"
        ).count()
        return data

    def get_available(self, obj):
        data = ParkingSlot.objects.filter(status=True).count()
        return data


class RevenueSerializer(serializers.ModelSerializer):
    daily = serializers.SerializerMethodField("get_daily")
    monthly = serializers.SerializerMethodField("get_monthly")

    class Meta:
        model = Payments
        fields = ("daily", "monthly")

    def get_daily(self, obj):
        today = timezone.now().date()
        total_price_earned_today = (
            Payments.objects.filter(date__date=today).aggregate(
                total_price=Sum("price")
            )["total_price"]
            or 0
        )
        return total_price_earned_today

    def get_monthly(self, obj):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        total_price_earned_within_month = (
            Payments.objects.filter(
                date__date__gte=start_of_month, date__date__lte=today
            ).aggregate(total_price=Sum("price"))["total_price"]
            or 0
        )
        return total_price_earned_within_month
