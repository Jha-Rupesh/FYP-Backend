from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
import datetime

from parkingspace.models import (
    Comments,
    ParkingPrice,
    ParkingSlot,
    Parking,
    Reply,
    VehicleDetails,
)
from parkingspace.serializers import (
    AdminParkingSlotSerializer,
    CheckoutPriceSerializer,
    ParkingSerializer,
    ParkingSlotAvailableSerializer,
    ParkingSlotSerializer,
    CheckOutAdminSerializer,
    PriceSerializer,
    RevenueSerializer,
)
from payment.models import Payments, notify
from payment.views import Payment
from user.models import User


# Create your views here.\
class AvailableSlot(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        slot = ParkingSlot.objects.all()
        if self.request.user.is_staff:
            serializer = AdminParkingSlotSerializer(slot, many=True)
        else:
            serializer = ParkingSlotSerializer(slot, many=True)
        return Response({"space": serializer.data}, status=status.HTTP_200_OK)


class BookSlot(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        # Check if the parking space is available or not

        parking_space = ParkingSlot.objects.get(id=data["parking_space"])
        if parking_space.status == True:
            vehicle_detail, _ = VehicleDetails.objects.get_or_create(
                vehicle_type=data["vehicle_type"], vehicle_number=data["vehicle_number"]
            )
            parking_book = Parking.objects.create(
                user=self.request.user,
                parking_spot=parking_space,
                parking_status=True,
                vehicle=vehicle_detail,
                parking_time=datetime.datetime.now(),
            )
            parking_space.status = False
            parking_space.save()
            noti = notify.objects.create(
                user=self.request.user,
                content="Your parking booking has been confirmed.",
            )
            return Response(
                "Successfully booked the parking space", status=status.HTTP_201_CREATED
            )
        return Response(
            "Parking Space has been booked!", status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, *args, **kwargs):
        try:
            if self.request.user.is_admin:
                parking_detail = Parking.objects.filter(
                    parking_status=True,
                    check_out=False,
                )
            else:
                parking_detail = Parking.objects.filter(
                    user=self.request.user,
                    parking_status=True,
                    check_out=False,
                )
            serializer = ParkingSerializer(parking_detail, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Parking.DoesNotExist:
            return Response(
                "No Parking Details Found", status=status.HTTP_404_NOT_FOUND
            )


class BookHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            if self.request.user.is_admin:
                parking_detail = Parking.objects.filter(
                    check_out=True, parking_status=False
                )
            else:
                parking_detail = Parking.objects.filter(
                    user=self.request.user, check_out=True
                )
            serializer = ParkingSerializer(parking_detail, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Parking.DoesNotExist:
            return Response(
                "No Parking Details Found", status=status.HTTP_404_NOT_FOUND
            )


class CheckOutParking(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        park = Parking.objects.get(
            user=self.request.user, parking_status=True, check_out=False
        )
        park.check_out = True
        park.check_out_time = datetime.datetime.now()
        park.save()
        notify.objects.create(
            user_id=User.objects.filter(is_staff=True).first().id,
            content="Check Out request generated for: {}".format(
                park.parking_spot.slot_name
            ),
        )
        serializer = CheckoutPriceSerializer(park, many=False)
        return Response({"data": "Success"}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_client or self.request.user.is_admin:
            park = Parking.objects.filter(parking_status=True, check_out=True)
            serializer = CheckOutAdminSerializer(park, many=True)
            return Response(
                {
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"data": "User is not authorized!"}, status=status.HTTP_401_UNAUTHORIZED
        )


class AcceptCheckout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.user.is_client or self.request.user.is_admin:
            parking_spots = self.kwargs["pk"]
            print(parking_spots)
            parking = Parking.objects.get(id=parking_spots)
            parking.parking_status = False
            parking.save()
            slot = ParkingSlot.objects.get(id=parking.parking_spot.id)
            slot.status = True
            slot.save()
            notify.objects.create(
                user=parking.user,
                content="Check Out request accepted for: {}".format(
                    parking.parking_spot.slot_name
                ),
            )
            return Response(
                {"data": "The car has been checked Out."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": "User is not authorized!"}, status=status.HTTP_401_UNAUTHORIZED
        )


class pricedata(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            parking_detail = ParkingPrice.objects.all().first()
            serializer = PriceSerializer(parking_detail, many=False)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Parking.DoesNotExist:
            return Response(
                "No Parking Details Found", status=status.HTTP_404_NOT_FOUND
            )


class Addslot(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        data = request.data
        slot = ParkingSlot.objects.create(
            slot_name=data["slot_name"], status=True
        ).save()
        return Response("Slot Added!", status=status.HTTP_200_OK)


class UpdatePrice(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        data = request.data
        price = ParkingPrice.objects.all().first()
        price.two_wheeler_price = data["two"]
        price.four_wheeler_price = data["four"]
        price.save()
        return Response("Price Updated!", status=status.HTTP_200_OK)


class PieData(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        slot = ParkingSlot.objects.all().first
        serializer = ParkingSlotAvailableSerializer(slot, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Revenue(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        slot = Payments.objects.all().first
        serializer = RevenueSerializer(slot, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddComments(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        data = request.data
        parking_id = data["id"]
        comment_text = data["comment"]

        try:
            parking = Parking.objects.get(pk=parking_id)
            comment = Comments.objects.create(
                parking=parking, name=request.user.name, comment=comment_text
            )
            return Response(
                {"message": "Comment added successfully"}, status=status.HTTP_200_OK
            )
        except Parking.DoesNotExist:
            return Response(
                {"message": "Parking spot not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AddReply(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        data = request.data
        comment_id = data["id"]

        reply_text = data["comment"]

        try:
            comment = Comments.objects.get(pk=comment_id)
            reply = Reply.objects.create(
                comment=comment, name="Admin", reply=reply_text
            )
            return Response(
                {"message": "Reply added successfully"}, status=status.HTTP_200_OK
            )
        except Comments.DoesNotExist:
            return Response(
                {"message": "Comment not found"}, status=status.HTTP_204_NO_CONTENT
            )


class GetReplies(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                id = request.GET.get('id')
                
                parking = Parking.objects.get(pk=id)
            else:
                parking = Parking.objects.get(user=request.user, parking_status=True, check_out=False)
            comments = parking.comments.all()
            comments_data = []
            for comment in comments:
                replies = comment.replies.all()
                replies_data = [
                    {
                        "name": reply.name,
                        "reply": reply.reply,
                        "created_at": reply.created_at,
                    }
                    for reply in replies
                ]
                comment_data = {
                    "id": comment.id,
                    "name": comment.name,
                    "comment": comment.comment,
                    "created_at": comment.created_at,
                    "replies": replies_data,
                }
                comments_data.append(comment_data)
            return Response({"comments": comments_data}, status=status.HTTP_200_OK)
        except Parking.DoesNotExist:
            return Response(
                {"message": "Parking spot not found"}, status=status.HTTP_204_NO_CONTENT
            )
