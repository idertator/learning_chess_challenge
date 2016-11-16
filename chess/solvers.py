from abc import ABCMeta, abstractmethod
from collections import deque
from itertools import permutations
from time import time

from .structures import Board


class Solver(metaclass=ABCMeta):

    def __init__(self, rows: int, cols: int, pieces: list):
        """Abstract base class for solvers

        Args:
            rows: Row count
            cols: Column count
            pieces: List of tuples of two elements (Piece, Count)
        """
        self.rows = rows
        self.cols = cols
        self.pieces = pieces
        self._time = 0

    @classmethod
    @abstractmethod
    def identifier(cls) -> str:
        """Solver unique identifier

        Returns:
            Unique identifier
        """
        pass

    @abstractmethod
    def _solutions(self):
        """Generator of available solutions

        Yields:
            Board: Solution board
        """
        pass

    def solutions(self):
        self._time = time()
        yield from self._solutions()
        self._time = time() - self._time

    @property
    def time(self) -> float:
        """Time used for the computation in seconds"""
        return self._time


class NaiveBruteForceSolver(Solver):
    """
    TODO: Fix this, is not working properly
    """

    @classmethod
    def identifier(cls) -> str:
        return 'naive'

    def __init__(self, rows: int, cols: int, pieces: list):
        super(NaiveBruteForceSolver, self).__init__(rows, cols, pieces)

    def _solutions(self):
        available_pieces = []
        for piece, count in self.pieces:
            for _ in range(count):
                available_pieces.append(piece())

        for pieces in permutations(available_pieces):
            for row in range(self.rows):
                for col in range(self.cols):
                    available_pieces = deque(pieces)
                    board = Board.new(self.rows, self.cols)
                    while available_pieces and board.next_position()[0] is not None:
                        next_piece = available_pieces.popleft()
                        for arow, acol in board.available_positions():
                            if board.add_piece(next_piece, arow, acol):
                                break
                        else:
                            available_pieces.appendleft(next_piece)
                            del board
                            break

                    if not available_pieces:
                        yield board


class RecursiveBruteForceSolver(Solver):

    completed = set()

    @classmethod
    def identifier(cls):
        return 'recursive'

    def _solutions(self):
        available_pieces = []
        for piece, count in self.pieces:
            for _ in range(count):
                available_pieces.append(piece())

        RecursiveBruteForceSolver.completed = set()
        recursive_function = RecursiveBruteForceSolver._solutions_recursive

        board = Board.new(self.rows, self.cols)
        for solution in recursive_function(board, available_pieces, 0, 0):
            print(solution.pieces)
            yield solution

    @staticmethod
    def _solutions_recursive(board: Board, pieces: list, row: int, col: int):
        if set(board.pieces) not in RecursiveBruteForceSolver.completed:

            if not pieces:
                RecursiveBruteForceSolver.completed.add(frozenset(board.pieces))
                yield board

            if board.next_position()[0] is not None:
                for index, piece in enumerate(pieces):
                    next_board = board.copy()
                    for next_row, next_col in board.available_positions():
                        if next_board.add_piece(piece, next_row, next_col):
                            next_pieces = pieces.copy()
                            del next_pieces[index]
                            yield from RecursiveBruteForceSolver._solutions_recursive(next_board, next_pieces, next_row, next_col)
                            next_board = board.copy()

            # remove = {completed for completed in RecursiveBruteForceSolver.completed if completed.intersection(board.pieces) == board.pieces}
            # RecursiveBruteForceSolver.completed -= remove

            RecursiveBruteForceSolver.completed.add(frozenset(board.pieces))


