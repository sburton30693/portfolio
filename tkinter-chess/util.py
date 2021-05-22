# Spencer Burton
# 5/3/2021
# Utility functions for chess stuff


from piece import *
import copy


# Constants
WIDTH = 622
HEIGHT = 636
TITLE = "Chess"

TILE_COLOR = ("#ffcacb", "#be5256", "#9cc2ff", "#70a7ff")
BG_COLOR = "#eeeeee"
FILTER_MOVES_THAT_CHECK = True
FIRST_TURN = "white"

# This is the starting positions of the board
PIECE_TYPES = ["pawn", "rook", "bishop", "knight", "king", "queen"]
FIRST_ROW = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]


def from_index(index):
    return Position(index % BOARD_WIDTH, index // BOARD_WIDTH)


def piece_from_name(name, color, position=(0, 0)):
    if name == "pawn":
        return Pawn(color, position)
    elif name == "rook":
        return Rook(color, position)
    elif name == "knight":
        return Knight(color, position)
    elif name == "bishop":
        return Bishop(color, position)
    elif name == "queen":
        return Queen(color, position)
    elif name == "king":
        return King(color, position)
    else:
        return Piece("", "blank", position)


def opposite_color(color):
    if color == "black":
        return "white"
    elif color == "white":
        return "black"
    else:
        return color


def rank_by_type(name):
    if name == "king":
        return 100
    elif name == "queen":
        return 9
    elif name == "rook":
        return 5
    elif name == "bishop":
        return 3
    elif name == "knight":
        return 3
    elif name == "pawn":
        return 1
    else:
        return 0


def tile_color_at(x, y):
    return TILE_COLOR[(x + y) % 2]


def move_color_at(x, y):
    return TILE_COLOR[(x + y) % 2 + 2]


def piece_img_index(name, color):
    if name == "blank" or color == "":
        return 0

    index = PIECE_TYPES.index(name) * 2 + 1

    if color == "black":
        index += 1

    return index


def castle_controlled(board, color):
    if color == "white":
        king_y = 7
    elif color == "black":
        king_y = 0

    king = board.at(4, king_y)

    if king.type != "king":
        return True

    for i in range(2, 7):
        temp_board = copy.deepcopy(board)
        temp_board.move(4, king_y, i, king_y)

        if in_check(temp_board, color):
            return True

    return False


def find_move_that_wins(board, valid_moves, color):
    for move_set in valid_moves:
        for move in move_set[1]:
            piece = board.at(move.x, move.y)

            if piece.color == opposite_color(color) and piece.type == "king":
                return (move_set[0], move)

    return None


def num_moves_possible(board, color):
    num_moves = 0

    for piece in board.pieces:
        if piece.color != color:
            continue

        num_moves += len(piece.valid_moves(board))

    return num_moves


def get_all_moves(board, color):
    valid_moves = []

    for piece in board.pieces:
        if piece.color == color:
            moves = piece.valid_moves(board)
            if moves:
                valid_moves += [(piece, moves)]

    return valid_moves


def in_check(board, color):
    for piece in board.pieces:
        if piece.color == opposite_color(color):
            valid_moves = piece.valid_moves(board)

            for move in valid_moves:
                move_piece = board.at(move.x, move.y)

                if move_piece.color == color and move_piece.type == "king":
                    return True

    return False


def remove_moves_that_check(board, valid_moves, color):
    new_moves = []

    for move_set in valid_moves:
        piece = move_set[0]
        new_move_set = (piece, [])
        for move in move_set[1]:
            temp_board = copy.deepcopy(board)
            temp_board.move(piece.pos.x, piece.pos.y, move.x, move.y)

            if not in_check(temp_board, color):
                new_move_set[1].append(move)

        new_moves.append(new_move_set)

    return new_moves


def has_no_moves(board, color):
    moves = get_all_moves(board, color)
    moves = remove_moves_that_check(board, moves, color)

    for move_set in moves:
        if move_set[1]:
            return False

    return True
