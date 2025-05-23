"""
Script para criar o executável do sistema de finanças pessoais.
"""
import PyInstaller.__main__
import os

# Caminho do ícone (se existir)
icon_path = os.path.join('resources', 'icon.ico')
icon_param = ['--icon', icon_path] if os.path.exists(icon_path) else []

PyInstaller.__main__.run([
    'main.py',
    '--name=Financas_Pessoais',
    '--windowed',
    '--onefile',
    '--add-data', '.env;.',
    '--hidden-import', 'PyQt5',
    '--hidden-import', 'pyodbc',
    *icon_param,
])