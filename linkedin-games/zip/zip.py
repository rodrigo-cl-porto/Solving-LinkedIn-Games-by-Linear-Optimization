from pyomo.opt import SolverStatus, TerminationCondition
import matplotlib.pyplot as plt
import networkx as nx
import pyomo.environ as pyo


class Zip(pyo.ConcreteModel):

    def __init__(self, board_dims:tuple[int], numbered_squares:dict|list, walls:list=None):

        super().__init__()

        # Board dimensions
        m, n = board_dims
        M = m*n
        self.m = pyo.Param(initialize=m, within=pyo.PositiveIntegers)
        self.n = pyo.Param(initialize=n, within=pyo.PositiveIntegers)

        if M < 2:
            raise ValueError("The board size is too small.")

        if len(numbered_squares) > M:
            raise ValueError("The number of numbered squares exceeds the amount of vertices in the grid.")
        
        if len(numbered_squares) < 2:
            raise ValueError("The quantity of numbered squares is too small.")

        if isinstance(numbered_squares, list):
            numbered_squares = {key: value for key, value in enumerate(numbered_squares)}
        elif not isinstance(numbered_squares, dict):
            raise ValueError("The numbered squares must be a dictionary or a list.")

        # Ranges
        I = self.I = pyo.RangeSet(m)
        J = self.J = pyo.RangeSet(n)

        # Sets
        V = self.V = pyo.Set(initialize=lambda model: [(i, j) for i in I for j in J])
        E = self.E = pyo.Set(initialize=lambda model: [
            ((i, j), (i+1, j)) for i in I for j in J if i+1 in I] + [
            ((i, j), (i-1, j)) for i in I for j in J if i-1 in I] + [
            ((i, j), (i, j+1)) for i in I for j in J if j+1 in J] + [
            ((i, j), (i, j-1)) for i in I for j in J if j-1 in J]
        )
        K = self.K = pyo.Set(initialize=numbered_squares.keys(), dimen=2)
        W = self.W = pyo.Set(initialize=walls)
        
        # Decision variables
        x = self.x = pyo.Var(E, within=pyo.Binary, initialize=0)
        u = self.u = pyo.Var(V, within=pyo.NonNegativeReals)

        # Parameters
        k = self.k = pyo.Param(V, initialize=numbered_squares, default=0, within=pyo.NonNegativeIntegers)

        # Objective function
        self.obj = pyo.Objective(expr=0)
    
        # Constraints
        self.outgoing_edges_constraints = pyo.Constraint(
            V,
            rule=lambda model, i, j: \
                sum(x[(i,j),w] for w in V if ((i,j),w) in E) == 1 if k[i,j] != len(K) else \
                sum(x[(i,j),w] for w in V if ((i,j),w) in E) == 0
        )
        
        self.incoming_edges_constraints = pyo.Constraint(
            V,
            rule=lambda model, i, j: \
                sum(x[v,(i,j)] for v in V if (v,(i,j)) in E) == 1 if k[i,j] != 1 else \
                sum(x[v,(i,j)] for v in V if (v,(i,j)) in E) == 0
        )
    
        if W is not None:
            self.wall_constraints = pyo.Constraint(
                W,
                rule=lambda model, i, j, r, s: x[i,j,r,s] + x[r,s,i,j] == 0
            )
    
        M = n * m
    
        self.subroute_elimination_constraints = pyo.Constraint(
            E,
            rule=lambda model, i, j, r, s: u[r,s] >= u[i,j] + 1 - M*(1 - x[i,j,r,s])
        )
        
        self.first_square_position_constraint = pyo.Constraint(
            K,
            rule= lambda model, i, j: u[i,j] == 1 if k[i,j] == 1 else pyo.Constraint.Skip
        )
        
        self.ordinal_position_constraints = pyo.Constraint(
            K, K,
            rule= lambda model, i, j, r, s: u[i,j] >= u[r,s] + 1 if k[i,j] == k[r,s] + 1 else pyo.Constraint.Skip
        )
        
        self.last_square_position_constraint = pyo.Constraint(
            K,
            rule= lambda model, i, j: u[i,j] == M if k[i,j] == len(K) else pyo.Constraint.Skip
        )


    def solve(self, verbose:bool=False):

        result = pyo.SolverFactory("highs").solve(self)

        if result.Solver.status == SolverStatus.ok and result.Solver.termination_condition == TerminationCondition.feasible:
            print("Zip solved successfully!")
        else:
            print("No feasible solution was found!")
            print(result.Solver)


    def show(self):

        G = nx.grid_2d_graph(self.n, self.m).to_directed()
        plt.figure(figsize=(3.4, 3.4))
        
        nx.draw(
            G,
            pos= {(i,j): (j,-i) for i, j in G.nodes()},
            with_labels= True,
            labels= {(i-1, j-1): self.k[i,j] for (i,j) in self.K},
            arrows=False,
            node_shape="o", # round nodes
            node_size= 1000,
            node_color= ["white" if (i+1,j+1) in self.K else "#EE5F12" for (i,j) in G.nodes()],
            edge_color= "#EE5F12",
            edgecolors='#EE5F12',
            linewidths= 3,
            width= 35,
            edgelist= [((i-1, j-1), (r-1, s-1)) for i,j,r,s in self.E if round(self.x[i,j,r,s].value) == 1]
        )
        plt.show()


if __name__ == "__main__":

    # Zip No. 166
    
    numbered_squares = {
        (1,1):  9,
        (1,2): 10,
        (1,3): 11,
        (2,1):  8,
        (2,4): 13,
        (3,1):  7,
        (3,4): 14,
        (3,5): 12,
        (4,2):  6,
        (4,3): 15,
        (4,6): 16,
        (5,3):  5,
        (5,6):  3,
        (6,4):  4,
        (6,5):  1,
        (6,6):  2
    }

    zip = Zip((6,6), numbered_squares)
    zip.solve()
    zip.show()