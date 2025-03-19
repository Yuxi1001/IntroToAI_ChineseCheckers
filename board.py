import numpy as np


class Board:
    """
    Class for managing a chinese checkers board.

    The class deals with cartesian x,y coordinates, where 0,0 is unplayable bottom left,
    and 16,24 is upper right. 12,0 is the lower-most playable field.

    Moves happen through the move(current_x, current_y, to_x, to_y) method.
    Illigal moves are not controlled but the is_legal_move(current_x,
    current_y, to_x, to_y) method will check.

    Legal moves will be able to be found with the get_legal_moves() method.

    Only player 1 and 2 are supported at the moment.
    """

    WIDTH = 25#棋盘宽度
    HEIGHT = 17#棋盘高度

    PLAYER_1_INIT_POS = [
        (12, 0),
        (11, 1),
        (13, 1),
        (10, 2),
        (12, 2),
        (14, 2),
        (9, 3),
        (11, 3),
        (13, 3),
        (15, 3),
    ]
    PLAYER_1_NR = 2#2代表红色棋子

    PLAYER_2_INIT_POS = [
        (12, 16),
        (11, 15),
        (13, 15),
        (10, 14),
        (12, 14),
        (14, 14),
        (9, 13),
        (11, 13),
        (13, 13),
        (15, 13),
    ]
    PLAYER_2_NR = 3

    def __init__(self, players=2):
        self.board = Board.get_empty_board()#创建空棋盘
        self.players = players

        if players == 2:
            self.fill_cells(Board.PLAYER_1_INIT_POS, Board.PLAYER_1_NR)#放置玩家1
            self.fill_cells(Board.PLAYER_2_INIT_POS, Board.PLAYER_2_NR)#放置玩家2
        else:
            raise NotImplementedError("Only two players are supported at the moment")

    def get_state(self):
        """Method for getting the state of the board as a flat numpy array"""
        return np.array(self.board).flatten()

    def reset(self):
        self.board = Board.get_empty_board()
        if self.players == 2:
            self.fill_cells(Board.PLAYER_1_INIT_POS, 2)
            self.fill_cells(Board.PLAYER_2_INIT_POS, 3)
        else:
            raise NotImplementedError("Only two players are supported at the moment")

    def fill_cells(self, cells, value):
        """Method for filling a list of cells with a value"""
        for x, y in cells:
            self.set_cell(x, y, value)

    def get_cell(self, x, y):
        """Method for getting the value at given x and y location"""
        return self.board[Board.HEIGHT - 1 - y][x]

    def set_cell(self, x, y, value):
        """Method for setting a value at given x and y location"""
        self.board[Board.HEIGHT - 1 - y][x] = value

    def get_player_positions(self, player):
        position = []
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                if self.get_cell(x, y) == player:
                    position.append((x, y))

        return position

    def move(self, current_x, current_y, to_x, to_y):
        """Method for moveing a piecefrom one cell to another"""
        self.set_cell(to_x, to_y, self.get_cell(current_x, current_y))
        self.set_cell(current_x, current_y, 1)

    def player_in_territory(self, player, territory):
        for p_x, p_y in territory:
            if self.get_cell(p_x, p_y) != player:
                return False

        return True

    def is_won(self):
        """
        Returns 0 if nobody has won, 1 if player one and 2 if player two has
        won and so on
        """
        if self.players == 2:
            if self.player_in_territory(Board.PLAYER_1_NR, Board.PLAYER_2_INIT_POS):
                return Board.PLAYER_1_NR
            elif self.player_in_territory(Board.PLAYER_2_NR, Board.PLAYER_1_INIT_POS):
                return Board.PLAYER_2_NR

        return 0

    def get_graphical_representation(self, highlighted_pieces=[]):
        string = ""
        for row_i, row in enumerate(self.board):
            for col_i, col in enumerate(row):
                if col == 0:
                    string += " "

                elif col == 1:
                    string += "O"

                else:
                    if (col_i, Board.HEIGHT - 1 - row_i) in highlighted_pieces:
                        string += "\033[1m" + str(col - 1) + "\033[0m"
                    else:
                        string += str(col - 1)
            string += "\n"

        return string

    def get_legal_moves(self, x, y, jump=False, prev=[]):
        """
        Method for listing all the legal moves
        """
        # TODO: Convert to set instead of list

        # Check that a player is being moved.
        if self.get_cell(x, y) <= 1 and not jump:
            return []

        moves = []

        if jump:
            moves.append((x, y))#记录跳跃路径
        else:
            prev = []
        #遍历周围6个方向
        #实现两种合法走法:1、单步移动->相邻空格可以走.2、跳跃->隔一个棋子,落到空格可以跳(支持连跳)3、递归搜索,如果可以连续跳跃就递归计算
        for surr_x, surr_y in self.get_surrounding(x, y):
            if self.get_cell(surr_x, surr_y) == 1 and not jump:
                moves.append((surr_x, surr_y))

            elif self.get_cell(surr_x, surr_y) > 1:
                over_piece_pos = self.get_coord_over_piece(x, y, surr_x, surr_y)
                if not over_piece_pos is None:
                    over_x, over_y = over_piece_pos
                    # print(f"At: {x}, {y}, {prev=}, {over_x}, {over_y}")
                    if (
                        self.get_cell(over_x, over_y) == 1
                        and not (over_x, over_y) in prev
                    ):
                        # print(f"Checking {over_x},{over_y}, {prev=}")
                        prev.append((x, y))
                        moves.extend(self.get_legal_moves(over_x, over_y, True, prev))
        prev = []
        # print("Done: ", moves)
        return moves

    def get_all_legal_moves_by_player(self, player):
        moves = []
        for x, y in self.get_player_positions(player):
            for to_x, to_y in self.get_legal_moves(x, y):
                moves.append((x, y, to_x, to_y))

        return moves

    def get_coord_over_piece(self, current_x, current_y, surr_x, surr_y):
        """
        Method for getting the coordinate over a surrounding piece.
        """

        v_x = surr_x - current_x
        v_y = surr_y - current_y

        x, y = (surr_x + v_x, surr_y + v_y)

        if x < 0 or x >= Board.WIDTH or y < 0 or y >= Board.HEIGHT:
            return None

        return (x, y)

    def get_surrounding(self, x, y):
        """
        Method for getting all surrounding coordinates, they will not
        exceed the coordinates of the board, but they may contain zeros (out of
        bounds)
        """

        points = []

        # Left
        if x - 2 >= 0:
            points.append((x - 2, y))

        # Up Left
        if x - 1 >= 0 and y + 1 < Board.HEIGHT:
            points.append((x - 1, y + 1))

        # Up Right
        if x + 1 < Board.WIDTH and y + 1 < Board.HEIGHT:
            points.append((x + 1, y + 1))

        # Right
        if x + 2 < Board.WIDTH:
            points.append((x + 2, y))

        # Down Right
        if x + 1 < Board.WIDTH and y - 1 >= 0:
            points.append((x + 1, y - 1))

        # Down Left
        if x - 1 >= 0 and y - 1 >= 0:
            points.append((x - 1, y - 1))

        return points

    @staticmethod
    def get_empty_board():
        """Creates an empty chinese checkers board"""

        star_pattern = [1, 2, 3, 4, 13, 12, 11, 10, 9, 10, 11, 12, 13, 4, 3, 2, 1]
        board = []
        for line in star_pattern:
            line_pattern = []
            if line % 2 == 0:
                line_pattern.append(1)
                for _ in range(line // 2 - 1):
                    line_pattern.extend([0, 1])

                line_pattern.extend(
                    [0 for _ in range(Board.WIDTH // 2 - (line // 2) * 2 + 1)]
                )
                line_pattern = line_pattern[::-1] + [0] + line_pattern

            else:
                for _ in range(line // 2):
                    line_pattern.extend([0, 1])

                line_pattern.extend(
                    [0 for _ in range(Board.WIDTH // 2 - (line // 2) * 2)]
                )
                line_pattern = line_pattern[::-1] + [1] + line_pattern

            board.append(line_pattern)

        return board

    @staticmethod
    def get_all_possible_actions():
        """Gets a list of all possible actions"""
        empty_board = Board.get_empty_board()
        actions = []
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                if empty_board[y][x] == 1:
                    continue
                for to_x in range(Board.WIDTH):
                    for to_y in range(Board.HEIGHT):
                        if empty_board[to_y][to_x] == 1 and (x, y) != (to_x, to_y):
                            actions.append((x, y, to_x, to_y))

        return actions

    def __iter__(self):
        return self.board.__iter__()


if __name__ == "__main__":
    board = Board()
    print(board.get_graphical_representation([(9, 3)]))

    print("(9,3):", board.get_legal_moves(9, 3))

    board.move(11, 3, 10, 4)

    print(board.get_graphical_representation([(10, 2)]))

    print("(10,2):", board.get_legal_moves(10, 2))
