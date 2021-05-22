# Spencer Burton
# 4/7/2021
# Piece classes for Chess

BOARD_WIDTH = 8
BOARD_HEIGHT = 8


def name_to_letter(name):
    if name == "king":
        return "k"
    elif name == "queen":
        return "q"
    elif name == "rook":
        return "r"
    elif name == "bishop":
        return "b"
    elif name == "knight":
        return "n"
    elif name == "pawn":
        return "p"
    else:
        return "="

def opposite_color(color):
    if color == "black":
        return "white"
    elif color == "white":
        return "black"
    else:
        return color


# Attach this to all the stuff
class Position(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def index(self):
        return self.x + self.y * BOARD_WIDTH


class Board(object):
    def __init__(self):
        self.pieces = []
        self.populate()

    def populate(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                self.pieces.append(Piece("", "blank", Position(x, y)))

    def at(self, x, y):
        try:
            piece = self.pieces[x + y * BOARD_WIDTH]
            return piece
        except IndexError:
            print("Invalid index: ({}, {})".format(x, y))

    def set_at(self, x, y, piece):
        piece.pos = Position(x, y)
        piece.last_pos = Position(x, y)
        self.pieces[x + y * BOARD_WIDTH] = piece

    def move(self, src_x, src_y, des_x, des_y):
        self.set_at(des_x, des_y, self.at(src_x, src_y))
        self.set_at(src_x, src_y, Piece("", "blank"))
        self.at(des_x, des_y).moved()
        self.at(des_x, des_y).last_pos = Position(src_x, src_y)

    def as_text(self):
        string = ""

        for piece in self.pieces:
            string += name_to_letter(piece.type)

        return string


class Piece(object):
    def __init__(self, color, piece_type, position=Position(0, 0)):
        self.color = color
        self.type = piece_type
        self.pos = position
        self.has_moved = False
        self.last_pos = position

    def valid_moves(self, board):
        return []

    def moved(self):
        self.has_moved = True


class Pawn(Piece):
    def __init__(self, color, position=Position(0, 0)):
        super(Pawn, self).__init__(color, "pawn", position)
        self.can_passant = [True, True]
        self.in_passant = [False, False]
        self.moved_two = False

    def valid_moves(self, board):
        direction = 0

        if self.color == "black":
            direction = 1
        elif self.color == "white":
            direction = -1

        # Add en passant

        # Check directly in front, and two the sides of that
        # which will be valid if there is a enemy piece there
        # Third value determines whether a piece needs to be there
        check_moves = [(self.pos.x, self.pos.y + direction, False),
                       (self.pos.x + 1, self.pos.y + direction, True),
                       (self.pos.x - 1, self.pos.y + direction, True)]

        # If the pawn is still in it's starting place, then
        # it can move two tiles forward
        if self.pos.y == 1 and self.color == "black" \
                or self.pos.y == 6 and self.color == "white":

            # It can only move two tiles if there is not a piece directly in front of it
            if board.at(self.pos.x, self.pos.y + direction).type == "blank" and not self.has_moved:
                check_moves.append((self.pos.x, self.pos.y + direction * 2, False))

        valid_moves = []

        for move_index in range(len(check_moves)):
            move = check_moves[move_index]

            # Out of bounds, don't even try
            if move[0] >= 8 or move[0] < 0 or move[1] >= 8 or move[1] < 0:
                continue

            board_piece = board.at(move[0], move[1])

            if board_piece.type == "blank":
                if not move[2]:
                    valid_moves.append(Position(move[0], move[1]))
            else:
                if move[2] and board_piece.color != self.color:
                    valid_moves.append(Position(move[0], move[1]))

        # Check for en passant
        self.check_passant(board, direction)

        if self.can_passant[0]:
            if self.in_passant[0]:
                valid_moves.append(Position(self.pos.x - 1, self.pos.y + direction))
        if self.can_passant[1]:
            if self.in_passant[1]:
                valid_moves.append(Position(self.pos.x + 1, self.pos.y + direction))

        return valid_moves

    def check_passant(self, board, direction):
        self.in_passant = [False, False]

        if (self.color == "white" and self.pos.y == 3) or \
                (self.color == "black" and self.pos.y == 4):  # Pawn in the fifth rank
            right = board.at(self.pos.x + 1, self.pos.y)
            left = board.at(self.pos.x - 1, self.pos.y)
            check_right = False
            check_left = False

            if right.type == "pawn" and right.color == opposite_color(self.color):
                if right.moved_two:
                    check_right = True
            if left.type == "pawn" and left.color == opposite_color(self.color):
                if left.moved_two:
                    check_left = True

            if check_right:
                check = board.at(self.pos.x + 1, self.pos.y + direction)
                if check.type == "blank":
                    self.in_passant[1] = True
            if check_left:
                check = board.at(self.pos.x - 1, self.pos.y + direction)
                if check.type == "blank":
                    self.in_passant[0] = True


class Rook(Piece):
    def __init__(self, color, position=(0, 0)):
        super(Rook, self).__init__(color, "rook", position)

    def valid_moves(self, board):
        # Rook can move as far horizontally or vertically
        # unless a piece blocks the way, if that piece
        # is of the opposite color, it can take it as a move.
        # Some loops add 1 so it doesn't check itself

        valid_moves = []

        # Check the horizontal for valid moves first
        # Left side of piece
        for i in reversed(range(0, self.pos.x)):
            piece = board.at(i, self.pos.y)
            if piece.type == "blank":
                valid_moves.append(Position(i, self.pos.y))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(i, self.pos.y))
                break
        # Right side of the piece
        for i in range(self.pos.x + 1, BOARD_WIDTH):
            piece = board.at(i, self.pos.y)
            if piece.type == "blank":
                valid_moves.append(Position(i, self.pos.y))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(i, self.pos.y))
                break

        # Check the vertical for valid moves now
        # Above the piece
        for i in reversed(range(0, self.pos.y)):
            piece = board.at(self.pos.x, i)
            if piece.type == "blank":
                valid_moves.append(Position(self.pos.x, i))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(self.pos.x, i))
                break
        # Below the piece
        for i in range(self.pos.y + 1, BOARD_HEIGHT):
            piece = board.at(self.pos.x, i)
            if piece.type == "blank":
                valid_moves.append(Position(self.pos.x, i))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(self.pos.x, i))
                break

        return valid_moves


