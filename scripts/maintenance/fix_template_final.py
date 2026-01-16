# -*- coding: utf-8 -*-
"""
Corriger définitivement le template
"""

# Lire le fichier
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\templates\tracker\calories_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corriger les lignes 1-10
lines[0] = "{% extends 'tracker/base.html' %}\n"
lines[1] = "{% load static %}\n"
lines[2] = "\n"
lines[3] = '{% block title %}Suivi Calories - {{ selected_date|date:"d/m/Y" }}{% endblock %}\n'
lines[4] = "\n"

# Supprimer les lignes 6-7 incorrectes si elles existent
if len(lines) > 6 and '{% load static' in lines[5]:
    del lines[5:7]

# Sauvegarder
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\templates\tracker\calories_dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Template corrige - lignes 1-7 nettoyees")
