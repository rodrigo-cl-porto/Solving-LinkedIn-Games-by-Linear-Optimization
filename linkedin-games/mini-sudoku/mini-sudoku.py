import matplotlib.pyplot as plt
import networkx as nx
import pyomo.environ as pyo


class Sudoku(pyo.ConcreteModel):
    
    def __init__(self, n, grid:tuple):

        super().__init__()

        self.__n = n

        p, q = grid

        if p*q == n:
            self.__grid = grid
        else:
            raise ValueError("The dimensions of subgrid must match with the sudoku's length")
        
        G = nx.grid_2d_graph(n, n)
        nx.set_node_attributes(G, 0, "value")
        self.matrix = G

    def set_value_to_square(self, square:tuple, value:int):
        square = tuple(i-1 for i in square)
        self.matrix.nodes[square]["value"] = value

    def get_value_from_square(self, square:tuple) -> int:
        square = tuple(i-1 for i in square)
        return self.matrix.nodes[square]["value"]

    def solve(self):

        # Setting the main inputs of the model.
        n = self.__n
        p, q = self.__grid
        filled_values = [
            (n[0]+1, n[1]+1, self.matrix.nodes[n]["value"]) \
            for n in self.matrix.nodes() if self.matrix.nodes[n]["value"] != 0
        ]

        # Instantiating the Concrete Model.
        model = pyo.ConcreteModel()
        
        # Ranges
        I = model.I = pyo.RangeSet(n)
        J = model.J = pyo.RangeSet(n)
        K = model.K = pyo.RangeSet(n)
        U = model.u = pyo.RangeSet(p)
        V = model.v = pyo.RangeSet(q)

        # Sets
        S = model.Submatrices = pyo.Set(
            V, U,
            initialize= lambda model, v, u: \
            [(i, j) for i in range(p*(v-1)+1, p*v+1) for j in range(q*(u-1)+1, q*u+1)]
        )
        F = model.FilledValues = pyo.Set(initialize=filled_values)
        
        # Decision variables
        x = model.x = pyo.Var(I, J, K, within=pyo.Binary, initialize=0)
        
        # Objective function
        model.obj = pyo.Objective(expr=0)
        
        # Constraints
        model.unique_digits_per_row_constraints = pyo.Constraint(
            J, K,
            rule=lambda model, j, k: sum(x[i,j,k] for i in I) == 1
        )

        model.unique_digits_per_column_constraints = pyo.Constraint(
            I, K,
            rule=lambda model, i, k: sum(x[i,j,k] for j in J) == 1
        )

        model.unique_digits_per_submatrix_constraints = pyo.Constraint(
            V, U, K,
            rule=lambda model, v, u, k: sum(x[i,j,k] for (i, j) in S[v,u]) == 1
        )

        model.single_digit_per_square_constraints = pyo.Constraint(
            I, J,
            rule=lambda model, i, j: sum(x[i,j,k] for k in K) == 1
        )

        model.alreadey_filled_squares_constraints = pyo.Constraint(
            F,
            rule=lambda model, i, j, k: x[i,j,k] == 1
        )
        
        # Solving the model by Gurobi.
        solver = pyo.SolverFactory("gurobi")
        solver.solve(model)

        # Saving the solution in the Sudoku grid.
        solution = [(i, j, k) for i in I for j in J for k in K if model.x[i, j, k].value == 1]
        for i, j, k in solution:
            self.set_value_to_square((i, j), k)
            
    
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

    mini_sudoku = MiniSudoku(6, (2,3))
    mini_sudoku.set_value_to_square((1,1), 1)
    mini_sudoku.set_value_to_square((2,2), 2)
    mini_sudoku.set_value_to_square((2,5), 3)
    mini_sudoku.set_value_to_square((3,3), 3)
    mini_sudoku.set_value_to_square((3,4), 6)
    mini_sudoku.set_value_to_square((4,3), 5)
    mini_sudoku.set_value_to_square((4,4), 4)
    mini_sudoku.set_value_to_square((5,2), 4)
    mini_sudoku.set_value_to_square((5,5), 5)
    mini_sudoku.set_value_to_square((6,6), 6)

    mini_sudoku.solve()
    mini_sudoku.show()