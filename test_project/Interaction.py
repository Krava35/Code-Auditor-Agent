import pickle

import Exceptions
import Field


class Interaction(object):
    def __init__(self):
        self.data = []
        self.x = None
        self.y = None
        self.action = None
        self.length = None
        self.width = None
        self.bombs = None
        self.file = None

    def set_data(self, move: str):
        self.data = move.replace("[", "").replace("]", "").replace(" ", "").split(",")
        if len(self.data) != 3:
            raise Exceptions.MoveFormatException("Move must be entered like this: [X, Y, Action]")

    def set_x(self):
        self.x = int(self.data[0])
        if (self.x < 0) or (self.x >= self.width):
            raise Exceptions.XValueException("X must be positive and less than field width")

    def set_y(self):
        self.y = int(self.data[1])
        if (self.y < 0) or (self.y >= self.length):
            raise Exceptions.YValueException("Y must be positive and less than field length")

    def set_action(self):
        if (self.data[2] != "Flag") and (self.data[2] != "Open"):
            raise Exceptions.ActionFormatException("Action must be Flag or Open")
        self.action = self.data[2]

    def set_length(self):
        while True:
            try:
                self.length = int(input("Input field length: "))
                if self.length <= 0:
                    raise Exceptions.LengthNegativeException("Length must be positive")
                break
            except Exceptions.LengthNegativeException as exception:
                print(exception)
            except ValueError:
                print("Length must be positive integer")

    def set_width(self):
        while True:
            try:
                self.width = int(input("Input field width: "))
                if self.width <= 0:
                    raise Exceptions.WidthNegativeException("Width must be positive")
                break
            except Exceptions.WidthNegativeException as exception:
                print(exception)
            except ValueError:
                print("Width must be positive integer")

    def set_bombs(self):
        while True:
            try:
                self.bombs = int(input("Input number of bombs: "))
                if self.bombs <= 0:
                    raise Exceptions.BombsNegativeException("Number of bombs must be positive ")
                if self.bombs > self.width * self.length:
                    raise Exceptions.NumberOfBombsException("The number of bombs cannot exceed the number of cells")
                break
            except Exceptions.BombsNegativeException as exception:
                print(exception)
            except Exceptions.NumberOfBombsException as exception:
                print(exception)
            except ValueError:
                print("Number of bombs must be positive integer")

    def set_parameters(self):
        while True:
            try:
                self.set_length()
                self.set_width()
                self.set_bombs()
                break
            except Exceptions.LengthNegativeException as exception:
                print(exception)
            except Exceptions.WidthNegativeException as exception:
                print(exception)
            except Exceptions.BombsNegativeException as exception:
                print(exception)
            except Exceptions.NumberOfBombsException as exception:
                print(exception)

    def get_move(self, field):
        while True:
            try:
                move = input("Input move. '[X, Y, Action]' or 'Save': ")
                if move == "Save":
                    self.save_game(field)
                    break
                self.set_data(move)
                self.set_x()
                self.set_y()
                self.set_action()
                break
            except Exceptions.MoveFormatException as exception:
                print(exception)
            except Exceptions.XValueException as exception:
                print(exception)
            except Exceptions.YValueException as exception:
                print(exception)
            except Exceptions.ActionFormatException as exception:
                print(exception)

    def load_game(self):
        try:
            path = input("Input file path (format: '.pickle'): ")
            file = open(path, "rb")
            return pickle.load(file)
        except FileNotFoundError:
            print("Game file not founded")

    def save_game(self, field):
        file_name = input("Input name for file: ") + ".pickle"
        file = open(file_name, "wb")
        pickle.dump(field, file)

    def start_ask(self):
        print("If you want start new game type 'New' оr if you want load the game type 'Load'")
        print("If you want close close app type 'Exit'")
        return input(": ")

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_action(self):
        return self.action

    def get_length(self):
        return self.length

    def get_width(self):
        return self.width

    def get_number_of_bombs(self):
        return self.bombs
