import sys
from PyQt5.QtWidgets import *
from E_MainWindow import *


app = QApplication([])

window = E_MainWindow()

window.resize(1500, 800)
window.show()
sys.exit(app.exec_())
