import sys
import cv2
from numpy import zeros, uint8
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSizePolicy
import GUI
import SelectionTools as slt
import HandTrakingModule as htm
from time import sleep
# import pygame
# pygame.init()
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Adjust as needed
# screen_width, screen_height = screen.get_size()
import tkinter as tk

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

print(f"Screen Resolution: {screen_width}x{screen_height}")


slc = slt.SelectionTools(screen_width,screen_height)
gui = GUI.GUI()

TOOL_THICKNESS = 5
ERASER_THICKNESS = 20

detector = htm.handDetector(detectionCon=0.85)

# imgCanvas = np.zeros((720, 1280, 3), np.uint8)
imgCanvas = zeros((720, 1280, 3), dtype=uint8)

GUI.GUI.visible_toolbar = True

class FaceDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.draw_onClick_flag = False
        self.Kb_Flag = False
        self.eraser_Flag = False
        self.clear_canvas_flag = False

        self.COLOR_SELECTED = (0, 0, 0)
        self.shape_selected = None
        self.pen_selected = None

        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 1280)
        self.capture.set(4, 720)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.xp, self.yp = 0, 0

        # Temporary variables to store coordinates
        self.rect_start = None
        self.rect_end = None
        self.straight_line_start = None
        self.straight_line_end = None

        # Mouse position tracking
        self.mouse_x, self.mouse_y = 0, 0

    def initUI(self):
        self.setWindowTitle('Face Detection App')

        # Create a label to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setScaledContents(True)

        # Create a button to quit the application
        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self.close)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.quit_button)

        # Set the layout on a central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Maximize the window
        self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #for rectangle and straaight line
            self.mouse_x, self.mouse_y = event.x(), event.y()
            if not (320 < self.mouse_x < 960 and 23 < self.mouse_y < 224):
                self.draw_onClick_flag = True
            # print(f"Left mouse button clicked!{self.mouse_y}")
            slc.check_tool_selection(self.mouse_x, self.mouse_y)
            self.Kb_Flag = slc.keyboardFlag
            self.eraser_Flag = slc.eraserFlag
            self.clear_canvas_flag = slc.clearCanvas        
            if self.eraser_Flag:
                self.COLOR_SELECTED = (0, 0, 0)
            if gui.visible_colorbar:
                self.COLOR_SELECTED = slc.check_color(self.mouse_x, self.mouse_y)
            if gui.visible_penbar:
                self.pen_selected = slc.check_pen(self.mouse_x, self.mouse_y)
                self.shape_selected = None
            if gui.visible_shapebar:
                self.shape_selected = slc.check_shape(self.mouse_x, self.mouse_y)
                self.pen_selected = None


    def update_frame(self):
        if self.clear_canvas_flag:
            imgCanvas[:] = (0, 0, 0)  # Reset to a blank black canvas
            self.clear_canvas_flag = False  # Reset the flag after clearing
        success, img = self.capture.read()
        img = cv2.flip(img, 1)  # inverting the image

        # Find landmarks and process fingers
        detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            if len(lmList[0]) != 0:
                x1, y1 = lmList[0][8][1:]  # tip of index finger
                x2, y2 = lmList[0][4][1:]  # tip of thumb
                x3, y3 = lmList[0][12][1:]

        fingers = detector.fingersUp()

        if len(fingers) != 0:
            # Handle virtual keyboard logic
            if self.Kb_Flag:
                img = gui.draw(img)
                if len(lmList) > 0:
                    for button in gui.buttonList:
                        x, y = button.pos
                        w, h = button.size

                        if x < lmList[0][8][1] < x + w and y < lmList[0][8][2] < y + h:
                            cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            l, _, _ = detector.findDistance(8, 12, img, draw=False)

                            # when clicked
                            if l < 40:
                                cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                                cv2.putText(img, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                                gui.finalText += button.text
                                sleep(0.5)

                cv2.rectangle(img, (150, 450), (1050, 850), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, gui.finalText, (210, 520),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5)

            # Rectangle Mode (Thumb and Index Finger up)
            elif self.shape_selected == "Rectangle" and fingers[1] and fingers[0]:  # Assuming thumb is fingers[0]
                self.rect_start = (x1, y1)
                self.rect_end = (x2, y2)
                cv2.rectangle(img, (x1, y1), (x2, y2), self.COLOR_SELECTED, TOOL_THICKNESS)
                if self.draw_onClick_flag == True:
                    self.draw_onClick_flag = False
                    cv2.rectangle(img, self.rect_start, self.rect_end, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.rectangle(imgCanvas, self.rect_start, self.rect_end, self.COLOR_SELECTED, TOOL_THICKNESS)
                    self.rect_start = None
                    self.rect_end = None
            
            elif self.shape_selected == "Circle" and fingers[1] and fingers[0]:  # Assuming thumb is fingers[0]
                center = (x1, y1)
                radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)  # Euclidean distance as radius
                cv2.circle(img, center, radius, self.COLOR_SELECTED, TOOL_THICKNESS)
                if self.draw_onClick_flag:
                    self.draw_onClick_flag = False
                    cv2.circle(img, center, radius, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.circle(imgCanvas, center, radius, self.COLOR_SELECTED, TOOL_THICKNESS)

            elif self.shape_selected == "Triangle" and fingers[1] and fingers[0] and fingers[2]:  # Three fingers
                pt1 = (x1, y1)  # Index finger
                pt2 = (x2, y2)  # Thumb
                pt3 = (x3, y3)  # Middle finger

                cv2.line(img, pt1, pt2, self.COLOR_SELECTED, TOOL_THICKNESS)
                cv2.line(img, pt2, pt3, self.COLOR_SELECTED, TOOL_THICKNESS)
                cv2.line(img, pt3, pt1, self.COLOR_SELECTED, TOOL_THICKNESS)

                if self.draw_onClick_flag:
                    self.draw_onClick_flag = False
                    cv2.line(img, pt1, pt2, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.line(img, pt2, pt3, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.line(img, pt3, pt1, self.COLOR_SELECTED, TOOL_THICKNESS)
                    
                    cv2.line(imgCanvas, pt1, pt2, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.line(imgCanvas, pt2, pt3, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.line(imgCanvas, pt3, pt1, self.COLOR_SELECTED, TOOL_THICKNESS)

            elif self.pen_selected == "StraightLine" and fingers[1] and fingers[0]:
                self.straight_line_start = (x1, y1)
                self.straight_line_end = (x2, y2)
                cv2.line(img, (x1, y1), (x2, y2), self.COLOR_SELECTED, TOOL_THICKNESS)
                if self.draw_onClick_flag == True:
                    self.draw_onClick_flag = False
                    cv2.line(img, self.straight_line_start, self.straight_line_end, self.COLOR_SELECTED, TOOL_THICKNESS)
                    cv2.line(imgCanvas, self.straight_line_start, self.straight_line_end, self.COLOR_SELECTED, TOOL_THICKNESS)
                    self.straight_line_start = None
                    self.straight_line_end = None

            else:
                if self.pen_selected == "Brush" and fingers[1] and not fingers[0] and not fingers[2] and not fingers[3] and not fingers[4]:
                    cv2.circle(img, (x1, y1), TOOL_THICKNESS, (255, 0, 255), cv2.FILLED)

                    if self.xp == 0 and self.yp == 0:
                        self.xp, self.yp = x1, y1

                    if self.COLOR_SELECTED == (0, 0, 0):
                        cv2.line(img, (self.xp, self.yp), (x1, y1), self.COLOR_SELECTED, ERASER_THICKNESS)
                        cv2.line(imgCanvas, (self.xp, self.yp), (x1, y1), self.COLOR_SELECTED, ERASER_THICKNESS)
                    else:
                        cv2.line(img, (self.xp, self.yp), (x1, y1), self.COLOR_SELECTED, TOOL_THICKNESS)
                        cv2.line(imgCanvas, (self.xp, self.yp), (x1, y1), self.COLOR_SELECTED, TOOL_THICKNESS)

                    self.xp, self.yp = x1, y1

                else:
                    self.xp, self.yp = 0, 0

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)
        gui.handleGUI(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        qt_image = QImage(img.data,
                          img.shape[1],
                          img.shape[0],
                          img.strides[0],
                          QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))


    def closeEvent(self, event):
        self.timer.stop()
        self.capture.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    face_detection_app = FaceDetectionApp()
    face_detection_app.show()
    sys.exit(app.exec_())