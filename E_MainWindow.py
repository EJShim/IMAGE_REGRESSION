from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import math
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

class E_MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(E_MainWindow, self).__init__(parent)        

        self.plot = None
        self.selectedImage = None
        self.binaryImage = None
        self.lines = []

        #Initialize Layout
        self.setWindowTitle("Regression")

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        importAction = QAction("Import Image", self)
        importAction.triggered.connect(self.import_image)
        toolbar.addAction(importAction)


        drawAction = QAction("Regression Line", self)
        drawAction.triggered.connect(self.draw_regression_plane)
        toolbar.addAction(drawAction)

        threshsolider = QSlider(Qt.Horizontal)
        threshsolider.setRange(0, 255)
        threshsolider.setSingleStep(1)
        threshsolider.setSliderPosition(100)
        toolbar.addWidget(threshsolider)
        threshsolider.valueChanged.connect(self.slider_change)


        #Layout
        MainLayout = QHBoxLayout()
        centralWidget.setLayout(MainLayout)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)        
        MainLayout.addWidget(self.canvas)

        #Add Button Events
        self.initialize_button_events()
        
    def initialize_button_events(self):
        self.buttonClicked = False
        self.startPos = None
        self.curPos = None
        self.patch = None
        
        self.canvas.mpl_connect('button_press_event', self.on_button_clicked)
        self.canvas.mpl_connect('button_release_event', self.on_button_up)
        self.canvas.mpl_connect('motion_notify_event', self.on_button_move)

    def slider_change(self, value):
        if self.selectedImage == None:
            return
            
        self.binaryImage = self.binarize_array(self.selectedImage, value)
        self.show_image(self.binaryImage)


    def import_image(self):
        
        path = QFileDialog.getOpenFileName(self, "import Images", './', 'image files(*.png *.jpg) ;; image files(*.jpg)')

        image = Image.open(path[0])

        #Binarize Image
        image = image.convert('L')
        image = np.array(image)
        self.binaryImage = self.binarize_array(image)

        self.show_image(self.binaryImage)

        self.selectedImage = image

    def show_image(self, image):
        self.figure.clf()
        self.lines = []
        self.patch = None
        
        self.plot = self.figure.add_subplot(111)        
        self.plot.imshow(image)      

        self.canvas.draw()

    def draw_rectangle(self, start, cur):        
        if self.plot == None: return
        
        width = cur[0] - start[0]
        height = cur[1] - start[1]        

        if not self.patch == None: self.patch.remove()
        self.patch = patches.Rectangle(start, width, height, fill=False, edgecolor="red" )
        self.plot.add_patch( self.patch )

        self.canvas.draw()

    def binarize_array(self, numpy_array, threshold=100):
        numpy_array = (numpy_array > threshold) * 1.0
        return numpy_array

    def on_button_clicked(self, event):
        if event.xdata == None: return
        self.buttonClicked = True        
        self.startPos = [event.xdata, event.ydata]

    def on_button_move(self, event):        
        if self.buttonClicked:            
            self.curPos = [event.xdata, event.ydata]
            self.draw_rectangle(self.startPos, self.curPos)
    
    def on_button_up(self, event):    
        self.buttonClicked = False

    def draw_regression_plane(self):
        if self.binaryImage == None: return        
        pointX = []
        pointY = []

        for i in range(int(self.startPos[0]), int(self.curPos[0])):
            for j in range(int(self.startPos[1]), int(self.curPos[1])):
                if not self.binaryImage[j][i] == 0.0:
                    pointX.append(i)
                    pointY.append(j)

        if len(pointX) < 1: return


        lineStart = pointX[0]
        lineEnd = pointX[len(pointX)-1]


        pointX = np.asarray(pointX)
        pointY = np.asarray(pointY)
        
        # self.plot.scatter(pointX, pointY)
        # self.canvas.draw()

        pointX = pointX.reshape((pointX.shape[0], 1))
        pointY = pointY.reshape((pointY.shape[0], 1))

        regr = linear_model.LinearRegression()
        regr.fit(pointX, pointY)

        
        imgRange = self.binaryImage.shape
        lineX = [[lineStart-200],[lineEnd+200]]
        lineX = np.asarray(lineX)

        lineY = np.zeros((2, 1)) 
        lineY = regr.predict(lineX)
        

        lineStart = [lineX[0][0], lineY[0][0]]
        lineEnd = [lineX[1][0], lineY[1][0]]
        line = [lineStart, lineEnd]                
        self.lines.append(line)

        
        self.plot.plot(lineX, lineY, color='blue', linewidth=3)
        self.canvas.draw()


        if len(self.lines) < 2:
            return
        elif len(self.lines) == 2:
            self.find_cross(self.lines[0], self.lines[1])
        else:
            for i in range(len(self.lines)):
                if i == len(self.lines)-1:
                    self.find_cross(self.lines[i], self.lines[0])
                else:
                    self.find_cross(self.lines[i], self.lines[i+1])
            
        

    def find_cross(self, line1, line2):
        

        x1 = line1[0][0]
        y1 = line1[0][1]
        x2 = line1[1][0]
        y2 = line1[1][1]
        x3 = line2[0][0]
        y3 = line2[0][1]
        x4 = line2[1][0]
        y4 = line2[1][1]

        #Check line crossing
        cross = ((x1*y2 - x2*y1) + (x2*y3 - x3*y2) + (x3*y1 - x1*y3)) * ((x1*y2 - x2*y1) + (x2*y4 - x4*y2) + (x4*y1 - x1*y4))
        
        if cross >= 0:
            return


        m1 = (y2 - y1) / (x2 - x1)
        m2 = (y4 - y3) / (x4 - x3)

        rad = math.atan(m1) - math.atan(m2)
        deg = math.fabs(math.degrees(rad))

        anot = deg

        crossX = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
        crossY = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))

        # self.plot.plot(crossX, crossY, 'o')
        self.plot.annotate(anot, color='red', fontsize=10, xy=(crossX, crossY), xytext=(crossX, crossY - 100), arrowprops=dict(facecolor='red', shrink=0.01))
        self.canvas.draw()        


