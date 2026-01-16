
import os

file_path = r'tracker/templates/tracker/calories_dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific Django syntax error
new_content = content.replace('meal.code==template.meal_type', 'meal.code == template.meal_type')

if content == new_content:
    print("No replacement made - string might be different?")
    # Let's try to be more flexible if exact string match fails
    import re
    new_content = re.sub(r'meal\.code==template\.meal_type', 'meal.code == template.meal_type', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("File updated successfully.")
with open(file_path, 'r', encoding='utf-8') as f:
    check = f.read()
    if 'meal.code == template.meal_type' in check:
        print("VERIFICATION: SUCCESS - Spaces found!")
    else:
        print("VERIFICATION: FAILED - Spaces NOT found!")
