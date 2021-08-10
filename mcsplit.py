import random
import sys


class Graph(object):
    __slots__ = ["_node_count", "_adj_mat"]
    def __init__(self):
        self._node_count = 0
        self._adj_mat = [[0 for _ in range(100)] for _ in range(100)]

    def add_node(self):
        self._node_count += 1

    def add_edge(self, v, w):
        self._adj_mat[v][w] = True
        self._adj_mat[w][v] = True

    def nodes(self):
        return list(range(self._node_count))

    def number_of_nodes(self):
        return self._node_count

    def adj_row(self, v):
        return self._adj_mat[v]
#    def has_edge(self, v, w):
#        return self._adj_mat[v][w]


class LabelClass(object):
    """A label class, used by the McSplit algorithm.

    A label class contains a list of nodes from graph G and a list of nodes
    from graph H to which these may be mapped.  The `is_adjacent` member is
    a boolean which is true if and only if the nodes in the label class are
    adjacent to at least one node of the current subgraph.
    """

    __slots__ = ["G_nodes", "H_nodes", "is_adjacent"]

    def __init__(self, is_adjacent, G_nodes, H_nodes):
        self.G_nodes = G_nodes
        self.H_nodes = H_nodes
        self.is_adjacent = is_adjacent


class PartitioningMCISFinder(object):
    """A class implementing the McSplit algorithm"""

    def __init__(self, G, H, connected):
        self.G = G
        self.H = H
        self.connected = connected
        self.list_of_mcs = []

    def refine_label_classes(self, label_classes, v, w):
        new_label_classes = []
        for lc in label_classes:
            G_adj_row_v = G.adj_row(v)
            H_adj_row_w = H.adj_row(w)
            new_lc_0 = LabelClass(
                lc.is_adjacent,
                [u for u in lc.G_nodes if not G_adj_row_v[u]],
                [u for u in lc.H_nodes if not H_adj_row_w[u]]
            )
            new_lc_1 = LabelClass(
                True,
                [u for u in lc.G_nodes if G_adj_row_v[u]],
                [u for u in lc.H_nodes if H_adj_row_w[u]]
            )
            for new_lc in [new_lc_0, new_lc_1]:
                if new_lc.G_nodes and new_lc.H_nodes:
                    new_label_classes.append(new_lc)
        return new_label_classes

    def select_label_class(self, label_classes, assignment_count):
        if self.connected and assignment_count > 0:
            candidates = [lc for lc in label_classes if lc.is_adjacent]
        else:
            candidates = label_classes
        if not candidates:
            return None
        return min(candidates, key=lambda lc: max(len(lc.G_nodes), len(lc.H_nodes)))

    def calculate_bound(self, label_classes):
        return sum(min(len(lc.G_nodes), len(lc.H_nodes)) for lc in label_classes)

    def search(self, label_classes, assignments, target):
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
        label_class = LabelClass(False, sorted(self.G.nodes()), sorted(self.H.nodes()))
        self.search([label_class], {}, target)
        if self.list_of_mcs:
            return [set(mcs.items()) for mcs in self.list_of_mcs]
        else:
            return None


def common_induced_subgraph(G, H, target, connected=False):
    """
    Find a common induced subgraph with at least a given number of nodes


    This is the decision version of the :func:`max_common_induced_subgraph`
    function.
    """
    return PartitioningMCISFinder(G, H, connected).find_common_subgraph(target)


def max_common_induced_subgraph(G, H, connected=False):
    """
    Find a maximum common induced subgraph
    """
    min_n = min(G.number_of_nodes(), H.number_of_nodes())
    for target in range(min_n, -1, -1):
        search_result = common_induced_subgraph(G, H, target, connected)
        if search_result is not None:
            return search_result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {} MAX_N".format(sys.argv[0]))
        exit(1)
    max_n = int(sys.argv[1])

    G = Graph()
    H = Graph()
    for v in range(max_n):
        G.add_node()
        H.add_node()
        for w in range(v - 1):
            if random.random() < 0.5:
                G.add_edge(v, w)
            if random.random() < 0.5:
                H.add_edge(v, w)
        result = max_common_induced_subgraph(G, H)
        print("{} {} {}".format(v + 1, len(result[0]), len(result)))
#G = Graph()
#H = Graph()
#G.add_node(1)
#G.add_node(2)
#G.add_node(3)
#H.add_node(1)
#H.add_node(2)
#H.add_node(3)
#G.add_edge(1,2)
#G.add_edge(1,3)
#G.add_edge(2,3)
#print(max_common_induced_subgraph(G, H))
