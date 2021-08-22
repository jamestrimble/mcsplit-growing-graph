import random
import sys

tmp_counter = [0]

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

    def del_edge(self, v, w):
        self._adj_mat[v][w] = False
        self._adj_mat[w][v] = False

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


def random_graph(n):
    G = Graph(n)
    for v in range(n):
        for w in range(v):
            if random.random() < 0.5:
                G.add_edge(v, w)
    return G


class LabelClass(object):
    """A label class, used by the McSplit algorithm.

    A label class contains a list of nodes from graph G and a list of nodes
    from graph H to which these may be mapped.
    """

    def __init__(self, G_nodes, H_nodes):
        self.G_nodes = G_nodes
        self.H_nodes = H_nodes


class PartitioningMCISFinder(object):
    """A class implementing the McSplit algorithm"""

    def __init__(self, G, H):
        self.G = G
        self.H = H
        self.list_of_mcs = []

    def refine_label_classes(self, label_classes, v, w):
        new_label_classes = []
        for lc in label_classes:
            G_nodes = lc.G_nodes
            H_nodes = lc.H_nodes
            G_adj_row_v = self.G.adj_row(v)
            H_adj_row_w = self.H.adj_row(w)
            new_lc_0_G_nodes = [u for u in G_nodes if not G_adj_row_v[u]]
            new_lc_0_H_nodes = [u for u in H_nodes if not H_adj_row_w[u]]
            if new_lc_0_G_nodes and new_lc_0_H_nodes:
                new_label_classes.append(LabelClass(
                    new_lc_0_G_nodes,
                    new_lc_0_H_nodes
                ))
            if len(new_lc_0_G_nodes) < len(G_nodes) and len(new_lc_0_H_nodes) < len(H_nodes):
                new_label_classes.append(LabelClass(
                    [u for u in G_nodes if G_adj_row_v[u]],
                    [u for u in H_nodes if H_adj_row_w[u]]
                ))
        return new_label_classes

    def select_label_class(self, label_classes, assignment_count):
        if not label_classes:
            return None
        return min(label_classes, key=lambda lc: max(len(lc.G_nodes), len(lc.H_nodes)))

    def calculate_bound(self, label_classes):
        return sum(min(len(lc.G_nodes), len(lc.H_nodes)) for lc in label_classes)

    def search(self, label_classes, assignments, target):
        tmp_counter[0] += 1
        if len(assignments) == target:
            self.list_of_mcs.append(dict(assignments))
            return
        if len(assignments) + self.calculate_bound(label_classes) < target:
            return
        label_class = self.select_label_class(label_classes, len(assignments))
        if label_class is None:
            return
        v = label_class.G_nodes.pop()
        H_nodes = label_class.H_nodes[:]
        for w in H_nodes:
            label_class.H_nodes[:] = [u for u in H_nodes if u != w]
            assignments[v] = w
            new_label_classes = self.refine_label_classes(label_classes, v, w)
            self.search(new_label_classes, assignments, target)
            del assignments[v]
        label_class.H_nodes[:] = H_nodes
        new_label_classes = [lc for lc in label_classes if lc.G_nodes]
        self.search(new_label_classes, assignments, target)

    def find_common_subgraph(self, target):
        """Find a common subgraph with at least `target` nodes using McSplit"""
        self.search([LabelClass(sorted(self.G.nodes()), sorted(self.H.nodes()))], {}, target)
        if self.list_of_mcs:
            return [set(mcs.items()) for mcs in self.list_of_mcs]
        else:
            return None


def induced_subgraph_isomorphism(G, H):
    """
    Find a maximum common induced subgraph
    """
    target = G.number_of_nodes()
    return PartitioningMCISFinder(G, H).find_common_subgraph(target) is not None



# The following function is more-or-less copied from NetworkX
def from_graph6_bytes(bytes_in):
    def bits():
        """Returns sequence of individual bits from 6-bit-per-value
        list of data values."""
        for d in data:
            for i in [5, 4, 3, 2, 1, 0]:
                yield (d >> i) & 1

    def data_to_n(data):
        """Read initial one-, four- or eight-unit value from graph6
        integer sequence.
        Return (value, rest of seq.)"""
        if data[0] <= 62:
            return data[0], data[1:]
        if data[1] <= 62:
            return (data[1] << 12) + (data[2] << 6) + data[3], data[4:]
        return (
            (data[2] << 30)
            + (data[3] << 24)
            + (data[4] << 18)
            + (data[5] << 12)
            + (data[6] << 6)
            + data[7],
            data[8:],
        )

    if bytes_in.startswith(b">>graph6<<"):
        bytes_in = bytes_in[10:]

    data = [c - 63 for c in bytes_in]
    if any(c > 63 for c in data):
        raise ValueError("each input character must be in range(63, 127)")

    n, data = data_to_n(data)
    nd = (n * (n - 1) // 2 + 5) // 6
    if len(data) != nd:
        raise NetworkXError(
            f"Expected {n * (n - 1) // 2} bits but got {len(data) * 6} in graph6"
        )

    G = Graph(n)
    for (i, j), b in zip([(i, j) for j in range(1, n) for i in range(j)], bits()):
        if b:
            G.add_edge(i, j)

    return G


def read_all_graphs(n):
    with open("mckay-data/graph{}.g6".format(n), "rb") as f:
        for line in f:
            yield from_graph6_bytes(line.strip())

    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 {} NP NT".format(sys.argv[0]))
        exit(1)

    nP = int(sys.argv[1])
    nT = int(sys.argv[2])

    patterns = {}
    for i in range(1, 7):
        all_graphs = [G for G in read_all_graphs(i)]
        if not isinstance(all_graphs, list):
            all_graphs = [all_graphs]
        patterns[i] = all_graphs
        patterns[i].sort(key=lambda G: -abs(sum(sum(row) for row in G._adj_mat) - G.number_of_nodes() * (G.number_of_nodes() - 1) / 2))
#            break

    print(sum(all(induced_subgraph_isomorphism(P, T) for P in patterns[nP]) for T in read_all_graphs(nT)))
