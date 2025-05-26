"""
Script para criar o executável do sistema de finanças pessoais.
"""
import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--name=Financas_Pessoais',
    '--windowed',
    '--onefile',
    '--add-data', '.env;.',
    '--hidden-import', 'PyQt5',
    '--hidden-import', 'pyodbc',
])