"""
This module contains the data structures and conventions used in the whole program.
"""

# Standard library
from __future__ import annotations
from typing import NamedTuple, Optional

# 3rd party
import numpy as np


class BoardState(NamedTuple):
    """
    A data structure representing a full description of a chess position, i.e. the position state.

    board : numpy.ndarray(shape=(8, 8), dtype=numpy.int8)
        A 2-dimensional array representing a specific board position,
        i.e. the location of each piece on the board.
        Axis 0 (2nd. dimension) corresponds to files (columns) ordered from 'a' to 'h'.
        Axis 1 (1st. dimension) corresponds to ranks (rows) ordered from 1 to 8.
        Thus, indexing the board as `board[i, j]` gives the data for the square on row 'i'
        and column 'j'. For example, `board[0, 1]` is square 'b1'.
        The data for each square is an integer from –6 to +6, where:
        0 = empty, 1 = pawn, 2 = knight, 3 = bishop, 4 = rook, 5 = queen, 6 = king
        White pieces are denoted with positive integers, while black pieces have the
        same magnitude but with a negative sign (e.g. +6 = white king, –6 = black king).
    castling_rights : dict[numpy.int8, numpy.ndarray(shape=(2,), dtype=numpy.bool_)]
        A dictionary representing the castling availabilities, i.e. whether either player is
        permanently disqualified to castle, for white (key: 1) and black (key: -1).
        Each value is a 1-dimensional array, corresponding to queenside and kingside castles, in
        that order (i.e. element 0: queenside, 1: kingside). Data is boolean:
        True (castling allowed) or False (not allowed).
    player : numpy.int8
        Current player to move; +1 is white and -1 is black.
    enpassant_file : numpy.int8
        The file (column) index (from 0 to 7), in which an en passant capture is allowed
        for the current player in the current move. Defaults to -1 if no en passant allowed.
    fifty_move_count : numpy.int8
        Number of plies (half-moves) since the last capture or pawn advance, used for
        the fifty-move-draw rule; if the number reaches 100, the game ends in a draw.
    ply_count : numpy.int16
        The number of plies (half-moves) from the beginning of the game. Starts at 0.
    """

    board: np.ndarray
    castling_rights: dict[np.int8, dict[np.int8, bool]]
    player: np.int8
    enpassant_file: np.int8
    fifty_move_count: np.int8
    ply_count: np.int16
    is_checkmate: Optional[bool] = None
    is_draw: Optional[bool] = None

    @classmethod
    def create_new_game(cls) -> BoardState:
        """
        Instantiate a new Chessboard in the starting position of a standard game.

        Returns
        -------
        BoardState
        """
        # Set up board
        board = np.zeros(shape=(8, 8), dtype=np.int8)  # Initialize an all-zero 8x8 array
        board[(1, -2), :] = [[1], [-1]]  # Set white and black pawns on rows 2 and 7
        board[0, :] = [4, 2, 3, 5, 6, 3, 2, 4]  # Set white's main pieces on row 1
        board[-1, :] = -board[0]  # Set black's main pieces on row 8
        # Set instance attributes describing the game state to their initial values
        return cls(
            board=board,
            castling_rights={
                np.int8(1): {np.int8(-2): True, np.int8(2): True},
                np.int8(-1): {np.int8(-2): True, np.int8(2): True}
            },
            player=np.int8(1),
            enpassant_file=np.int8(-1),
            fifty_move_count=np.int8(0),
            ply_count=np.int16(0),
        )


class Move(NamedTuple):
    """
    A data structure representing a move in the game.

    s0 : numpy.ndarray[shape=(2, ), dtype=numpy.int8]
        Row and column index of the start square (both from 0 to 7), respectively.
        For example, [1, 0] is the square 2a.
    s1 : numpy.ndarray[shape=(2, ), dtype=numpy.int8]
        Row and column index of the end square (both from 0 to 7), respectively.
    p : numpy.int8
        Piece-ID of the moving piece:
        1 = pawn, 2 = knight, 3 = bishop, 4 = rook, 5 = queen, 6 = king
        White pieces are denoted with positive integers, while black pieces have the
        same magnitude but with a negative sign (e.g. +6 = white king, –6 = black king).
    pp : numpu.int8
        Piece-ID of the promoted piece, if the move leads to a promotion, otherwise 0.
    """

    s0: np.ndarray
    s1: np.ndarray
    p: np.int8
    pp: np.int8 = 0

    def __eq__(self, other):
        return (
            np.all(self.s0 == other.s0)
            and np.all(self.s1 == other.s1)
            and self.p == other.p
            and self.pp == other.pp
        )


class Moves(NamedTuple):

    s0s: np.ndarray
    s1s: np.ndarray
    ps: np.ndarray
    pps: np.ndarray

    def to_move_list(self):
        return [
            Move(s0, s1, p, pp) for s0, s1, p, pp in zip(self.s0s, self.s1s, self.ps, self.pps)
        ]

    def has_move(self, move: Move):
        has_s0 = np.all(self.s0s == move.s0, axis=1)
        has_s1 = np.all(self.s1s == move.s1, axis=1)
        has_p = self.ps == move.p
        has_pps = self.pps == move.pp
        has_all = has_s0 & has_s1 & has_p & has_pps
        return np.any(has_all)

    @property
    def is_empty(self):
        return self.s0s.size == 0


class Color(NamedTuple):
    name: str
    letter: str


class Piece(NamedTuple):
    color: Color
    name: str
    letter: str
    symbol: str


class Pieces(NamedTuple):
    NULL: np.int8 = np.int8(0)
    P: np.int8 = np.int8(1)
    N: np.int8 = np.int8(2)
    B: np.int8 = np.int8(3)
    R: np.int8 = np.int8(4)
    Q: np.int8 = np.int8(5)
    K: np.int8 = np.int8(6)

P = Pieces()

class Square(NamedTuple):
    file: str
    rank: int


COLOR = {-1: Color(name="black", letter="b"), 1: Color(name="white", letter="w")}
PIECE = {
    -6: Piece(color=COLOR[-1], name="king", letter="K", symbol="♚"),
    -5: Piece(color=COLOR[-1], name="queen", letter="Q", symbol="♛"),
    -4: Piece(color=COLOR[-1], name="rook", letter="R", symbol="♜"),
    -3: Piece(color=COLOR[-1], name="bishop", letter="B", symbol="♝"),
    -2: Piece(color=COLOR[-1], name="knight", letter="N", symbol="♞"),
    -1: Piece(color=COLOR[-1], name="pawn", letter="P", symbol="♟"),
    +1: Piece(color=COLOR[+1], name="pawn", letter="P", symbol="♙"),
    +2: Piece(color=COLOR[+1], name="knight", letter="N", symbol="♘"),
    +3: Piece(color=COLOR[+1], name="bishop", letter="B", symbol="♗"),
    +4: Piece(color=COLOR[+1], name="rook", letter="R", symbol="♖"),
    +5: Piece(color=COLOR[+1], name="queen", letter="Q", symbol="♕"),
    +6: Piece(color=COLOR[+1], name="king", letter="K", symbol="♔"),
}
FILE = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
RANK = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7", 7: "8"}
SQUARE = {
    (rank_idx, file_idx): f"{file}{rank}"
    for rank_idx, rank in RANK.items()
    for file_idx, file in FILE.items()
}
CASTLE = {0: "kingside", 1: "queenside"}
