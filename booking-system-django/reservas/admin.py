from django.contrib import admin

from .models import Availability, Booking, Resource


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'slot_minutes', 'is_active')
    inlines = [AvailabilityInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('resource', 'user', 'start', 'end', 'status')
    list_filter = ('status', 'resource')
