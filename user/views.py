import base64
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
import json

from parkingspace.models import Parking
from .models import User
from user.serializer import (
    UserDataSerial,
)
from .utils import Util
from pyotp import TOTP

OTP_VALIDITY_TIME: int = 60 * 150


def get_base32_key(user) -> str:
    # Generates a base32 value based on the key provided.
    # Key used should be hashed value of password.
    key = settings.SECRET_KEY + str(user.id)
    key = bytes(key, encoding="UTF-8")
    val = base64.b32encode(key)
    val = str(val)
    return val.split("'")[1]


def generate_otp(user, digits=4) -> int:
    base32_key = get_base32_key(user)
    otp = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).now()
    return otp


def validate_otp(user, otp: int, digits=4) -> bool:
    base32_key = get_base32_key(user)
    return TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).verify(otp)


# To verify User duing Signup
class activatepw(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        global otp
        try:
            data = request.data
            otp = data["otp"]
            emails = data["email"]
            users = User.objects.get(email=emails)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            users = None
        if users is not None and validate_otp(users, otp):
            refresh = RefreshToken.for_user(users)
            return Response(
                {
                    "message": "User Verified!",
                    "user_id": users.id,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Invalid Activation Link!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# To verify User During Forget Password
class activate(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        global otp
        try:
            data = request.data

            otp = data["otp"]
            print(otp)
            username = data["email"]
            users = User.objects.get(email__iexact=username)
            print(users)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            users = None
        print(validate_otp(users, otp))
        if users is not None and validate_otp(users, otp):

            users.is_verified = True
            users.save()
            refresh = RefreshToken.for_user(users)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "User Verified!",
                    "user_id": users.id,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Invalid Activation Link!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# To create User
class Create_User(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        data = request.data
        address = request.data.get("address", None)
        name = request.data.get("name", None)
        user_image = request.FILES.get("image", "")
        phone = request.data.get("phone", None)

        # try:
        try:
            userSign = User.objects.create_user(
                email=data["email"],
                password=data["password"],
                address=address,
                name=name,
                user_image=user_image,
                phone=phone,
                user_type=3,
            )
            mail_subject = "Activate your account."
            message = render_to_string(
                "emailtemplate.html",
                {"user": userSign, "otp": generate_otp(userSign)},
            )
            to_email = data["email"]
            data = {"email_body": message, "email": to_email, "subject": mail_subject}

            Util.send_email(data)
            userSign.save()
            return Response(
                {
                    "message": "User Created",
                },
                status=status.HTTP_200_OK,
            )

        except:
            return Response(
                {
                    "message": "Error!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# Login User/Admin
class Login_User(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            data = request.data
            username = data["email"]
            password = data["password"]
            try:
                user = authenticate(username=username, password=password)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    login(request, user)
                    userdetails = User.objects.get(email=username)
                    usertype = userdetails.user_type
                    serializer = UserDataSerial(userdetails, many=False)
                    parking = False
                    try:
                        parking_detail = Parking.objects.get(
                            user=userdetails, parking_status=True, check_out=False
                        )
                        parking = True
                    except:
                        parking = False
                    if not userdetails.is_verified:

                        return Response(
                            {
                                "message": "User is not verified",
                            },
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                    else:
                        response = {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "user_data": serializer.data,
                            "user_type": usertype,
                            "booking": parking,
                        }
                        return Response(response, status=status.HTTP_200_OK)

                else:
                    return Response(
                        {
                            "message": "Username or password doesn't match!",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except User.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)


# To send Email with OTP for Reset Password
class emailpass(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            emails = data["email"]
            signupdata = User.objects.get(email=emails)
            mail_subject = "Change Your Password."
            message = render_to_string(
                "passwordtemplate.html",
                {"user": signupdata, "otp": generate_otp(signupdata)},
            )
            to_email = emails
            data = {"email_body": message, "email": to_email, "subject": mail_subject}
            Util.send_email(data)
            messages.success(request, "")
            return Response(
                {
                    "message": "Check your email for password reset OTP",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


# To re-send OTP during Signup
class reverify(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            emails = data["email"]
            print(emails)
            signupdata = User.objects.get(email=emails)
            current_site = get_current_site(request)
            mail_subject = "Activate your account."
            message = render_to_string(
                "emailtemplate.html",
                {"user": signupdata, "otp": generate_otp(signupdata)},
            )
            to_email = emails
            data = {"email_body": message, "email": to_email, "subject": mail_subject}
            Util.send_email(data)
            return Response(
                {
                    "message": "Check your email for email verification link!",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {
                    "message": "Error!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# For forget password
class forgetpw(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            newpw = data["password"]
            repw = data["repassword"]
            if newpw == repw:
                userdata = User.objects.get(id=request.user.id)
                userdata.set_password(newpw)
                userdata.save()
                return Response(
                    {
                        "message": "The password has been reset!",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Password does not match",
                    },
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
        except:
            return Response(
                {
                    "message": "Error!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# To add/Update User Details
class details(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            name = data["name"]
            image = request.FILES.get("image")
            address = data["address"]
            contact = data["phone"]
            userData = User.objects.get(id=request.user.id)
            userData.name = name
            userData.user_image.delete()
            userData.user_image = image
            userData.phone = contact
            userData.address = address
            userData.save()
            return Response(
                {
                    "message": "The details has been updated!",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {
                    "message": "Error!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request, *args, **kwargs):
        userData = User.objects.get(id=request.user.id)
        serial = UserDataSerial(userData, many=False)
        return Response(serial.data, status=status.HTTP_200_OK)


# To change Password
class changepass(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            oldpass = data["oldpassword"]
            newpw = data["password"]
            user = authenticate(username=request.user, password=oldpass)
            if user is not None:
                userdata = User.objects.get(id=request.user.id)
                userdata.set_password(newpw)
                userdata.save()
                return Response(
                    {
                        "message": "The password has been updated!",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Wrong Password!",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                {
                    "message": "Error!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class checkdata(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        parking = False
        try:
            parking_detail = Parking.objects.get(
                user=self.request.user, parking_status=True, check_out=False
            )
            parking = True
        except:
            parking = False
        return Response(
            {
                "booking": parking,
            },
            status=status.HTTP_200_OK,
        )
