from enum import StrEnum
from math import sqrt
import re


class RecType(StrEnum):
    ANY = "Any"
    VERTICAL = "Vertical"
    HORIZONTAL = "Horizontal"
    SQUARE = "Square"


class Rectangle():
    
    def __init__(self,
        tip_square:tuple[int],
        tip_type:RecType=RecType.ANY,
        tip_area:int=None,
        color:str="#FFFFFF",
        width:int=0,
        height:int=0,
        x:int=0,
        y:int=0
    ):
        self._tip_square = tip_square
        self._tip_type = tip_type
        self._tip_area = tip_area
        self._color = color
        self._x = x
        self._y = y
        self._width = width
        self._height = height


    def __repr__(self) -> str:
        return f"Rectangle(\n\ttip_square={self.tip_square},\n\ttip_type={self.tip_type},\n\ttip_area={self.tip_area},\n\tx={self.x},\n\ty={self.y},\n\twidth={self.width},\n\theight={self.height}\n)"


    def __str__(self) -> str:
        return f"Rectangle(x={self.x}, y={self.y},  width={self.width}, height={self.height}, squares={self.squares})"


    def __eq__(self, other) -> bool:
        return \
            self.x == other.x and \
            self.y == other.y and \
            self.width == other.width and \
            self.height == other.height


    @staticmethod
    def __is_perfect_square(n:int) -> bool:
        return sqrt(n) % 1 == 0


    @property
    def tip_type(self) -> RecType:
        return self._tip_type


    @tip_type.setter
    def tip_type(self, value:RecType) -> RecType:
        self._tip_type = value


    @property
    def tip_square(self) -> tuple[int]:
        return self._tip_square


    @tip_square.setter
    def tip_square(self, value:tuple[int]):
        self._tip_square = value


    @property
    def tip_area(self) -> int:
        return self._tip_area


    @tip_area.setter
    def tip_area(self, value:int):
        if value < 1:
            raise ValueError("The area must be a positive integer.")

        if self.tip_type == RecType.SQUARE:
            if Rectangle.__is_perfect_square(value):
                self._tip_area = value
            else:
                raise ValueError("The informed area is not a perfect square.")
                
        self._tip_area = value


    @property
    def area(self):
        return self._width * self._height


    @property
    def color(self) -> str:
        return self._color


    @color.setter
    def color(self, value:str):
        pattern = re.compile(r"^\#[0-9A-F]{6}$", re.IGNORECASE)
        if re.fullmatch(pattern, value):
            self._color = value
        else:
            raise ValueError("The color must be a hex code.")


    @property
    def width(self) -> int:
        return self._width


    @width.setter
    def width(self, value:int):
        if value < 1:
            raise ValueError("The width must be a positive integer.")
        
        if value % 1 != 0:
            raise TypeError("The width must be a positive integer")
        
        self._width = int(value)


    @property
    def height(self) -> int:
        return self._height


    @height.setter
    def height(self, value:int):
        if value < 1:
            raise ValueError("The height must be a positive integer.")
        
        if value % 1 != 0:
            raise TypeError("The height must be a positive integer")
        
        self._height = int(value)


    @property
    def x(self) -> int:
        return self._x


    @x.setter
    def x(self, value:int):
        if value < 1:
            raise ValueError("The x position must be a positive integer.")
        
        if value % 1 != 0:
            raise TypeError("The x position must be a positive integer")
        
        self._x = int(value)


    @property
    def y(self) -> int:
        return self._y


    @y.setter
    def y(self, value:int):
        if value < 1:
            raise ValueError("The y position must be a positive integer.")
        
        if value % 1 != 0:
            raise TypeError("The y position must be a positive integer")

        self._y = value


    @property
    def squares(self) -> tuple[tuple[int]]:

        if self.x < 1 or self.y < 1 or self.width < 1 or self.height < 1:
            return ()

        return tuple((i,j) for i in range(self.y, self.y + self.height) for j in range(self.x, self.x + self.width))