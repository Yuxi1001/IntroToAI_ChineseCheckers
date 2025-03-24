import pygame
import threading
import time
import random
from board import Board
from mcts import mcts_search

# Window settings
WIDTH = 800
HEIGHT = 800
RADIUS = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

class Game:
    PLAYER_1_COLOR = "red"    # Human player color
    PLAYER_2_COLOR = "blue"   # AI player color

    def __init__(self):
        self.board = Board()
        self.cell_coords = {}
        self.selected_piece = None
        self.turn = Board.PLAYER_1_NR  # Human player starts first
        self.ai_move_thread = None
        self.ai_best_move = None

    # Compute AI move: call the pure MCTS search function
    def compute_ai_move(self):
        self.ai_best_move = mcts_search(self.board, Board.PLAYER_2_NR, iterations=1000)

    def update(self):
        # When it's the AI's turn, start a separate thread to compute the move
        if self.turn == Board.PLAYER_2_NR and self.ai_move_thread is None:
            self.ai_move_thread = threading.Thread(target=self.compute_ai_move)
            self.ai_move_thread.start()

        if self.turn == Board.PLAYER_2_NR and self.ai_move_thread is not None:
            if not self.ai_move_thread.is_alive():
                best_move = self.ai_best_move
                if best_move:
                    legal_moves = self.board.get_all_legal_moves_by_player(Board.PLAYER_2_NR)
                    if best_move not in legal_moves:
                        print("AI selected an illegal move:", best_move)
                        if legal_moves:
                            best_move = random.choice(legal_moves)
                        else:
                            best_move = None
                    if best_move:
                        x1, y1, x2, y2 = best_move
                        self.board.move(x1, y1, x2, y2)
                        print(f"AI moved piece from ({x1}, {y1}) to ({x2}, {y2})")
                    else:
                        print("AI did not find a valid move.")
                else:
                    print("AI did not find a valid move.")
                # Switch back to the human player's turn
                self.turn = Board.PLAYER_1_NR
                self.selected_piece = None
                self.ai_move_thread = None
                self.ai_best_move = None

    def draw(self, screen):
        BG_COLOR1 = (200, 200, 200)  # light gray
        BG_COLOR2 = (150, 150, 150)  # dark gray

        # Calculate the width and height of each cell based on the board dimensions
        cell_width = (WIDTH - RADIUS * 1.5) / self.board.WIDTH
        cell_height = (HEIGHT - RADIUS * 1.5) / self.board.HEIGHT

        for top in range(self.board.HEIGHT):
            for col in range(self.board.WIDTH):
                bg_color = BG_COLOR1 if (top + col) % 2 == 0 else BG_COLOR2

                center_x = RADIUS * 1.5 + col * ((WIDTH - RADIUS * 1.5) / self.board.WIDTH)
                center_y = RADIUS * 1.5 + top * ((HEIGHT - RADIUS * 1.5) / self.board.HEIGHT)

                cell_x = center_x - cell_width / 2
                cell_y = center_y - cell_height / 2

                rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
                pygame.draw.rect(screen, bg_color, rect)

        self.cell_coords.clear()

        for top, row in enumerate(self.board.board):
            y_index = Board.HEIGHT - 1 - top
            for x, cell in enumerate(row):
                if cell == 0:
                    continue

                coords = pygame.Vector2(
                    RADIUS * 1.5 + x * ((WIDTH - RADIUS * 1.5) / self.board.WIDTH),
                    RADIUS * 1.5 + top * ((HEIGHT - RADIUS * 1.5) / self.board.HEIGHT),
                )
                self.cell_coords[(x, y_index)] = coords

                if (x, y_index) == self.selected_piece:
                    piece_color = (0, 255, 0)  # Highlight the selected piece in green
                elif cell == Board.PLAYER_1_NR:
                    piece_color = self.PLAYER_1_COLOR
                elif cell == Board.PLAYER_2_NR:
                    piece_color = self.PLAYER_2_COLOR
                else:
                    piece_color = (128, 128, 128)

                pygame.draw.circle(screen, piece_color, coords, RADIUS)


    def on_click(self, coord):
        for (x, y), cell_coord in self.cell_coords.items():
            if pygame.Vector2(coord).distance_to(cell_coord) < RADIUS:
                self.on_cell_clicked(x, y)
                print(f"Clicked on cell {x}, {y}")
                break

    def on_cell_clicked(self, x, y):
        if self.turn == Board.PLAYER_1_NR:
            if self.selected_piece is None:
                if self.board.get_cell(x, y) == self.turn:
                    self.selected_piece = (x, y)
                    self.initial_position = (x, y)
            else:
                # Removed the mandatory jump check to allow sliding moves even when jump moves exist.
                legal_moves = self.board.get_legal_moves(*self.selected_piece)
                if (x, y) in legal_moves:
                    is_jump = abs(x - self.selected_piece[0]) > 1 or abs(y - self.selected_piece[1]) > 1
                    self.board.move(*self.selected_piece, x, y)
                    if is_jump:
                        chain_moves = [
                            move for move in self.board.get_legal_moves(x, y, jump=True)
                            if move != (x, y) and move != self.initial_position
                        ]
                        if chain_moves:
                            self.selected_piece = (x, y)
                            print("Chain jump available. Click a valid jump or press Enter to confirm move completion.")
                            return
                    self.turn = Board.PLAYER_2_NR
                    self.selected_piece = None
                    self.initial_position = None
                else:
                    if self.board.get_cell(x, y) == self.turn:
                        self.selected_piece = (x, y)

    def confirm_move(self):
        if self.turn == Board.PLAYER_1_NR and self.selected_piece is not None:
            print("Player confirmed move completion.")
            self.turn = Board.PLAYER_2_NR
            self.selected_piece = None
            self.initial_position = None

game = Game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and game.turn == Board.PLAYER_1_NR:
            game.on_click(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game.confirm_move()

    screen.fill("white")
    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
