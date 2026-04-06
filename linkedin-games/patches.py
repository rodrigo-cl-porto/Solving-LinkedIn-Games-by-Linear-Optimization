from enum import StrEnum

from cycler import V
from pkg_resources import _initialize
import pyomo.environ as pyo

class RecType(StrEnum):
    ANY = "Any"
    VERTICAL = "Vertical"
    HORIZONTAL = "Horizontal"
    SQUARE = "Square"

class Rectangle():
    def __init__(self, name:str, tip_square:tuple[int], type:RecType=RecType.ANY, area:int=None, color:str="#FFFFFF"):
        self.name = name
        self.tip_square = tip_square
        self.type = type
        self.area = area
        self.color = color

class Patches(pyo.ConcreteModel):

    def __init__(self, board_dims:tuple[int]=(6,6), rectangles:tuple[Rectangle]=()):
        
        if len(rectangles) < 1:
            raise ValueError("The tuple of rectangles cannot be empty.")
        
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
        A = self.A = pyo.Set(initialize=[k for k in rectangles if k.area != None])

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
            rule=lambda self, i, j: sum(x[i,j,k] for k in K) == 1
        )

        self.last_row_position_constraints = pyo.Constraint(
            K,
            rule=lambda self, k: r[k] + h[k] - 1 <= m
        )

        self.last_column_position_constraints = pyo.Constraint(
            K,
            rule=lambda self, k: c[k] + w[k] - 1 <= n
        )

        self.row_lower_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda self, i, j, k: r[k] - i <= m*(1 - x[i,j,k])
        )

        self.row_upper_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda self, i, j, k: i - (r[k] + h[k] - 1) <= m*(1 - x[i,j,k])
        )

        self.column_lower_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda self, i, j, k: c[k] - j <= n*(1 - x[i,j,k])
        )

        self.row_upper_bound_coverage_constraints = pyo.Constraint(
            I, J, K,
            rule= lambda self, i, j, k: j - (c[k] + w[k] - 1) <= n*(1 - x[i,j,k])
        )
    
    
    def solve(self):
        pass

    def show(self):
        pass