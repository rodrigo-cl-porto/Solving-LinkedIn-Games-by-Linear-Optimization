from pyomo.opt import SolverStatus, TerminationCondition
import matplotlib.pyplot as plt
import networkx as nx
import pyomo.environ as pyo


class Tango(pyo.ConcreteModel):

    def __init__(self, board_dims:tuple[int], like_pairs:dict, opp_pairs:dict, filled_squares:dict):

        super().__init__()

        # Board dimensions
        m, n = board_dims
        self.m = pyo.Param(initialize=m, within=pyo.PositiveIntegers)
        self.n = pyo.Param(initialize=n, within=pyo.PositiveIntegers)

        # Ranges
        I = self.I = pyo.RangeSet(n)
        J = self.J = pyo.RangeSet(m)

        # Sets
        S = self.squares = pyo.Set(initialize=lambda model: [(i, j) for i in I for j in J])
        L = self.L = pyo.Set(initialize=like_pairs)
        O = self.O = pyo.Set(initialize=opp_pairs)
        K = self.K = pyo.Set(initialize=filled_squares.keys(), dimen=2)

        # Decision variables
        x = self.x = pyo.Var(I, J, within=pyo.Binary)
    
        # Parameters
        k = self.FilledValues = pyo.Param(K, initialize=filled_squares, within=pyo.Binary)

        # Objective function
        self.obj = pyo.Objective(expr=0, sense=pyo.maximize)

        # Constraints
        self.equal_moons_suns_per_row_constraints = pyo.Constraint(
            I,
            rule=lambda model, i: sum(x[i,j] for j in J) == n/2
        )

        self.equal_moons_suns_per_column_constraints = pyo.Constraint(
            J,
            rule=lambda model, j: sum(x[i,j] for i in I) == m/2
        )

        self.no_three_consecutive_moons_per_row_constraints = pyo.Constraint(
            I, pyo.RangeSet(n-2),
            rule=lambda model, i, j: x[i,j] + x[i,j+1] + x[i,j+2] <= 2
        )
    
        self.no_three_consecutive_suns_per_row_constraints = pyo.Constraint(
            I, pyo.RangeSet(n-2),
            rule=lambda model, i, j: x[i,j] + x[i,j+1] + x[i,j+2] >= 1
        )

        self.no_three_consecutive_moons_per_column_constraints = pyo.Constraint(
            pyo.RangeSet(m-2), J,
            rule=lambda model, i, j: x[i,j] + x[i+1,j] + x[i+2,j] <= 2
        )
        
        self.no_three_consecutive_suns_per_column_constraints = pyo.Constraint(
            pyo.RangeSet(m-2), J,
            rule=lambda model, i, j: x[i,j] + x[i+1,j] + x[i+2,j] >= 1
        )

        self.like_pairs_constraints = pyo.Constraint(
            L,
            rule=lambda model, i, j, r, s: x[i,j] - x[r,s] == 0
        )

        self.opposite_pairs_constraints = pyo.Constraint(
            O,
            rule=lambda model, i, j, r, s: x[i,j] + x[r,s] == 1
        )

        self.already_filled_squares_constraints = pyo.Constraint(
            K,
            rule=lambda model, i, j: x[i,j] == k[i,j]
        )

    
    def solve(self):

        result = pyo.SolverFactory("gurobi").solve(self)

        if result.Solver.status == SolverStatus.ok and result.Solver.termination_condition == TerminationCondition.feasible:
            print("Tango solved successfully!")
        else:
            print("No feasible solution was found!")
            print(result.Solver)

    
    def show(self):
        
        G = nx.grid_2d_graph(self.m, self.n)
        pos = {(i,j): (j, -i) for i, j in G.nodes()}
        
        plt.figure(figsize=(3.4, 3.4))
        
        nx.draw(
            G,
            pos= pos,
            with_labels= True,
            labels= {(i,j): int(self.x[i+1,j+1].value) for i, j in G.nodes()},
            node_size= 1000,
            node_color= ["#EEEAE7" if (i+1,j+1) in self.K else "white" for (i,j) in G.nodes()],
            node_shape="s",
            edgecolors="#EEEAE7",
            linewidths= 1,
            width= 0,
            edgelist = [
                ((i-1, j-1), (r-1,s-1)) for i,j,r,s in self.O] + [
                ((i-1, j-1), (r-1,s-1)) for i,j,r,s in self.L
            ]
        )
        nx.draw_networkx_edge_labels(
            G,
            pos= pos,
            edge_labels= {
                ((i-1, j-1), (r-1,s-1)): "×" for i,j,r,s in self.O} | {
                ((i-1, j-1), (r-1,s-1)): "=" for i,j,r,s in self.L
            },
            font_color="#887658"
        )
        plt.show()


if __name__ == "__main__":

    # like (=) pairs, each element is ((i,j),(r,s))
    like_pairs = [
        ((2, 3), (2, 4)),
        ((2, 1), (3, 1)),
        ((2, 3), (3, 3)),
        ((2, 6), (3, 6)),
        ((4, 1), (4, 2)),
        ((6, 3), (6, 4)),
    ]

    # opposite (X) pairs
    opp_pairs = [
        ((2, 4), (3, 4)),
        ((3, 1), (4, 1)),
        ((3, 3), (3, 4)),
        ((3, 6), (4, 6)),
        ((4, 5), (4, 6)),
    ]

    # helper lists for the concrete instance (Tango #151)
    # already filled squares: (i,j) -> kij
    filled_squares = {
        (1, 2): 1,
        (1, 5): 1,
        (5, 2): 0,
        (5, 5): 1,
    }

    tango = Tango((6,6), like_pairs, opp_pairs, filled_squares)
    tango.solve().show()