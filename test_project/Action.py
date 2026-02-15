import Field


class Action(object):
    def __init__(self, field: Field.Field):
        self.field = field

    def open(self, x: int, y: int):
        self.field.get_cell(x, y).open()
        return self.field.get_cell(x, y).get_current_value()

    def flag(self, x: int, y: int):
        if self.field.get_cell(x, y).get_current_value() == "F":
            self.field.get_cell(x, y).set_current_value(" ")
        else:
            self.field.get_cell(x, y).set_current_value("F")

    def check(self):
        bombs = self.field.get_bombs()
        flags = 0
        for i in range(self.field.get_width()):
            for j in range(self.field.get_length()):
                if self.field.get_cell(i, j).get_current_value() == "F" and self.field.get_cell(i, j).get_secret_value() == "*":
                    flags += 1
                if self.field.get_cell(i, j).get_current_value() == "*":
                    self.field.open_all()
                    print("\nGame over, you lose.")
                    return True
        if flags == bombs:
            self.field.open_all()
            print("\nGame over, you win!")
            return True
        return False