class Knight(Piece):
    def __init__(self, color, position=(0, 0)):
        super(Knight, self).__init__(color, "knight", position)

    def valid_moves(self, board):
        # Knight can move either two horizontally and one vertically
        # or vice versa
        check_moves = [Position(self.pos.x + 2, self.pos.y + 1),
                       Position(self.pos.x + 2, self.pos.y - 1),
                       Position(self.pos.x + 1, self.pos.y + 2),
                       Position(self.pos.x + 1, self.pos.y - 2),
                       Position(self.pos.x - 1, self.pos.y + 2),
                       Position(self.pos.x - 1, self.pos.y - 2),
                       Position(self.pos.x - 2, self.pos.y + 1),
                       Position(self.pos.x - 2, self.pos.y - 1)]

        valid_moves = []

        for move in check_moves:
            if (move.x not in range(BOARD_WIDTH)) or (move.y not in range(BOARD_HEIGHT)):
                continue

            piece = board.at(move.x, move.y)
            if piece.type == "blank" or piece.color != self.color:
                valid_moves.append(move)

        return valid_moves


class Bishop(Piece):
    def __init__(self, color, position=(0, 0)):
        super(Bishop, self).__init__(color, "bishop", position)

    def valid_moves(self, board):
        # Bishop can move diagonally in 4 directions,
        # unless blocked by piece. If the piece is the
        # opposite color, it can take it as a move but not move past it.

        valid_moves = []

        # Check right side first
        # North-East diagonal
        for i in range(1, BOARD_WIDTH - self.pos.x):
            # Make sure the piece is on the board
            if (self.pos.y - i) not in range(BOARD_HEIGHT):
                break

            piece = board.at(self.pos.x + i, self.pos.y - i)
            if piece.type == "blank":
                valid_moves.append(Position(self.pos.x + i, self.pos.y - i))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(self.pos.x + i, self.pos.y - i))
                break
        # South-East diagonal
        for i in range(1, BOARD_WIDTH - self.pos.x):
            # Make sure the piece is on the board
            if (self.pos.y + i) not in range(BOARD_HEIGHT):
                break

            piece = board.at(self.pos.x + i, self.pos.y + i)
            if piece.type == "blank":
                valid_moves.append(Position(self.pos.x + i, self.pos.y + i))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(self.pos.x + i, self.pos.y + i))
                break

        # Check left side now
        # North-West diagonal
        for i in range(1, self.pos.x + 1):
            # Make sure the piece is on the board
            if (self.pos.y - i) not in range(BOARD_HEIGHT):
                break

            piece = board.at(self.pos.x - i, self.pos.y - i)
            if piece.type == "blank":
                valid_moves.append(Position(self.pos.x - i, self.pos.y - i))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(self.pos.x - i, self.pos.y - i))
                break
        # South-West diagonal
        for i in range(1, self.pos.x + 1):
            # Make sure the piece is on the board
            if (self.pos.y + i) not in range(BOARD_HEIGHT):
                break

            piece = board.at(self.pos.x - i, self.pos.y + i)
            if piece.type == "blank":
                valid_moves.append(Position(self.pos.x - i, self.pos.y + i))
            else:
                if piece.color != self.color:
                    valid_moves.append(Position(self.pos.x - i, self.pos.y + i))
                break

        return valid_moves


