import numpy as np

from ..board_representation import BoardState
from . import mappings
from ..consts import WHITE, BLACK, KINGSIDE, QUEENSIDE


def to_boardstate(record: str) -> BoardState:
    """
    Parse a Forsyth–Edwards Notation (FEN) record to transform the data into a format accepted
    by the class `boards.abc.Chessboard`.

    Parameters
    ----------
    record : str
        A FEN record as a string.

    Returns
    -------
    tuple[list[list[int]], list[list[int]], int, int, int, int]
    A new Chessboard object with the given board position.
        Board, castling status, current player (turn), fifty-move count, en passant file,
        and ply count, respectively. For more information, see `boards.abc.Chessboard`.
    """
    if not isinstance(record, str):
        raise ValueError("FEN record must be a string.")
    # A record contains six fields, each separated by a space:
    try:
        (
            piece_data,
            active_color,
            castling_avail,
            enpassant_square,
            halfmove_clock,
            fullmove_num,
        ) = record.split()
    except ValueError:
        raise ValueError("FEN record must contain six fields, each separated by a space.")
    # 1. Piece Data
    # describes each rank (from 8 to 1), with a '/' separating ranks:
    ranks = piece_data.split("/")
    if len(ranks) != 8:
        raise ValueError("FEN piece data should contain eight ranks, each separated by a '/'.")
    ranks.reverse()
    # Within each rank, squares are described from file a to h. Each piece is identified
    # by its algebraic notation, while white pieces are designated using uppercase letters
    # and black pieces use lowercase letters. A set of one or more consecutive empty squares
    # within a rank is denoted by a digit from "1" to "8".
    board = []
    for rank in ranks:
        board.append([])
        for square in rank:
            if square.isnumeric():
                board[-1].extend([0] * int(square))
            else:
                color = WHITE if square.isupper() else BLACK
                try:
                    board[-1].append(color * mappings.PIECE_LETTERS[square.upper()])
                except KeyError:
                    raise ValueError(f"Piece notation {square} is unknown.")
        if len(board[-1]) != 8:
            raise ValueError(f"Each rank should describe eight squares; got {len(board[-1])}")
    # 2. Active Color
    # "w" means that White is to move; "b" means that Black is to move.
    if active_color == "w":
        player = WHITE
    elif active_color == "b":
        player = BLACK
    else:
        raise ValueError(f"Active color must be either 'w' or 'b'; got {active_color}.")
    # 3. Castling Availability
    # If neither side has the ability to castle, this field uses the character "-".
    # Otherwise, it contains one or more letters:
    # Uppercase for white, lowercase for black; 'k' for kingside, 'q' for queenside.
    castling_rights = {
        WHITE: {QUEENSIDE: False, KINGSIDE: False},
        BLACK: {QUEENSIDE: False, KINGSIDE: False}
    }
    for avail in castling_avail:
        player_ = WHITE if avail.isupper() else BLACK
        if avail == "-":
            break
        elif avail.upper() == "K":
            castling_rights[player_][KINGSIDE] = True
        elif avail.upper() == "Q":
            castling_rights[player_][QUEENSIDE] = True
        else:
            raise ValueError(f"Castling availability field unrecognized; got {avail}")
    # 4. En passant target square
    # over which a pawn has just passed while moving two squares; in algebraic notation.
    # If there is no en passant target square, this field uses the character "-".
    # This is recorded regardless of whether there is a pawn in position to capture en passant.
    if enpassant_square == "-":
        enpassant_file = np.int8(-1)
    else:
        try:
            enpassant_file = np.int8(mappings.FILES[enpassant_square[0]])
        except KeyError:
            raise ValueError(f"En passant target square not recognized; got {enpassant_square}")
    # 5. Halfmove clock
    # number of halfmoves since the last capture or pawn advance, used for the fifty-move rule.
    try:
        halfmove_clock = np.int8(halfmove_clock)
    except ValueError:
        raise ValueError(f"Halfmove clock must be an integer; got {halfmove_clock}.")
    if 0 <= halfmove_clock <= 100:
        fifty_move_count = halfmove_clock
    else:
        raise ValueError(f"Halfmove clock must be between 0 and 50; got {halfmove_clock}.")
    # 6. Fullmove number
    # The number of the full moves. It starts at 1 and is incremented after Black's move.
    # According to
    #   Bonsdorff et al., Schach und Zahl. Unterhaltsame Schachmathematik. pp. 11–13,
    # the longest-possible game lasts 5899 moves (i.e. 11798 plies).
    try:
        fullmove_num = np.int8(fullmove_num)
    except ValueError:
        raise ValueError(f"Fullmove number must be an integer; got {fullmove_num}.")
    if 1 <= fullmove_num <= 5899:
        ply_count = (fullmove_num - 1) * 2 + (1 if player == BLACK else 0)
    else:
        raise ValueError(f"Fullmove number must be between 1 and 5899; got {fullmove_num}.")
    return BoardState(
        board=np.array(board, dtype=np.int8),
        castling_rights=castling_rights,
        player=np.int8(player),
        enpassant_file=np.int8(enpassant_file),
        fifty_move_count=np.int8(fifty_move_count),
        ply_count=np.int16(ply_count),
    )
