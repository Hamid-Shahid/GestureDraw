import sys
import cv2
import numpy as np
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QColor, QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton, 
                             QVBoxLayout, QWidget, QHBoxLayout, QColorDialog,
                             QButtonGroup, QSizePolicy)
import HandTrakingModule as htm


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDrawingState()
        self.initCamera()
        
        # Text functionality initialization
        self.typed_text = ""
        self.Kb_Flag = False
        self.text_position = (0, 0)
        self.COLOR_SELECTED = (0, 0, 0)  # Will be updated with color picker

    def initUI(self):
        self.setWindowTitle('Hand Tracking Drawing App')
        self.setGeometry(100, 100, 1280, 720)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Create and add the main toolbar
        self.createToolbar(main_layout)
        
        # Create and add the sub-toolbar (for tool options)
        self.sub_toolbar = QHBoxLayout()
        main_layout.addLayout(self.sub_toolbar)

        # Video display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.image_label, 1)

        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 0)
        main_layout.setStretch(2, 1)
    
    def keyPressEvent(self, event):
        if self.Kb_Flag:
            key = event.key()
            text = event.text()
            
            if key == Qt.Key_Backspace:
                self.typed_text = self.typed_text[:-1]
            elif key == Qt.Key_Return:
                # Handle text commit
                if len(self.lmList) > 0 and len(self.lmList[0]) > 8:
                    x, y = self.lmList[0][8][1], self.lmList[0][8][2]
                else:
                    x, y = self.text_position
                
                cv2.putText(self.canvas, self.typed_text, (x, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, self.drawing_color, 2)
                self.typed_text = ""
            elif key == Qt.Key_Space:  # Explicitly handle space for text
                self.typed_text += ' '
            elif text:
                self.typed_text += text
            event.accept()
        else:
            # Handle Enter for shapes
            if event.key() == Qt.Key_Return:
                self.commitShapeToCanvas()
                event.accept()
            else:
                super().keyPressEvent(event)

    def commitShapeToCanvas(self):
        if self.lmList and len(self.lmList[0]) > 8:
            hand = self.lmList[0]
            index_finger = next((lm for lm in hand if lm[0] == 8), None)
            thumb = next((lm for lm in hand if lm[0] == 4), None)
            
            if index_finger and thumb:
                x1, y1 = index_finger[1], index_finger[2]
                x2, y2 = thumb[1], thumb[2]
                thickness = 5 if self.eraser_mode else 5

                if self.current_tool == 'rectangle':
                    cv2.rectangle(self.canvas, (x1, y1), (x2, y2), 
                                self.drawing_color, thickness)
                elif self.current_tool == 'circle':
                    radius = int(np.hypot(x2 - x1, y2 - y1))
                    cv2.circle(self.canvas, (x1, y1), radius, 
                              self.drawing_color, thickness)
                elif self.current_tool == 'line':
                    cv2.line(self.canvas, (x1, y1), (x2, y2), 
                            self.drawing_color, thickness)

    def createToolbar(self, main_layout):
        # Primary tools
        toolbar = QHBoxLayout()
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)

        # Pen Button
        self.pen_btn = QPushButton('Pen')
        self.pen_btn.setCheckable(True)
        self.pen_btn.clicked.connect(self.showPenOptions)
        toolbar.addWidget(self.pen_btn)
        self.tool_group.addButton(self.pen_btn)

        # Shape Button
        self.shape_btn = QPushButton('Shapes')
        self.shape_btn.setCheckable(True)
        self.shape_btn.clicked.connect(self.showShapeOptions)
        toolbar.addWidget(self.shape_btn)
        self.tool_group.addButton(self.shape_btn)

        # Color Button
        self.color_btn = QPushButton('Color')
        self.color_btn.clicked.connect(self.chooseColor)
        toolbar.addWidget(self.color_btn)

        self.text_btn = QPushButton('Text')
        self.text_btn.setCheckable(True)
        self.text_btn.clicked.connect(lambda: self.setTool('text'))
        toolbar.addWidget(self.text_btn)
        self.tool_group.addButton(self.text_btn)

        # Eraser Button
        self.eraser_btn = QPushButton('Eraser')
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.clicked.connect(self.activateEraser)
        toolbar.addWidget(self.eraser_btn)
        self.tool_group.addButton(self.eraser_btn)

        # Clear Button
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self.clearCanvas)
        toolbar.addWidget(self.clear_btn)

        main_layout.addLayout(toolbar)

    def showPenOptions(self):
        self.clearSubToolbar()
        
        self.pen_group = QButtonGroup(self)
        self.pen_group.setExclusive(True)

        # Brush
        brush_btn = QPushButton('Brush')
        brush_btn.setCheckable(True)
        brush_btn.setChecked(True)
        brush_btn.clicked.connect(lambda: self.setTool('brush'))
        self.sub_toolbar.addWidget(brush_btn)
        self.pen_group.addButton(brush_btn)

        # Straight Line
        line_btn = QPushButton('Line')
        line_btn.setCheckable(True)
        line_btn.clicked.connect(lambda: self.setTool('line'))
        self.sub_toolbar.addWidget(line_btn)
        self.pen_group.addButton(line_btn)

    def showShapeOptions(self):
        self.clearSubToolbar()
        
        self.shape_group = QButtonGroup(self)
        self.shape_group.setExclusive(True)

        # Rectangle
        rect_btn = QPushButton('Rectangle')
        rect_btn.setCheckable(True)
        rect_btn.clicked.connect(lambda: self.setTool('rectangle'))
        self.sub_toolbar.addWidget(rect_btn)
        self.shape_group.addButton(rect_btn)

        # Circle
        circle_btn = QPushButton('Circle')
        circle_btn.setCheckable(True)
        circle_btn.clicked.connect(lambda: self.setTool('circle'))
        self.sub_toolbar.addWidget(circle_btn)
        self.shape_group.addButton(circle_btn)

        # Triangle
        triangle_btn = QPushButton('Triangle')
        triangle_btn.setCheckable(True)
        triangle_btn.clicked.connect(lambda: self.setTool('triangle'))
        self.sub_toolbar.addWidget(triangle_btn)
        self.shape_group.addButton(triangle_btn)

    def clearSubToolbar(self):
        while self.sub_toolbar.count():
            item = self.sub_toolbar.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def initDrawingState(self):
        self.current_tool = 'brush'
        self.drawing_color = (0, 0, 0)  # Default color
        self.eraser_mode = False
        self.canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.xp, self.yp = 0, 0
        self.detector = htm.handDetector(detectionCon=0.85)

    def initCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)

    def setTool(self, tool):
        self.current_tool = tool
        if tool == 'text':
            self.Kb_Flag = True
        else:
            self.Kb_Flag = False

    def chooseColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawing_color = (color.blue(), color.green(), color.red())
            self.COLOR_SELECTED = self.drawing_color  # Update text color
            self.eraser_mode = False
            self.eraser_btn.setChecked(False)

    def activateEraser(self):
        self.eraser_mode = True
        self.drawing_color = (0, 0, 0)  # Black color for eraser

    def clearCanvas(self):
        self.canvas = np.zeros((720, 1280, 3), dtype=np.uint8)

    def updateFrame(self):
        success, img = self.cap.read()
        if not success:
            return

        img = cv2.flip(img, 1)
        self.detector.findHands(img)
        self.lmList = self.detector.findPosition(img, draw=False)
        fingers = self.detector.fingersUp()

        # Text functionality
        if self.Kb_Flag:
            cv2.putText(img, f"Typing: {self.typed_text}", (200, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            if len(self.lmList) > 0 and len(self.lmList[0]) > 8:
                x, y = self.lmList[0][8][1], self.lmList[0][8][2]
                self.text_position = (x, y)
                cv2.circle(img, (x, y), 5, (0, 255, 0), cv2.FILLED)

        if self.lmList:
            self.processGestures(img, self.lmList, fingers)

        img = self.applyCanvas(img)
        self.displayImage(img)

    def processGestures(self, img, lmList, fingers):
        hand = lmList[0]
        index_finger = next((lm for lm in hand if lm[0] == 8), None)
        thumb = next((lm for lm in hand if lm[0] == 4), None)
        middle_finger = next((lm for lm in hand if lm[0] == 12), None)
        
        if not all([index_finger, thumb, middle_finger]):
            # Skip processing if any required landmarks are missing
            self.xp, self.yp = 0, 0
            return

        x1, y1 = index_finger[1], index_finger[2]  # Index finger
        x2, y2 = thumb[1], thumb[2]                # Thumb
        x3, y3 = middle_finger[1], middle_finger[2] # Middle finger

        thickness = 5 if self.eraser_mode else 5

        if self.current_tool == 'brush' and fingers[1] and not any(fingers[2:]):
            if self.xp == 0 and self.yp == 0:
                self.xp, self.yp = x1, y1
            cv2.line(img, (self.xp, self.yp), (x1, y1), self.drawing_color, thickness)
            cv2.line(self.canvas, (self.xp, self.yp), (x1, y1), self.drawing_color, thickness)
            self.xp, self.yp = x1, y1
        else:
            self.xp, self.yp = 0, 0

        if self.current_tool == 'line' and fingers[1] and fingers[0]:
            cv2.line(img, (x1, y1), (x2, y2), self.drawing_color, thickness)

        if self.current_tool == 'rectangle' and fingers[1] and fingers[0]:
            cv2.rectangle(img, (x1, y1), (x2, y2), self.drawing_color, thickness)

        if self.current_tool == 'circle' and fingers[1] and fingers[0]:
            radius = int(np.hypot(x2 - x1, y2 - y1))
            cv2.circle(img, (x1, y1), radius, self.drawing_color, thickness)

    def applyCanvas(self, img):
        img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        return cv2.bitwise_or(img, self.canvas)

    def displayImage(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qt_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec_())