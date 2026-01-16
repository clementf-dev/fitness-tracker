# -*- coding: utf-8 -*-
file_path = 'tracker/templates/tracker/calories_dashboard.html'

content = open(file_path, 'r', encoding='utf-8').read()

# Fix the template syntax error
content = content.replace('meal.code==template.meal_type', 'meal.code == template.meal_type')

open(file_path, 'w', encoding='utf-8').write(content)
print('Fixed template syntax!')
