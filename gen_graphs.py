import random
import sys

class Graph(object):
    def __init__(self, node_count = 0):
        self._adj_mat = [[0] * node_count for _ in range(node_count)]

    def add_node(self):
        self._adj_mat.append([0] * len(self._adj_mat))
        for row in self._adj_mat:
            row.append(0)

    def add_edge(self, v, w):
        self._adj_mat[v][w] = True
        self._adj_mat[w][v] = True

    def nodes(self):
        return list(range(len(self._adj_mat)))

    def number_of_nodes(self):
        return len(self._adj_mat)

    def adj_row(self, v):
        return self._adj_mat[v]

    def induced_subgraph(self, vv):
        result = Graph(len(vv))
        for i, v in enumerate(vv):
            for j, w in enumerate(vv):
                if self._adj_mat[v][w]:
                    result.add_edge(i, j)
        return result

    def density(self):
        n = self.number_of_nodes()
        if n < 2:
            return -1
        return float(sum(sum(row) for row in self._adj_mat)) / (n * (n - 1))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 {} MAX_N SEED".format(sys.argv[0]))
        exit(1)

    max_n = int(sys.argv[1])
    random.seed(int(sys.argv[2]))

    G = Graph(max_n)
    H = Graph(max_n)

    for v in range(max_n):
        for w in range(v):
            if random.random() < 0.5:
                G.add_edge(v, w)
            if random.random() < 0.5:
                H.add_edge(v, w)
    for order in range(1, max_n + 1):
        for graph_name, g in [("G", G), ("H", H)]:
            with open("generated-graphs/" + graph_name + str(order) + ".grf", "w") as f:
                graph = g.induced_subgraph(list(range(order)))
                f.write("p edge {} {}\n".format(graph.number_of_nodes(), 0))
                for v, row in enumerate(graph._adj_mat):
                    for w, has_edge in enumerate(row):
                        if has_edge and w > v:
                            f.write("e {} {}\n".format(v + 1, w + 1))
