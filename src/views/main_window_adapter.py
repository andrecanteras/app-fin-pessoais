"""
Adaptador para a janela principal que funciona com PyQt6, PyQt5 ou PySide6.
Este arquivo serve como uma camada de compatibilidade entre diferentes bibliotecas Qt.
"""

class MainWindowAdapter:
    """Adaptador para a janela principal que funciona com diferentes bibliotecas Qt."""
    
    def __init__(self, qt_lib):
        """
        Inicializa o adaptador com a biblioteca Qt apropriada.
        
        Args:
            qt_lib (str): Nome da biblioteca Qt a ser usada ('PyQt6', 'PyQt5' ou 'PySide6')
        """
        self.qt_lib = qt_lib
        
        if qt_lib == "PyQt6":
            from src.views.main_window import MainWindow
            self.window = MainWindow()
        elif qt_lib == "PyQt5":
            from src.views.main_window_pyqt5 import MainWindow
            self.window = MainWindow()
        elif qt_lib == "PySide6":
            from src.views.main_window_pyside6 import MainWindow
            self.window = MainWindow()
        else:
            raise ValueError(f"Biblioteca Qt não suportada: {qt_lib}")
    
    def show(self):
        """Mostra a janela principal."""
        self.window.show()