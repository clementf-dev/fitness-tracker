from django.urls import path
from .views import (
    # Dashboard
    dashboard, api_combined_data,
    # Calories
    calories_dashboard, add_meal_item, delete_meal_item, edit_meal_item,
    update_meal_item_order, calories_calendar, save_meal_as_template,
    # Food
    food_database, add_food, edit_food, delete_food, search_food_api,
    # Templates
    meal_templates, add_meal_template, edit_meal_template,
    delete_meal_template, delete_template_item, apply_template, edit_template_item,
    # Imports
    import_csv, sync_from_drive_view,
    # Data Management
    data_management, edit_entry, delete_entry, bulk_delete_entries, gym_calendar,
    # Manual Entries
    add_weight, add_steps, add_activity, add_gym_session, add_cardio, add_calories,
    delete_gym_session_calendar,
)


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('import/', import_csv, name='import_csv'),
    path('sync-drive/', sync_from_drive_view, name='sync_from_drive'),
    
    # Ajout manuel
    path('add/weight/', add_weight, name='add_weight'),
    path('add/steps/', add_steps, name='add_steps'),
    path('add/activity/', add_activity, name='add_activity'),
    path('add/gym/', add_gym_session, name='add_gym_session'),
    path('delete/gym-calendar/', delete_gym_session_calendar, name='delete_gym_session_calendar'),
    path('add/cardio/', add_cardio, name='add_cardio'),
    path('add/calories/', add_calories, name='add_calories'),
    
    # Data Management
    path('manage/', data_management, name='data_management'),
    path('manage/edit/<str:entry_type>/<int:entry_id>/', edit_entry, name='edit_entry'),
    path('manage/delete/<str:entry_type>/<int:entry_id>/', delete_entry, name='delete_entry'),
    path('manage/bulk-delete/', bulk_delete_entries, name='bulk_delete_entries'),
    path('gym-calendar/', gym_calendar, name='gym_calendar'),

    # ============================================
    # ROUTES POUR LE SUIVI DES CALORIES
    # ============================================
    
    # Calories Dashboard
    path('calories/', calories_dashboard, name='calories_dashboard'),
    path('calories/update-order/', update_meal_item_order, name='update_meal_item_order'),
    path('calories/calendar/', calories_calendar, name='calories_calendar'),
    path('calories/add/<str:date_str>/<str:meal_type>/', add_meal_item, name='add_meal_item'),
    path('calories/edit-item/<int:item_id>/', edit_meal_item, name='edit_meal_item'),
    path('calories/delete/<int:item_id>/', delete_meal_item, name='delete_meal_item'),
    path('calories/save-template/<str:date_str>/<str:meal_type>/', save_meal_as_template, name='save_meal_as_template'),
    path('calories/<str:date_str>/', calories_dashboard, name='calories_dashboard_date'),
    
    # Food Database
    path('food/', food_database, name='food_database'),
    path('food/add/', add_food, name='add_food'),
    path('food/edit/<int:food_id>/', edit_food, name='edit_food'),
    path('food/delete/<int:food_id>/', delete_food, name='delete_food'),
    
    # Meal Templates
    path('templates/', meal_templates, name='meal_templates'),
    path('templates/add/', add_meal_template, name='add_meal_template'),
    path('templates/edit/<int:template_id>/', edit_meal_template, name='edit_meal_template'),
    path('templates/delete/<int:template_id>/', delete_meal_template, name='delete_meal_template'),
    path('templates/edit-item/<int:item_id>/', edit_template_item, name='edit_template_item'),
    path('templates/delete-item/<int:item_id>/', delete_template_item, name='delete_template_item'),
    path('templates/apply/<int:template_id>/', apply_template, name='apply_template'),

    # API endpoints
    path('api/combined-data/', api_combined_data, name='api_combined_data'),
    path('api/food/search/', search_food_api, name='search_food_api'),
]

# Reload trigger (Template Fix applied)
