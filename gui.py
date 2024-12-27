from tkinter import Tk, Canvas, Label, Button, Frame
from PIL import ImageTk, Image
from engine.game import Game

UNSCALED_RECT_SIZE = 0.008


class Window(Tk):
    def __init__(self, game: Game):

        Tk.__init__(self)
        # for 4k
        self.tk.call('tk', 'scaling', '-displayof', '.', 1)

        # setup variables
        self.game = game

        # create widgets
        self.board_canvas = Canvas(self, background="white")
        self.control_frame = Frame(self)
        self.label_current_player = Label(self.control_frame, text="Current Player: X")
        self.button_next_turn = Button(self.control_frame, text="Next Turn", command=self.next_turn)

        # layout widgets
        self.board_canvas.pack(fill='both', expand=True, anchor='w')
        self.control_frame.pack(before=self.board_canvas, side='bottom', anchor='s')
        self.label_current_player.pack(fill='x')
        self.button_next_turn.pack(fill='x')

        # setup canvas
        self.board_img_pil = Image.open('board.jpg')
        self.board_img = ImageTk.PhotoImage(self.board_img_pil)
        self.img_id = self.board_canvas.create_image(300, 300, image=self.board_img)

        # move image on resize
        self.bind("<Configure>", self.update_ui)
        self.player_colors = ["black", "red", "yellow", "green", "blue", "purple"]
        self.old_canvas_size = self.winfo_width(), self.winfo_height()
        self.player_rects = [self.board_canvas.create_rectangle(0, 0, 1, 1, fill=self.player_colors[i]) for i in
                             range(len(self.game.players))]
        self.player_txts = [self.board_canvas.create_text(0, 0, text=plr.name) for plr in self.game.players]

        # create data for node locations on image
        self.node_locations = {}
        with open("node_locations.txt", "r") as f:
            for line in f:
                l = line.split(" ")
                self.node_locations[int(l[0])] = (float(l[1]), float(l[2]))

    def next_turn(self, *_):
        try:
            self.game.next_turn()
            self.label_current_player.configure(
                text="Current Player: {}".format(self.game.players[self.game.turn].name))
        except:
            w, h = self.board_canvas.winfo_width(), self.board_canvas.winfo_height()
            self.board_canvas.create_rectangle(w / 4, h / 4, w * 3 / 4, h * 3 / 4, fill="red")
            self.board_canvas.create_text(w / 2, h / 2, text="EXCEPTION OCCURRED; CHECK LOG", font="Helvetica 36")
            raise
        self.update_ui()

    def update_ui(self, *_):
        width = self.board_canvas.winfo_width()
        height = self.board_canvas.winfo_height()
        if self.old_canvas_size != (width, height):  # don't update the image unless we *have* to
            self.old_canvas_size = (width, height)
            tmp_pil = self.board_img_pil.resize((width, height))
            self.board_canvas.delete(self.img_id)
            self.board_img = ImageTk.PhotoImage(tmp_pil)
            self.img_id = self.board_canvas.create_image(int(width / 2), int(height / 2), image=self.board_img)

        for i, player in enumerate(self.game.players):
            x, y = self.node_locations[player.pos]
            x *= width
            y *= height
            self.board_canvas.coords(self.player_rects[i], x + width * UNSCALED_RECT_SIZE,
                                     y + width * UNSCALED_RECT_SIZE, x - width * UNSCALED_RECT_SIZE,
                                     y - width * UNSCALED_RECT_SIZE)
            self.board_canvas.coords(self.player_txts[i], x, y)
            self.board_canvas.lift(self.player_rects[i])
            self.board_canvas.lift(self.player_txts[i])
