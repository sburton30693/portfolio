# Spencer Burton
# 5/3/2021
# Chess class for all the versions, p v p, ai v ai, p v ai

# Goals:
#  - Promotion with a choice of piece
#  - En Passant and Castling
#  - Stalemate, Draw, Check, and Checkmate conditions
#  - Can't do the same move

from util import *

# + means place black pieces
# - means place white pieces
# = means blank
# r = rook, n = knight, b = bishop, q = queen, k = king, p = pawn
DEFAULT_CONFIG = \
    "+rnbqkbnr"\
    " pppppppp"\
    " ========"\
    " ========"\
    " ========"\
    " ========"\
    "-pppppppp"\
    " rnbqkbnr"


class Chess(object):
    def __init__(self, init_config=DEFAULT_CONFIG):
        self.board = Board()
        self.move_num = 0
        self.turn = FIRST_TURN
        self.initial = init_config

        self.game_boards = []

        self.reset()

    def reset(self):
        self.turn = FIRST_TURN
        self.move_num = 0
        self.game_boards = []

        x = 0
        y = 0
        i = 0
        color = ""

        while x + y <= 14:
            if x >= BOARD_WIDTH:
                x = 0
                y += 1

            pos = Position(x, y)
            char = self.initial[i]

            if char == "+":
                color = "black"
            elif char == "-":
                color = "white"
            elif char == "=":
                self.board.set_at(pos.x, pos.y, piece_from_name("", ""))
                x += 1
            elif char == "r":
                self.board.set_at(pos.x, pos.y, piece_from_name("rook", color))
                x += 1
            elif char == "n":
                self.board.set_at(pos.x, pos.y, piece_from_name("knight", color))
                x += 1
            elif char == "b":
                self.board.set_at(pos.x, pos.y, piece_from_name("bishop", color))
                x += 1
            elif char == "q":
                self.board.set_at(pos.x, pos.y, piece_from_name("queen", color))
                x += 1
            elif char == "k":
                self.board.set_at(pos.x, pos.y, piece_from_name("king", color))
                x += 1
            elif char == "p":
                self.board.set_at(pos.x, pos.y, piece_from_name("pawn", color))
                x += 1

            i += 1

        self.game_boards.append(self.board.as_text())

    def attempt_move(self, piece_pos, move):
        piece = self.board.at(piece_pos.x, piece_pos.y)

        if piece.color != self.turn:
            return False

        legal_moves = piece.valid_moves(self.board)
        legal_moves = remove_moves_that_check(self.board, [(piece, legal_moves)], self.turn)[0][1]

        if move in legal_moves:
            castle = self.is_castling(piece, move)
            if castle:
                # Move king
                self.board.move(piece.pos.x, piece.pos.y, move.x, move.y)
                # Move rook
                if castle < 0:
                    self.board.move(BOARD_WIDTH - 1, piece.pos.y, move.x - 1, move.y)
                elif castle > 0:
                    self.board.move(0, piece.pos.y, move.x + 1, move.y)

                piece.castled()

            elif self.is_en_passant(piece, move):
                # Remove other Pawn
                self.board.set_at(move.x, piece.pos.y, piece_from_name("", ""))
                # Move Pawn
                self.board.move(piece.pos.x, piece.pos.y, move.x, move.y)
            else:
                self.board.move(piece.pos.x, piece.pos.y, move.x, move.y)
            self.move_num += 1
            self.turn = opposite_color(self.turn)
            self.game_boards.append(self.board.as_text())
            self.update_piece_data()
            return True

        return False

    def is_castling(self, piece, move):
        if piece.type == "king":
            diff = piece.pos.x - move.x
            if diff > 1:  # Queen-side castle
                return 1
            elif diff < 1:  # King-side castle
                return -1

        return False

    def is_en_passant(self, piece, move):
        if piece.type == "pawn":
            if self.board.at(move.x, move.y).type == "blank" and \
                    (move.x != piece.pos.x and move.y != piece.pos.y):
                return True

        return False

    def update_piece_data(self):
        for piece in self.board.pieces:
            if piece.type == "pawn":
                diff = piece.pos.y - piece.last_pos.y
                if diff > 1 or diff < 1:
                    piece.moved_two = True

                if piece.in_passant[0]:
                    if piece.can_passant[0]:
                        piece.can_passant[0] = False
                else:
                    piece.can_passant[0] = True

                if piece.in_passant[1]:
                    if piece.can_passant[1]:
                        piece.can_passant[1] = False
                else:
                    piece.can_passant[1] = True

    def at(self, pos):
        return self.board.at(pos.x, pos.y)

    def has_promotion(self):
        for i in range(0, BOARD_WIDTH):
            piece_top = self.board.at(i, 0)
            piece_bot = self.board.at(i, 7)

            if piece_top.type == "pawn" and piece_top.color == "white":
                return piece_top.color
            elif piece_bot.type == "pawn" and piece_bot.color == "black":
                return piece_bot.color

        return False

    def promote(self, new_piece_type, color):
        if new_piece_type not in ("knight", "bishop", "rook", "queen"):
            new_piece_type = "queen"

        for i in range(0, BOARD_WIDTH):
            piece_top = self.board.at(i, 0)
            piece_bot = self.board.at(i, 7)

            if piece_top.type == "pawn" and piece_top.color == color:
                self.board.set_at(piece_top.pos.x, piece_top.pos.y, piece_from_name(new_piece_type, color))
            elif piece_bot.type == "pawn" and piece_bot.color == color:
                self.board.set_at(piece_bot.pos.x, piece_bot.pos.y, piece_from_name(new_piece_type, color))

    def check_for_end_condition(self):
        # Check for a checkmate or stalemate
        for color in ("white", "black"):
            if has_no_moves(self.board, color):
                if in_check(self.board, color):
                    return "checkmate", color
                else:
                    return "stalemate", color

        # Check for a draw
        white_pieces = []
        black_pieces = []
        pieces = {"white": white_pieces, "black": black_pieces}

        for piece in self.board.pieces:
            if piece.color == "white":
                white_pieces.append(piece.type)
            elif piece.color == "black":
                black_pieces.append(piece.type)

        # Sort the pieces based on rank
        white_pieces.sort(reverse=True, key=rank_by_type)
        black_pieces.sort(reverse=True, key=rank_by_type)

        # Check for king vs king
        if white_pieces == ["king"] and black_pieces == ["king"]:
            return "draw", "No forced checkmate possible"

        # Check for king vs king + minor piece (knight or bishop) and
        # Check for king vs king + two knights and
        # Check for king + minor piece vs king + minor piece
        for color in ("white", "black"):
            pl = pieces[color]
            ol = pieces[opposite_color(color)]

            if pl == ["king", "bishop"] or pl == ["king", "knight"]:
                if ol == ["king"]:
                    return "draw", "No forced checkmate possible"

            if pl == ["king", "knight", "knight"]:
                if ol == ["king"]:
                    return "draw", "No forced checkmate possible"

            if pl == ["king", "bishop"] or pl == ["king", "knight"]:
                if ol == ["king", "bishop"] or ol == ["king", "knight"]:
                    return "draw", "No forced checkmate possible"

        # Check for repetition, 3 of the same board positions
        for i, board_a in enumerate(self.game_boards):
            for j, board_b in enumerate(self.game_boards):
                for k, board_c in enumerate(self.game_boards):
                    # Don't compare the same indexes of boards
                    if i == j or i == k or j == k:
                        continue

                    if board_a == board_b == board_c:
                        return "draw", "Same board position repeated 3 times"

        return "", ""
