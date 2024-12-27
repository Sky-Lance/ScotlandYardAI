
from gui import Window
import mrx
# import detectives
import heuristic
from engine.game import Game

def main():
    # the_game = Game(mrx, detectives)
    the_game = Game(mrx, heuristic)
    win = Window(the_game)
    # detectives.initialize_game()
    win.mainloop()

if __name__ == "__main__":
    main()