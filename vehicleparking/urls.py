"""
URL configuration for vehicleparking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from payment.views import NotificationData, Payment
from user.views import Create_User, Login_User, activate, activatepw, checkdata,emailpass,details,changepass,forgetpw, reverify
from parkingspace.views import AddComments, AddReply, Addslot, AvailableSlot, BookHistory, BookSlot, CheckOutParking, AcceptCheckout, GetReplies, PieData, Revenue, UpdatePrice, pricedata

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/login/', Login_User.as_view(), name="login"),
    path('api/v1/register/', Create_User.as_view(), name="register"),
    path('api/v1/activate/', activate.as_view(), name='activate'),
    path('api/v1/activatepw/', activatepw.as_view(), name='password reset'),
    path('api/v1/emailpw/', emailpass.as_view(), name="Email recovery"),
    path('api/v1/userdetails/', details.as_view(), name="user details"),
    path('api/v1/changepassword/', changepass.as_view(), name="change password"),
    path('api/v1/forgetpassword/', forgetpw.as_view(), name="forget password"),
    path('api/v1/refresh-token/', TokenRefreshView.as_view(), name="refresh_token"),
    path('api/v1/available-slot/', AvailableSlot.as_view(), name="available_slot"),
    path('api/v1/book-slot/', BookSlot.as_view(), name='book_slot'),
    path('api/v1/check-out/', CheckOutParking.as_view(), name="check_out"),
    path('api/v1/accept-check-out/<str:pk>/', AcceptCheckout.as_view(), name="accept_check_out"),
    path('api/v1/payment/', Payment.as_view(), name="payment"),
    path('api/v1/reotp/', reverify.as_view(), name="resendotp"),
    path('api/v1/notify/', NotificationData.as_view(), name="notification"),
    path('api/v1/history/', BookHistory.as_view(), name="booking_history"),
    path('api/v1/check-data/', checkdata.as_view(), name="check_Data"),
    path('api/v1/price/', pricedata.as_view(), name="check_price"),
    path('api/v1/updateprice/', UpdatePrice.as_view(), name="update_price"),
    path('api/v1/addslot/', Addslot.as_view(), name="add_slot"),
    path('api/v1/piedata/', PieData.as_view(), name="piedata"),
    path('api/v1/revenue/', Revenue.as_view(), name="revenue"),
    path('api/v1/add-comment/', AddComments.as_view(), name="add_comment"),
    path('api/v1/add-reply/', AddReply.as_view(), name="add_reply"),
    path('api/v1/getcomment/', GetReplies.as_view(), name="get_replies"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)