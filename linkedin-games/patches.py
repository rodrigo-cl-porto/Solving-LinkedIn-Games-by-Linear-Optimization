from enum import StrEnum
from math import sqrt
import re

from pyomo.opt import SolverStatus, TerminationCondition
import matplotlib.pyplot as plt
import networkx as nx
import pyomo.environ as pyo


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


class Patches(pyo.ConcreteModel):

    def __init__(self, board_dims:tuple[int], rectangles:dict[str, Rectangle]):
        
        super().__init__()

        if len(rectangles) < 1:
            raise ValueError("The dictionary of rectangles cannot be empty.")
        else:
            self.Rectangles = rectangles

        # Board Parameters
        m, n = board_dims
        self.m = pyo.Param(initialize=m, within=pyo.PositiveIntegers)
        self.n = pyo.Param(initialize=n, within=pyo.PositiveIntegers)

        # Ranges
        I = self.I = pyo.RangeSet(m) # Row index
        J = self.J = pyo.RangeSet(n) # Column index
        K = self.K = pyo.Set(initialize=rectangles.keys()) # Rectangle index

        # Sets
        S = self.S = pyo.Set(initialize=lambda model: [(i, j) for i in I for j in J])
        T = self.T = pyo.Set(initialize=[(*k.tip_square, key) for key, k in rectangles.items()])
        V = self.V = pyo.Set(initialize=[key for key, k in rectangles.items() if k.tip_type == RecType.VERTICAL])
        H = self.H = pyo.Set(initialize=[key for key, k in rectangles.items() if k.tip_type == RecType.HORIZONTAL])
        Q = self.Q = pyo.Set(initialize=[key for key, k in rectangles.items() if k.tip_type == RecType.SQUARE])
        A = self.A = pyo.Set(initialize=[key for key, k in rectangles.items() if k.tip_area is not None])

        # Decision Variables
        x = self.x = pyo.Var(I, J, K, domain=pyo.Binary, initialize=0)
        c = self.c = pyo.Var(K, domain=pyo.PositiveIntegers)
        r = self.r = pyo.Var(K, domain=pyo.PositiveIntegers)
        w = self.w = pyo.Var(K, domain=pyo.PositiveIntegers)
        h = self.h = pyo.Var(K, domain=pyo.PositiveIntegers)

        # Parameters
        a = self.a = pyo.Param(K, initialize={key: k.tip_area for key, k in rectangles.items() if k.tip_area is not None})

        # Objective Function
        self.obj = pyo.Objective(expr=sum(w[k] + h[k] for k in K), sense=pyo.minimize)

        # Constraints
        self.unique_rectangle_per_square_constraints = pyo.Constraint(
            S,
            rule= lambda model, i, j: sum(x[i,j,k] for k in K) == 1
        )

        # Rectangle-Inside-Board Constraints
        self.last_row_position_constraints = pyo.Constraint(
            K,
            rule= lambda model, k: r[k] + h[k] - 1 <= m
        )

        self.last_column_position_constraints = pyo.Constraint(
            K,
            rule=lambda model, k: c[k] + w[k] - 1 <= n
        )

        # Square-Inside-Rectangle Constraints
        self.row_lower_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda model, i, j, k: r[k] - i <= m*(1 - x[i,j,k])
        )

        self.row_upper_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda model, i, j, k: i - (r[k] + h[k] - 1) <= m*(1 - x[i,j,k])
        )

        self.column_lower_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda model, i, j, k: c[k] - j <= n*(1 - x[i,j,k])
        )

        self.column_upper_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda model, i, j, k: j - (c[k] + w[k] - 1) <= n*(1 - x[i,j,k])
        )

        # Tip Constraints
        self.tip_square_constraints = pyo.Constraint(
            T,
            rule= lambda model, i, j, k: x[i,j,k] == 1
        )
    
        self.tip_area_constraints = pyo.Constraint(
            A,
            rule= lambda model, k: sum(x[i,j,k] for (i,j) in S) == a[k]
        )

        self.vertical_rectangle_constraints = pyo.Constraint(
            V,
            rule= lambda model, k: w[k] <= h[k] - 1
        )

        self.horizontal_rectangle_constraints = pyo.Constraint(
            H,
            rule= lambda model, k: w[k] >= h[k] + 1
        )

        self.square_rectangle_constraints = pyo.Constraint(
            Q,
            rule= lambda model, k: w[k] == h[k]
        )
    
    
    def solve(self) -> None:
        result = pyo.SolverFactory("highs").solve(self)

        if result.Solver.status == SolverStatus.ok and result.solver.termination_condition == TerminationCondition.optimal:
            print("Optimal solution found!")
            for k in self.K:
                rect = self.Rectangles[k]
                rect.x = int(round(self.c[k].value, 0))
                rect.y = int(round(self.r[k].value, 0))
                rect.width = int(round(self.w[k].value, 0))
                rect.height = int(round(self.h[k].value, 0))
                print(f"{k}: {repr(rect)}")
        else:
            print("It was not possible to find a feasible solution for the game.")
            print(result.solver)


    def show(self) -> None:

        G = nx.grid_2d_graph(self.m.value, self.n.value)
        plt.figure(figsize=(3, 3))

        nx.draw(
            G,
            pos= {(i, j): (j, -i) for (i, j) in G.nodes()},
            node_size= 1100,
            node_shape="s",
            node_color= [self.Rectangles[k].color for i in self.I for j in self.J for k in self.K if round(self.x[i,j,k].value, 0) == 1],
            width= 0,
        )
        plt.show()


if __name__ == "__main__":

    # Example of Tango No. 15
    rectangles = {
        "yellow":  Rectangle((1, 2), RecType.ANY,      2, "#846A0B"),
        "teal":    Rectangle((1, 4), RecType.ANY,      6, "#096B78"),
        "purple":  Rectangle((2, 6), RecType.ANY,      2, "#5A3DB1"),
        "green":   Rectangle((3, 1), RecType.ANY,      6, "#0A7541"),
        "orange":  Rectangle((3, 3), RecType.VERTICAL, 2, "#EF6C00"),
        "red":     Rectangle((4, 4), RecType.SQUARE,   4, "#E30102"),
        "blue":    Rectangle((4, 6), RecType.ANY,      2, "#097BB1"),
        "magenta": Rectangle((5, 1), RecType.ANY,      2, "#A01E4E"),
        "brick":   Rectangle((6, 3), RecType.ANY,      6, "#9B3C1C"),
        "brown":   Rectangle((6, 5), RecType.ANY,      4, "#503B36")
    }

    patches = Patches((6,6), rectangles)
    patches.solve()
    patches.show()