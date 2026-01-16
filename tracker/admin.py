from django.contrib import admin
from .models import WeightEntry, StepsEntry, ActivityEntry, GymSession, CardioEntry, CaloriesEntry


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'weight', 'body_fat_percentage']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date', '-time']


@admin.register(StepsEntry)
class StepsEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'steps']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date', '-time']


@admin.register(ActivityEntry)
class ActivityEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'activity_name', 'activity_type', 'distance_km']
    list_filter = ['date', 'activity_type']
    search_fields = ['date', 'activity_name', 'activity_type']
    ordering = ['-date', '-time']


@admin.register(GymSession)
class GymSessionAdmin(admin.ModelAdmin):
    list_display = ['date', 'notes']
    list_filter = ['date']
    search_fields = ['date', 'notes']
    ordering = ['-date']


@admin.register(CardioEntry)
class CardioEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'treadmill_minutes', 'bike_minutes', 'total_minutes']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date']


@admin.register(CaloriesEntry)
class CaloriesEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'calories', 'notes']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date']
