# -*- coding: utf-8 -*-
file_path = 'tracker/templates/tracker/calories_dashboard.html'

content = open(file_path, 'r', encoding='utf-8').read()

# Fix ALL instances of the template syntax error
content = content.replace('meal.code==template.meal_type', 'meal.code == template.meal_type')

# Write it back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify the fix
content_after = open(file_path, 'r', encoding='utf-8').read()
if 'meal.code==template.meal_type' in content_after:
    print('ERROR: Fix did not apply!')
else:
    print('SUCCESS: Template syntax fixed!')
    # Count occurrences of the correct pattern
    count = content_after.count('meal.code == template.meal_type')
    print(f'Found {count} correctly formatted instance(s).')
