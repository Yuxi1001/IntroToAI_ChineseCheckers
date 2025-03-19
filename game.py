import pygame

from board import Board
from mcts import mcts



WIDTH = 800
HEIGHT = 800
RADIUS = 20

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)



class Game:
    PLAYER_1_COLOR = "red"   # Human (Player 1)
    PLAYER_2_COLOR = "blue" # AI (Player 2)

    def __init__(self):
        self.board = Board()
        self.cell_coords = {}
        self.selected_piece = None
        self.turn = Board.PLAYER_1_NR   # Human player goes first
        self.ai_move_made = False      # Flag to prevent repeated AI moves

    def draw(self, screen):
        self.cell_coords.clear()
        for top, row in enumerate(self.board.board):
            y = Board.HEIGHT - 1 - top
            for x, cell in enumerate(row):
                if cell == 0:
                    continue
                coords = pygame.Vector2(
                    RADIUS * 1.5 + x * ((WIDTH - RADIUS * 1.5) / self.board.WIDTH),
                    RADIUS * 1.5 + top * ((HEIGHT - RADIUS * 1.5) / self.board.HEIGHT),
                )
                self.cell_coords[(x, y)] = coords
                if (x, y) == self.selected_piece:
                    pygame.draw.circle(screen, "green", coords, RADIUS)
                elif cell == Board.PLAYER_1_NR:
                    pygame.draw.circle(screen, self.PLAYER_1_COLOR, coords, RADIUS)
                elif cell == Board.PLAYER_2_NR:
                    pygame.draw.circle(screen, self.PLAYER_2_COLOR, coords, RADIUS)
                else:
                    pygame.draw.circle(screen, "grey", coords, RADIUS)

    def update(self):
        # If it's AI's turn (Player 2) and we haven't already made the AI move this cycle,
        # run MCTS to compute the best move.
        if self.turn == Board.PLAYER_2_NR and not self.ai_move_made:
            best_move = mcts(self.board, Board.PLAYER_2_NR, iterations=1000)
            if best_move:
                x1, y1, x2, y2 = best_move
                self.board.move(x1, y1, x2, y2)
                print(f"AI moved piece from ({x1}, {y1}) to ({x2}, {y2})")
            else:
                print("AI did not find a valid move.")
            # After the AI moves, switch turn back to the human.
            self.turn = Board.PLAYER_1_NR
            self.selected_piece = None
            self.ai_move_made = True
        # Reset the AI move flag when it’s human’s turn.
        if self.turn == Board.PLAYER_1_NR:
            self.ai_move_made = False

    def on_click(self, coord):
        for (x, y), cell_coord in self.cell_coords.items():
            if pygame.Vector2(coord).distance_to(cell_coord) < RADIUS:
                self.on_cell_clicked(x, y)
                print(f"Clicked on cell {x}, {y}")
                break

    def on_cell_clicked(self, x, y):
        # Process human input only when it's the human's turn.
        if self.turn == Board.PLAYER_1_NR:
            if self.selected_piece is None:
                # Allow selecting only the human's pieces.
                if self.board.get_cell(x, y) == self.turn:
                    self.selected_piece = (x, y)
            else:
                legal_moves = self.board.get_legal_moves(*self.selected_piece)
                if (x, y) in legal_moves:
                    self.board.move(*self.selected_piece, x, y)
                    # Check for a chain jump opportunity.
                    if len(self.board.get_legal_moves(x, y, jump=True)) > 1:
                        self.selected_piece = (x, y)    # 继续选中棋子，允许连跳
                    else:
                        # End the human turn and switch to AI.
                        self.turn = Board.PLAYER_2_NR
                        self.selected_piece = None
                else:
                    self.selected_piece = None  #取消选中

        # if self.selected_piece is None:
        #     if self.board.get_cell(x, y) == self.turn:#只允许当前玩家选棋子
        #         self.selected_piece = (x, y)
        # else:
        #     if (x, y) in self.board.get_legal_moves(*self.selected_piece):
        #         self.board.move(*self.selected_piece, x, y)
        #         # 检查是否还能跳
        #         if len(self.board.get_legal_moves(x, y, jump=True)) > 1:
        #             self.selected_piece = (x, y)  # 继续选中棋子，允许连跳
        #         else:#没有可跳的,才切回合
        #             self.turn = Board.PLAYER_1_NR if self.turn == Board.PLAYER_2_NR else Board.PLAYER_2_NR  # 轮流切换回合
        #             self.selected_piece = None
        #     else:
        #         self.selected_piece = None#取消选中


game = Game()

clicked_last_frame = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Only process human input when it's the human's turn.
        if event.type == pygame.MOUSEBUTTONDOWN and game.turn == Board.PLAYER_1_NR:
            game.on_click(pygame.mouse.get_pos())

    screen.fill("white")
    game.update()
    game.draw(screen)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

    # # poll for events
    # # pygame.QUIT event means the user clicked X to close your window
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         running = False

    # # fill the screen with a color to wipe away anything from last frame
    # screen.fill("white")
    # game.update()
    # game.draw(screen)

    # click = pygame.mouse.get_pressed()
    # if click[0] and not clicked_last_frame:
    #     game.on_click(pygame.mouse.get_pos())
    #     clicked_last_frame = True
    # elif not click[0]:
    #     clicked_last_frame = False

    # # flip() the display to put your work on screen
    # pygame.display.flip()

    # # limits FPS to 60
    # # dt is delta time in seconds since last frame, used for framerate-
    # # independent physics.
    # dt = clock.tick(60) / 1000

pygame.quit()
