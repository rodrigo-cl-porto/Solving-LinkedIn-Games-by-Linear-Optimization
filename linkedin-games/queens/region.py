class Region():

    def __init__(self, squares:set[tuple[int]], color:str="#FFFFFF"):
        self._squares = squares
        self._color = color


    @property
    def squares(self) -> set[tuple[int]]:
        return self._squares
    

    @squares.setter
    def squares(self, value:set[tuple[int]]):
        self._squares = value


    @property
    def color(self) -> str:
        return self._color
    

    @color.setter
    def color(self, value:str):
        self._color = value


class QueensBoard():
    
    def __init__(self, rows:int, columns:int, regions:tuple[Region]):
        self._m = rows
        self._n = columns
        self._regions = regions


    @property
    def rows(self) -> int:
        return self._m
    

    @rows.setter
    def rows(self, value: int):

        if value < 1:
            msg = "The number of rows must not be less than 1."
            raise ValueError(msg)
        
        if value % 1 == 0:
            msg = "The number of rows must be an integer."
            raise TypeError(msg)
        
        self._m = int(round(value, 0))


    @property
    def columns(self) -> int:
        return self._n
    
    
    @columns.setter
    def columns(self, value: int):

        if value < 1:
            msg = "The number of columns must not be less than 1."
            raise ValueError(msg)
        
        if value % 1 == 0:
            msg = "The number of columns must be an integer."
            raise TypeError(msg)
        
        self._n = int(round(value, 0))


    @property
    def size(self) -> int:
        return self._m * self._n
    
    
    @property
    def squares(self) -> set[tuple[int]]:
        return {(i,j) for i in range(1, self._m+1) for j in range(1, self._n+1)}
    

    @property
    def regions(self) -> dict|list[Region]:
        return self._regions
    

    @regions.setter
    def regions(self, value:tuple[Region]):

        if len(value) != len({r.color for r in value}):
            msg = "There must not be two regions with the same color."
            raise ValueError(msg)
        
        if {set(r.squares) for r in value}.is
        
        self._regions = {r.color: r.squares for r in value}

        


if __name__ == "__main__":

    regions = {
        "purple": [(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (2,6), (2,7), (3,6), (3,7), (4,6), (4,7), (5,7), (6,7), (7,7)],
        "orange": [(2,1), (2,2), (2,3), (2,4), (3,1), (4,1), (4,2), (5,1), (5,2), (6,1), (6,2), (6,4), (6,5), (6,6), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6)],
        "blue": [(2,5), (3,5)],
        "green": [(3,2), (3,3)],
        "gray": [(3,4), (4,3), (4,4), (4,5), (5,4)],
        "red": [(5,3), (6,3)],
        "yellow": [(5,5), (5,6)]
    }

    game_board = QueensBoard(6,6, regions)
    print(game_board.squares)