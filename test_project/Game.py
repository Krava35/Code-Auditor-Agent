import sys
import time

import Action
import Field
import Interaction


class Game(object):
    def __init__(self, interaction: Interaction.Interaction, field: Field.Field, action: Action.Action):
        self.interaction = interaction
        self.field = field
        self.action = action

    def run(self):
        while True:
            try:
                answer = self.interaction.start_ask()
                if answer == "New":
                    self.field.set_parameters()
                    while True:
                        time_start = time.time()
                        self.field.create_field()
                        end = time.time()-time_start
                        if self.game():
                            print(end)
                            break
                elif answer == "Load":
                    self.field = self.interaction.load_game()
                    while True:
                        if self.game():
                            break
                elif answer == "Exit":
                    sys.exit(0)
            except AttributeError:
                print("File format exception")
    def game(self):
        self.field.show_field()
        while True:
            self.interaction.get_move(self.field)
            if self.interaction.get_action() == "Open":
                self.action.open(self.interaction.get_x(), self.interaction.get_y())
                self.field.show_field()
            if self.interaction.get_action() == "Flag":
                self.action.flag(self.interaction.get_x(), self.interaction.get_y())
                self.field.show_field()
            if self.action.check():
                self.field.show_field()
                break
        return True
