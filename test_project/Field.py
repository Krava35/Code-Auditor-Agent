import random

import Cell
import Interaction


class Field(object):
    def __init__(self, interaction: Interaction.Interaction):
        self.interaction = interaction
        self.width = None
        self.length = None
        self.bombs = None
        self.field = None

    def set_parameters(self):
        self.interaction.set_parameters()
        self.length = self.interaction.get_length()
        self.width = self.interaction.get_width()
        self.bombs = self.interaction.get_number_of_bombs()

    def create_field(self):
        self.field = [[]]
        for i in range(int(self.length)):
            self.field.append([])
            for j in range(int(self.width)):
                self.field[i].append(Cell.Cell())
        self.set_bombs()

    def get_field(self):
        return self.field

    def get_cell(self, x: int, y: int):
        return self.field[y][x]

    def get_length(self):
        return self.length

    def get_width(self):
        return self.width

    def get_bombs(self):
        return self.bombs

    def set_bombs(self):
        count = 0
        while count < self.bombs:
            x = random.randint(0, self.length - 1)
            y = random.randint(0, self.width - 1)
            if self.field[x][y].get_secret_value() == "*":
                continue
            self.field[x][y].set_value("*")
            count += 1
            if self.length == 1 and self.width == 1:
                break
            elif self.length == 1 and y == 0:
                self.field[x][y + 1].up_value()
            elif self.length == 1 and y == (self.width - 1):
                self.field[x][y - 1].up_value()
            elif self.length == 1:
                self.field[x][y + 1].up_value()
                self.field[x][y - 1].up_value()
            elif self.width == 1 and x == 0:
                self.field[x + 1][y].up_value()
            elif self.width == 1 and x == (self.width - 1):
                self.field[x - 1][y].up_value()
            elif self.width == 1:
                self.field[x + 1][y].up_value()
                self.field[x - 1][y].up_value()
            elif x == 0 and y == 0:
                self.field[x + 1][y].up_value()
                self.field[x + 1][y + 1].up_value()
                self.field[x][y + 1].up_value()
            elif x == 0 and y == (self.width - 1):
                self.field[x][y - 1].up_value()
                self.field[x + 1][y - 1].up_value()
                self.field[x + 1][y].up_value()
            elif x == 0:
                self.field[x][y - 1].up_value()
                self.field[x + 1][y - 1].up_value()
                self.field[x + 1][y].up_value()
                self.field[x + 1][y + 1].up_value()
                self.field[x][y + 1].up_value()
            elif x == (self.length - 1) and y == (self.width - 1):
                self.field[x - 1][y].up_value()
                self.field[x - 1][y - 1].up_value()
                self.field[x][y - 1].up_value()
            elif y == (self.width - 1):
                self.field[x - 1][y].up_value()
                self.field[x - 1][y - 1].up_value()
                self.field[x][y - 1].up_value()
                self.field[x + 1][y - 1].up_value()
                self.field[x + 1][y].up_value()
            elif x == (self.length - 1) and y == 0:
                self.field[x - 1][y].up_value()
                self.field[x - 1][y + 1].up_value()
                self.field[x][y + 1].up_value()
            elif x == (self.length - 1):
                self.field[x][y + 1].up_value()
                self.field[x - 1][y + 1].up_value()
                self.field[x - 1][y].up_value()
                self.field[x - 1][y - 1].up_value()
                self.field[x][y - 1].up_value()
            elif y == 0:
                self.field[x + 1][y].up_value()
                self.field[x + 1][y + 1].up_value()
                self.field[x][y + 1].up_value()
                self.field[x - 1][y + 1].up_value()
                self.field[x - 1][y].up_value()
            else:
                self.field[x][y - 1].up_value()
                self.field[x - 1][y - 1].up_value()
                self.field[x - 1][y].up_value()
                self.field[x - 1][y + 1].up_value()
                self.field[x][y + 1].up_value()
                self.field[x + 1][y + 1].up_value()
                self.field[x + 1][y].up_value()
                self.field[x + 1][y - 1].up_value()

    def show_field(self):
        print("     ", end="")
        for i in range(self.width):
            print(str(i).center(6), end="")

        border = "    -"
        for i in range(self.width):
            border += "------"

        print("")
        print(border)
        for i in range(len(self.field) - 1):
            print(str(i).center(3) + " |  ", end="")
            for j in range(len(self.field[i])):
                if j != len(self.field[i]) - 1:
                    print(self.field[i][j].get_current_value(), end="  |  ")
                else:
                    print(self.field[i][j].get_current_value(), end="  |\n")
            print(border)

    def open_all(self):
        for i in range(len(self.field) - 1):
            for j in range(len(self.field[i])):
                if self.field[i][j].get_current_value() == " ":
                    self.field[i][j].open()
