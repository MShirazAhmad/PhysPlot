import sys

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from matplotlib.figure import Figure

from physplot_gui.figure_editor.gui import MainWindow


def create_splash() -> QSplashScreen:
    """
    Returns the start-up progress target the main window reports to.

    PhysPlot: the editor opens inside PhysPlot in a moment, so this splash screen is
    never shown and carries no image; it only receives the progress messages.
    """
    return QSplashScreen(QPixmap())


def main(figure: Figure | None = None) -> Figure:
    """
    Entry point of the application.

    Initializes the application, creates a splash screen, creates the main window,
    shows the window, finishes the splash screen, and starts the application event loop.
    """
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    splash = create_splash()
    window = MainWindow(splash, figure)
    window.show()
    splash.finish(window)

    figure = None

    def get_figure():
        figure = window.fm.figure

    app.aboutToQuit.connect(get_figure)
    app.exec()


if __name__ == "__main__":
    main()
