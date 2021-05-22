# Spencer Burton
# An AI class and various AI types

import random
from util import *


class AIPlayer(object):
    def __init__(self):
        pass

    def choose_move(self, board, color):
        return None


# An ai that just chooses a random valid move
class RandomAI(AIPlayer):
    def __init__(self):
        super(RandomAI, self).__init__()
        self.name = "Random AI"

    def choose_move(self, board, color):
        if has_no_moves(board, color):
            return None

        move = None
        all_moves = get_all_moves(board, color)
        all_moves = remove_moves_that_check(board, all_moves, color)

        while move is None:
            move_set = random.choice(all_moves)
            if move_set[1]:
                move = random.choice(move_set[1])

        return (move_set[0], move)


class TakePieceAI(AIPlayer):
    def __init__(self):
        super(TakePieceAI, self).__init__()
        self.name = "Take Piece AI"

    def choose_move(self, board, color):
        if has_no_moves(board, color):
            return None

        valid_moves = get_all_moves(board, color)

        highest_rank = 0
        highest_rank_move = None
        move_piece = None

        if in_check(board, color):
            for move_set in valid_moves:
                piece = move_set[0]
                for move in move_set[1]:
                    temp_board = copy.deepcopy(board)
                    temp_board.move(piece.pos.x, piece.pos.y, move.x, move.y)

                    if not in_check(temp_board, color):
                        return (piece, move)

        # Filter out moves that put the king in check
        valid_moves = remove_moves_that_check(board, valid_moves, color)

        possible_win = find_move_that_wins(board, valid_moves, color)

        if possible_win is not None:
            return possible_win

        for move_set in valid_moves:
            piece = move_set[0]
            for move in move_set[1]:
                taken_piece = board.at(move.x, move.y)
                if taken_piece.color == opposite_color(color):
                    if highest_rank_move is None:
                        highest_rank = rank_by_type(taken_piece.type)
                        highest_rank_move = move
                        move_piece = piece
                    elif rank_by_type(taken_piece.type) > highest_rank:
                        highest_rank = rank_by_type(taken_piece.type)
                        highest_rank_move = move
                        move_piece = piece

        if highest_rank > 0:
            return (move_piece, highest_rank_move)

        return RandomAI().choose_move(board, color)


# Tries to minimize the number of moves the other player can make
class LeastMovesAI(AIPlayer):
    def __init__(self):
        super(LeastMovesAI, self).__init__()
        self.name = "Least Move AI"

    def choose_move(self, board, color):
        if has_no_moves(board, color):
            return None

        valid_moves = get_all_moves(board, color)

        lowest_moves = 999999
        final_move = None
        final_piece = None

        if in_check(board, color):
            for move_set in valid_moves:
                piece = move_set[0]
                for move in move_set[1]:
                    temp_board = copy.deepcopy(board)
                    temp_board.move(piece.pos.x, piece.pos.y, move.x, move.y)

                    if not in_check(temp_board, color):
                        return (piece, move)

        # Filter out moves that put the king in check
        valid_moves = remove_moves_that_check(board, valid_moves, color)

        possible_win = find_move_that_wins(board, valid_moves, color)

        if possible_win is not None:
            return possible_win

        for move_set in valid_moves:
            piece = move_set[0]
            for move in move_set[1]:
                temp_board = copy.deepcopy(board)
                temp_board.move(piece.pos.x, piece.pos.y, move.x, move.y)
                num_moves = num_moves_possible(temp_board, opposite_color(color))

                if num_moves < lowest_moves:
                    lowest_moves = num_moves
                    final_move = move
                    final_piece = piece

        if not final_move or not final_piece:
            return RandomAI().choose_move(board, color)

        return (final_piece, final_move)
