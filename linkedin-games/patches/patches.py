from pyomo.opt import SolverStatus, TerminationCondition
import matplotlib.pyplot as plt
import networkx as nx
import pyomo.environ as pyo

from .rectangle import Rectangle, RecType


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
        S = self.S = pyo.Set(initialize=lambda model: [(i, j) for i in I for j in J]) # Set of all board squares
        T = self.T = pyo.Set(initialize=[(*rect.tip_square, key) for key, rect in rectangles.items()])
        V = self.V = pyo.Set(initialize=[key for key, rect in rectangles.items() if rect.tip_type == RecType.VERTICAL])
        H = self.H = pyo.Set(initialize=[key for key, rect in rectangles.items() if rect.tip_type == RecType.HORIZONTAL])
        Q = self.Q = pyo.Set(initialize=[key for key, rect in rectangles.items() if rect.tip_type == RecType.SQUARE])
        A = self.A = pyo.Set(initialize=[key for key, rect in rectangles.items() if rect.tip_area is not None])

        # Decision Variables
        x = self.x = pyo.Var(I, J, K, domain=pyo.Binary, initialize=0)
        c = self.c = pyo.Var(K, domain=pyo.PositiveIntegers)
        r = self.r = pyo.Var(K, domain=pyo.PositiveIntegers)
        w = self.w = pyo.Var(K, domain=pyo.PositiveIntegers)
        h = self.h = pyo.Var(K, domain=pyo.PositiveIntegers)

        # Parameters
        a = self.a = pyo.Param(
            K,
            initialize= {key: rect.tip_area for key, rect in rectangles.items() if rect.tip_area is not None}
        )

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

        if result.Solver.status == SolverStatus.ok and result.Solver.termination_condition == TerminationCondition.optimal:
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
            print(result.Solver)


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