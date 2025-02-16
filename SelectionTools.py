import GUI
class SelectionTools:
    COLOR_PURPLE = (255, 0, 255)
    COLOR_BLUE = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_RED = (0, 0, 255)
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    SELECTED_COLOR = COLOR_BLACK

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.gui = GUI.GUI()
        self.keyboardFlag = False
        self.eraserFlag = False
        self.clearCanvas = False

    def scale_x(self, original_x):
        return (original_x / 1366) * self.screen_width

    def scale_y(self, original_y):
        return (original_y / 768) * self.screen_height

    def check_tool_selection(self, x, y):
        toolbar_start_x = self.scale_x(320)
        toolbar_end_x = self.scale_x(960)
        toolbar_start_y = self.scale_y(15)
        toolbar_end_y = self.scale_y(110)

        if toolbar_start_x < x < toolbar_end_x and toolbar_start_y < y < toolbar_end_y:
            # Pen Tool
            pen_start_x = self.scale_x(345)
            pen_end_x = self.scale_x(445)
            if pen_start_x < x < pen_end_x:
                self.gui.reset_secondarybars()
                GUI.GUI.visible_penbar = True
                self.keyboardFlag = False
                self.eraserFlag = False
                self.clearCanvas = False

            # Shape Tool
            shape_start_x = self.scale_x(425)
            shape_end_x = self.scale_x(535)
            if shape_start_x < x < shape_end_x:
                self.gui.reset_secondarybars()
                GUI.GUI.visible_shapebar = True
                self.keyboardFlag = False
                self.eraserFlag = False
                self.clearCanvas = False

            # Color Tool
            color_start_x = self.scale_x(516)
            color_end_x = self.scale_x(625)
            if color_start_x < x < color_end_x:
                self.gui.reset_secondarybars()
                GUI.GUI.visible_colorbar = True
                self.keyboardFlag = False
                self.eraserFlag = False
                self.clearCanvas = False

            # Eraser Tool
            eraser_start_x = self.scale_x(605)
            eraser_end_x = self.scale_x(715)
            if eraser_start_x < x < eraser_end_x:
                self.gui.reset_secondarybars()
                self.eraserFlag = True
                self.keyboardFlag = False
                self.clearCanvas = False

            # Keyboard Tool
            keyboard_start_x = self.scale_x(695)
            keyboard_end_x = self.scale_x(800)
            if keyboard_start_x < x < keyboard_end_x:
                self.gui.reset_secondarybars()
                self.keyboardFlag = True
                self.eraserFlag = False
                self.clearCanvas = False

            # Clear All Tool
            clear_start_x = self.scale_x(860)
            clear_end_x = self.scale_x(920)
            if clear_start_x < x < clear_end_x:
                self.gui.reset_secondarybars()
                self.keyboardFlag = False
                self.eraserFlag = False
                self.clearCanvas = True

            # Setting Tool
            setting_start_x = self.scale_x(925)
            setting_end_x = self.scale_x(960)
            if setting_start_x < x < setting_end_x:
                self.gui.reset_secondarybars()
                self.keyboardFlag = False
                self.eraserFlag = False
                self.clearCanvas = False

    def check_color(self, x, y):
        color_bar_y_start = self.scale_y(143)
        color_bar_y_end = self.scale_y(193)
        if color_bar_y_start < y < color_bar_y_end:
            # Black
            black_start_x = self.scale_x(445)
            black_end_x = self.scale_x(545)
            if black_start_x < x < black_end_x:
                self.gui.reset_secondarybars()
                return self.COLOR_BLACK

            # White
            white_start_x = self.scale_x(530)
            white_end_x = self.scale_x(630)
            if white_start_x < x < white_end_x:
                self.gui.reset_secondarybars()
                return self.COLOR_WHITE

            # Red
            red_start_x = self.scale_x(615)
            red_end_x = self.scale_x(715)
            if red_start_x < x < red_end_x:
                self.gui.reset_secondarybars()
                return self.COLOR_RED

            # Green
            green_start_x = self.scale_x(700)
            green_end_x = self.scale_x(800)
            if green_start_x < x < green_end_x:
                self.gui.reset_secondarybars()
                return self.COLOR_GREEN

            # Blue
            blue_start_x = self.scale_x(785)
            blue_end_x = self.scale_x(885)
            if blue_start_x < x < blue_end_x:
                self.gui.reset_secondarybars()
                return self.COLOR_BLUE

    def check_pen(self, x, y):
        pen_bar_y_start = self.scale_y(143)
        pen_bar_y_end = self.scale_y(193)
        if pen_bar_y_start < y < pen_bar_y_end:
            # Brush
            brush_start_x = self.scale_x(530)
            brush_end_x = self.scale_x(630)
            if brush_start_x < x < brush_end_x:
                self.gui.reset_secondarybars()
                return "Brush"

            # Straight Line
            line_start_x = self.scale_x(615)
            line_end_x = self.scale_x(715)
            if line_start_x < x < line_end_x:
                self.gui.reset_secondarybars()
                return "StraightLine"

    def check_shape(self, x, y):
        shape_bar_y_start = self.scale_y(143)
        shape_bar_y_end = self.scale_y(193)
        if shape_bar_y_start < y < shape_bar_y_end:
            # Rectangle
            rect_start_x = self.scale_x(530)
            rect_end_x = self.scale_x(630)
            if rect_start_x < x < rect_end_x:
                self.gui.reset_secondarybars()
                return "Rectangle"

            # Triangle
            tri_start_x = self.scale_x(615)
            tri_end_x = self.scale_x(715)
            if tri_start_x < x < tri_end_x:
                self.gui.reset_secondarybars()
                return "Triangle"

            # Circle
            circle_start_x = self.scale_x(730)
            circle_end_x = self.scale_x(830)
            if circle_start_x < x < circle_end_x:
                self.gui.reset_secondarybars()
                return "Circle"

    def checkKeyboard(self, x, y):
        keyboard_bar_y_start = self.scale_y(143)
        keyboard_bar_y_end = self.scale_y(193)
        if keyboard_bar_y_start < y < keyboard_bar_y_end:
            # Keyboard Button
            key_start_x = self.scale_x(785)
            key_end_x = self.scale_x(835)
            if key_start_x < x < key_end_x:
                self.gui.reset_secondarybars()
                return True