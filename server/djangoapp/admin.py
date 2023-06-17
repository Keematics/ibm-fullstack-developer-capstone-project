from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel


# Register your models here.
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name',  'dealer_id', 'car_type', 'year']
    search_fields = ['name']

class CarMakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

# CarModelInline class

# CarModelAdmin class

# CarMakeAdmin class with CarModelInline

# Register models here
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake)