from pyomo.opt import SolverStatus, TerminationCondition
import matplotlib.pyplot as plt
import networkx as nx
import pyomo.environ as pyo

class Queens(pyo.ConcreteModel):

    def __init__(self, board_dims:tuple[int], regions:dict) -> None:

        super().__init__()

        m, n = board_dims
        self.m = pyo.Param(initialize=m, within=pyo.PositiveIntegers)
        self.n = pyo.Param(initialize=n, within=pyo.PositiveIntegers)

        # Ranges
        I = self.I = pyo.RangeSet(n)
        J = self.J = pyo.RangeSet(m)
        K = self.Colors = pyo.Set(initialize=regions.keys())

        # Sets
        S = self.S = pyo.Set(initialize=lambda model: [(i,j) for i in I for j in J])
        R = self.R = pyo.Set(K, initialize=regions, dimen=2)
        D = self.D = pyo.Set(initialize=lambda model: [
            ((i, j), (i+1, j+1)) for (i,j) in S if (i+1,j+1) in S] + [
            ((i, j), (i+1, j-1)) for (i,j) in S if (i+1,j-1) in S
        ])

        # Objective function
        self.obj = pyo.Objective(expr=0, sense=pyo.maximize)

        # Decision Variables
        x = self.x = pyo.Var(S, within=pyo.Binary, initialize=0)

        # Constraints
        self.single_crown_per_row_constraints = pyo.Constraint(
            I,
            rule=lambda model, i: sum(x[i,j] for j in J) == 1
        )

        self.single_crown_per_column_constraints = pyo.Constraint(
            J,
            rule=lambda model, j: sum(x[i,j] for i in I) == 1
        )

        self.single_crown_per_region_constraints = pyo.Constraint(
            K,
            rule=lambda model, k: sum(x[i,j] for (i,j) in R[k]) == 1
        )

        self.adjacent_squares_by_vertex_constraints = pyo.Constraint(
            D,
            rule=lambda model, i, j, r, s: x[i,j] + x[r,s] <= 1
        )


    def solve(self):

        # Optmization result
        result = pyo.SolverFactory("gurobi").solve(self)

        if result.Solver.status == SolverStatus.ok and result.Solver.termination_condition == TerminationCondition.feasible:
            print("Queens solved successfully!")
        else:
            print("No feasible solution was found!")
            print(result.Solver)
        


    def show(self):

        G = nx.grid_2d_graph(self.n, self.m)
        plt.figure(figsize=(3.4, 3.4))
        
        squares = [(i-1, j-1) for (i,j) in sorted(list(self.S))]

        color_map = [{(i-1, j-1): region for (i,j) in squares} for region, squares in regions.items()]
        color_map = {square: region for d in color_map for square, region in d.items()}
        color_map = [color_map[square] for square in squares]
        
        hex_map = {
            "purple": "#BBA3E1",
            "orange": "#FFC794",
            "blue": "#94BEFF",
            "green": "#B3DF9E",
            "gray": "#E0E0E0",
            "red": "#FF7B61",
            "yellow": "#E6F388"
        }

        color_map = [hex_map[color] for color in color_map]
        solution = [(i, j) for i in self.I for j in self.J if round(self.x[i,j].value, 0) == 1]

        nx.draw(
            G,
            pos= {(i,j): (j, -i) for i, j in G.nodes()},
            with_labels= True,
            labels= {(i-1, j-1): "O" for (i,j) in solution},
            node_size= 1000,
            node_color= color_map,
            node_shape="s",
            width=0
        )
        plt.show()


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

    queens = Queens((7,7), regions)
    queens.solve().show()