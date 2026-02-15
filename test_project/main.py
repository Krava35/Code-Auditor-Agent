from Action import Action
from Field import Field
from Game import Game
from Interaction import Interaction

interaction = Interaction()
field = Field(interaction)
action = Action(field)
game = Game(interaction, field, action)

game.run()