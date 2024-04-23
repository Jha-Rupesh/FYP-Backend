from django.contrib import admin

from payment.models import notify, Payments

# Register your models here.
admin.site.register([notify, Payments])