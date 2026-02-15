import Colors


class Cell(object):
    def __init__(self):
        self.colors = Colors.Colors()
        self.current_value = " "
        self.secret_value = self.colors.set_grey("0")

    def get_current_value(self):
        return self.current_value

    def get_secret_value(self):
        return self.secret_value

    def set_current_value(self, value: str):
        self.current_value = value

    def set_value(self, value):
        self.secret_value = value

    def up_value(self):
        if self.secret_value == self.colors.set_grey("0"):
            self.secret_value = self.colors.set_blue("1")
        elif self.secret_value == self.colors.set_blue("1"):
            self.secret_value = self.colors.set_beige("2")
        elif self.secret_value == self.colors.set_beige("2"):
            self.secret_value = self.colors.set_pink("3")
        elif self.secret_value == self.colors.set_pink("3"):
            self.secret_value = self.colors.set_red("4")
        elif self.secret_value == self.colors.set_red("4"):
            self.secret_value = self.colors.set_yellow("5")
        elif self.secret_value == self.colors.set_yellow("5"):
            self.secret_value = self.colors.set_green("6")
        elif self.secret_value == self.colors.set_green("6"):
            self.secret_value = self.colors.set_green2("7")
        elif self.secret_value == self.colors.set_green2("7"):
            self.secret_value = self.colors.set_red2("8")

    def open(self):
        self.current_value = self.secret_value