class Queen(Piece):
    def __init__(self, color, position=Position(0, 0)):
        super(Queen, self).__init__(color, "queen", position)

    def valid_moves(self, board):
        # Queen is basically a combination of rook and bishop.
        # A Queen can move in all four directions and diagonally,
        # Unless a piece is in the way, and if it's the opposite color
        # the queen can take it as a move, but not move past it.

        temp_rook = Rook(self.color, self.pos)
        temp_bishop = Bishop(self.color, self.pos)
        valid_moves = temp_rook.valid_moves(board) + temp_bishop.valid_moves(board)

        return valid_moves


class King(Piece):
    def __init__(self, color, position=Position(0, 0)):
        super(King, self).__init__(color, "king", position)
        self.has_castled = False

    def valid_moves(self, board):
        # The King can move to any of the eight spaces around it,
        # unless it is not on the board, or there is a piece in the way.
        # The King can take pieces of opposite color in his way as a move.
        valid_moves = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                if (self.pos.x + x) not in range(BOARD_WIDTH) or \
                        (self.pos.y + y) not in range(BOARD_HEIGHT):
                    continue

                piece = board.at(self.pos.x + x, self.pos.y + y)
                if piece.type == "blank" or piece.color != self.color:
                    valid_moves.append(Position(self.pos.x + x, self.pos.y + y))

        # Finally adding castling
        if not self.has_moved and not self.has_castled:
            if self.pos == Position(4, 7) or self.pos == Position(4, 0):
                # Check for blanks and rook
                queen_side = ["rook", "blank", "blank", "blank"]
                king_side = ["blank", "blank", "rook"]
                temp = []

                # Check queen side
                for i in range(0, 4):
                    piece = board.at(i, self.pos.y)
                    temp.append(piece.type)
                if queen_side == temp:
                    if not board.at(0, self.pos.y).has_moved:
                        valid_moves.append(Position(2, self.pos.y))

                temp = []

                # Check king side
                for i in range(5, 8):
                    piece = board.at(i, self.pos.y)
                    temp.append(piece.type)
                if king_side == temp:
                    if not board.at(7, self.pos.y).has_moved:
                        valid_moves.append(Position(6, self.pos.y))

        return valid_moves

    def castled(self):
        self.has_castled = True
