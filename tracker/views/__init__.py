"""
Tracker Views Package

This package contains all views for the fitness tracker application,
split into logical modules for better maintainability.

All views are re-exported here for backward compatibility with urls.py.
"""

# Dashboard views
from .dashboard import dashboard, api_combined_data

# Calories tracking views  
from .calories import (
    calories_dashboard,
    add_meal_item,
    delete_meal_item,
    edit_meal_item,
    update_meal_item_order,
    calories_calendar,
    save_meal_as_template,
)

# Food search and database views
from .food_search import (
    food_database,
    add_food,
    edit_food,
    delete_food,
    search_food_api,
)

# Meal templates views
from .templates_views import (
    meal_templates,
    add_meal_template,
    edit_meal_template,
    delete_meal_template,
    delete_template_item,
    apply_template,
    edit_template_item,
)

# Import views
from .imports import (
    import_csv,
    import_weight_csv,
    import_steps_csv,
    import_activities_csv,
    sync_from_drive_view,
)

# Data management views
from .data_management import (
    data_management,
    edit_entry,
    delete_entry,
    bulk_delete_entries,
    gym_calendar,
)

# Manual entry views
from .manual_entries import (
    add_weight,
    add_steps,
    add_activity,
    add_gym_session,
    add_cardio,
    add_calories,
    delete_gym_session_calendar,
)

__all__ = [
    # Dashboard
    'dashboard',
    'api_combined_data',
    
    # Calories
    'calories_dashboard',
    'add_meal_item',
    'delete_meal_item', 
    'edit_meal_item',
    'update_meal_item_order',
    'calories_calendar',
    'save_meal_as_template',
    
    # Food
    'food_database',
    'add_food',
    'edit_food',
    'delete_food',
    'search_food_api',
    
    # Templates
    'meal_templates',
    'add_meal_template',
    'edit_meal_template',
    'delete_meal_template',
    'delete_template_item',
    'apply_template',
    'edit_template_item',
    
    # Imports
    'import_csv',
    'import_weight_csv',
    'import_steps_csv',
    'import_activities_csv',
    'sync_from_drive_view',
    
    # Data Management
    'data_management',
    'edit_entry',
    'delete_entry',
    'bulk_delete_entries',
    'gym_calendar',
    
    # Manual Entries
    'add_weight',
    'add_steps',
    'add_activity',
    'add_gym_session',
    'add_cardio',
    'add_calories',
    'delete_gym_session_calendar',
]
