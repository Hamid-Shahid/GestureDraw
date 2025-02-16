import cv2
from os.path import dirname, join
# import cvzone
from cvzone.Utils import cornerRect
import Button as btn
import sys


class GUI:

    visible_toolbar = False
    visible_colorbar = False
    visible_shapebar = False
    visible_penbar = False

    def __init__(self):
        # Get the directory where the script is located
        script_dir = dirname(__file__)

        if getattr(sys, 'frozen', False):
            # If the script is run as a bundled executable (e.g., PyInstaller)
            self.folderPath = join(sys._MEIPASS, 'GUI_Items')
        else:
            # If the script is run normally
            self.folderPath = join(script_dir, 'GUI_Items')


        self.toolbar = cv2.imread(f'{self.folderPath}/toolbar.png')
        # print(self.toolbar)
        self.colorbar = cv2.imread(f'{self.folderPath}/colorbar.png')
        self.shapebar = cv2.imread(f'{self.folderPath}/shapebar.png')
        self.penbar = cv2.imread(f'{self.folderPath}/penbar.png')
        self.keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
                    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
        self.finalText = ""

    def show_toolbar(self, img):
        img[15:110,320:960] = self.toolbar

    def show_colorbar(self, img):
        img[120:220,415:865] = self.colorbar

    def show_shapebar(self, img):
        img[120:215,500:778] = self.shapebar

    def show_penbar(self, img):
        img[120:215,515:781] = self.penbar

    def reset_secondarybars(self):
        GUI.visible_penbar = False
        GUI.visible_colorbar = False
        GUI.visible_shapebar = False

    def handleGUI(self, img):
        if GUI.visible_toolbar:
            self.show_toolbar(img)

        if GUI.visible_colorbar:
            self.show_colorbar(img)

        if GUI.visible_shapebar:
            self.show_shapebar(img)

        if GUI.visible_penbar:
            self.show_penbar(img)

    def draw(self,img):
        self.buttonList = []
        for i in range(len(self.keys)):
            for j, key in enumerate(self.keys[i]):
                self.buttonList.append(btn.Button([100 * j + 150, 100 * i + 150], key))

        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                              20, rt=0)
            cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 65),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return img
