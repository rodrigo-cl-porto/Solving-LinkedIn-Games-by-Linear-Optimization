from enum import StrEnum
from math import sqrt
import pyomo.environ as pyo
import matplotlib.pyplot as plt
import networkx as nx
import re

class RecType(StrEnum):
    ANY = "Any"
    VERTICAL = "Vertical"
    HORIZONTAL = "Horizontal"
    SQUARE = "Square"


class Rectangle():
    
    def __init__(
        self,
        tip_square:tuple[int],
        type:RecType=RecType.ANY,
        area:int=None,
        color:str="#FFFFFF",
        width:int=0,
        height:int=0,
        x:int=0,
        y:int=0
    ):
        self.tip_square = tip_square
        self.type = type
        self.color = color
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        if area is not None:
            if area < 1:
                raise ValueError("The area must be a positive integer.")

            if type == RecType.SQUARE:
                if Rectangle.__is_perfect_square(area):
                    self.area = area
                else:
                    raise ValueError("The informed area is not a perfect square.")
                
            self.area = area
    
    @staticmethod
    def __is_perfect_square(n:int) -> bool:
        return sqrt(n) % 1 == 0
    
    @property
    def type(self) -> RecType:
        return self.type

    @property
    def tip_square(self) -> tuple[int]:
        return self.tip_square

    @property
    def area(self) -> int:
        return self.area
    
    @area.setter
    def area(self, area:int):
        if area < 1:
            raise ValueError("The area must be a positive integer.")

        if self.type == RecType.SQUARE:
            if Rectangle.__is_perfect_square(area):
                self.area = area
            else:
                raise ValueError("The informed area is not a perfect square.")
                
        self.area = area

    @property
    def color(self) -> str:
        return self.color
    
    @color.setter
    def color(self, color:str):
        pattern = re.compile(r"^\#[0-9A-F]{6}$", re.IGNORECASE)
        if re.fullmatch(pattern, color):
            self.color = color
        else:
            raise ValueError("The color must be a hex code.")
    
    @property
    def width(self) -> int:
        return self.width
    
    @width.setter
    def width(self, width:int):
        if width < 1:
            raise ValueError("The width must be a positive integer.")
        
        if type(width) != int or width % 1 != 0:
            raise TypeError("The width must be a positive integer")
        
        self.width = width

    @property
    def height(self) -> int:
        return self.height
    
    @height.setter
    def height(self, height:int):
        if height < 1:
            raise ValueError("The height must be a positive integer.")
        
        if type(height) != int or height % 1 != 0:
            raise TypeError("The height must be a positive integer")
        
        self.height = height
    
    @property
    def x(self) -> int:
        return self.x
    
    @x.setter
    def x(self, x:int):
        if x < 1:
            raise ValueError("The x position must be a positive integer.")
        
        if type(x) != int or x % 1 != 0:
            raise TypeError("The x position must be a positive integer")
        
        self.x = x

    @property
    def y(self) -> int:
        return self.y
    
    @y.setter
    def y(self, y:int):
        if y < 1:
            raise ValueError("The y position must be a positive integer.")
        
        if type(y) != int or y % 1 != 0:
            raise TypeError("The y position must be a positive integer")

        self.y = y


class Patches(pyo.ConcreteModel):

    def __init__(self, board_dims:tuple[int], rectangles:dict[str, Rectangle]):
        
        if len(rectangles) < 1:
            raise ValueError("The tuple of rectangles cannot be empty.")
        else:
            self.Rectangles = rectangles
        
        # Board Parameters
        m, n = board_dims
        self.m = pyo.Param(m, within=pyo.PositiveIntegers)
        self.n = pyo.Param(n, within=pyo.PositiveIntegers)

        # Ranges
        I = self.I = pyo.Range(m) # Row index
        J = self.J = pyo.Range(n) # Column index
        K = self.K = pyo.RangeSet(initialize= [k.name for k in rectangles]) # Rectangle index

        # Sets
        S = self.S = pyo.Set(initialize=lambda model: [(i, j) for i in I for j in J])
        T = self.T = pyo.Set(initialize=[k.tip_square for k in rectangles], dimen=2)
        V = self.V = pyo.Set(initialize=[k for k in rectangles if k.type == RecType.VERTICAL])
        H = self.H = pyo.Set(initialize=[k for k in rectangles if k.type == RecType.HORIZONTAL])
        Q = self.Q = pyo.Set(initialize=[k for k in rectangles if k.type == RecType.SQUARE])
        A = self.A = pyo.Set(initialize=[k for k in rectangles if k.area is not None])

        # Decision Variables
        x = self.x = pyo.Var(I, J, K, domain=pyo.Binary)
        c = self.c = pyo.Var(K, domain=pyo.PositiveIntegers)
        w = self.w = pyo.Var(K, domain=pyo.PositiveIntegers)
        r = self.r = pyo.Var(K, domain=pyo.PositiveIntegers)
        h = self.h = pyo.Var(K, domain=pyo.PositiveIntegers)

        # Parameters
        a = self.a = pyo.Param(initialize={k.name: k.area for k in K if k.area is not None})

        # Objective Function
        self.obj = pyo.Objective(expr=0)

        # Constraints
        self.unique_rectangle_per_square_constraints = pyo.Constraint(
            K,
            rule=lambda model, i, j: sum(x[i,j,k] for k in K) == 1
        )

        # Rectangle-Inside-Board Constraints
        self.last_row_position_constraints = pyo.Constraint(
            K,
            rule=lambda model, k: r[k] + h[k] - 1 <= m
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

        self.row_upper_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda model, i, j, k: j - (c[k] + w[k] - 1) <= n*(1 - x[i,j,k])
        )

        # Tip Constraints
        self.tip_square_constraints = pyo.Constraint(
            T,
            rule= lambda model, i, j, k: x[i,j,k] == 1
        )
    
        self.prescribed_area_constraints = pyo.Constraint(
            A,
            rule= lambda model, k: sum(x[i,j,k] for i in I for j in J) == a[k]
        )

        self.vertical_rectangle_constraints = pyo.Constraint(
            V,
            rule= lambda model, k: w[k] < h[k]
        )

        self.horizontal_rectangle_constraints = pyo.Constraint(
            H,
            rule= lambda model, k: w[k] > h[k]
        )

        self.square_rectangle_constraints = pyo.Constraint(
            Q,
            rule= lambda model, k: w[k] == h[k]
        )

    
    def solve(self) -> None:
        solver = pyo.SolverFactory("gurobi")
        solver.solve(self)


    def show(self):
        plt.figure(figsize=(3, 3))
        nx.draw(
            G= self.matrix,
            pos= {(i, j): (j, -i) for (i, j) in self.matrix.nodes()},
            with_labels= True,
            labels= {n: self.matrix.nodes[n]["value"] for n in self.matrix.nodes() if self.matrix.nodes[n]["value"] != 0},
            font_color="white",
            node_size= 1100,
            node_shape="s",
            node_color= "#1B1F22",
            width= 0,
            edgecolors="#999999",
            linewidths= .5,
        )
        plt.show()


if __name__ == "__main__":
    pass