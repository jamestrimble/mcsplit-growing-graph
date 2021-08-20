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
            G_adj_row_v = G.adj_row(v)
            H_adj_row_w = H.adj_row(w)
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


def max_common_induced_subgraph(G, H):
    """
    Find a maximum common induced subgraph
    """
    target = G.number_of_nodes()
    while True:
        search_result = PartitioningMCISFinder(G, H).find_common_subgraph(target)
        if search_result is not None:
            return search_result
        target = target - 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 {} MAX_N SEED".format(sys.argv[0]))
        exit(1)

    max_n = int(sys.argv[1])

    if not sys.argv[2].isnumeric():
        full_G = Graph()
        full_H = Graph()
        with open(sys.argv[2], "r") as f:
            lines = [[int(tok) for tok in line.strip().split()] for line in f.readlines()]
            n = lines[0][0]
            full_G._adj_mat = lines[1:n+1]
            full_H._adj_mat = lines[n+1:]
    else:
        random.seed(int(sys.argv[2]))
        full_G = Graph(max_n)
        full_H = Graph(max_n)
        for v in range(max_n):
            for w in range(v):
                if random.random() < 0.5:
                    full_G.add_edge(v, w)
                if random.random() < 0.5:
                    full_H.add_edge(v, w)
        for v in range(max_n):
            print([int(x) for x in full_G._adj_mat[v]])
        print()
        for v in range(max_n):
            print([int(x) for x in full_H._adj_mat[v]])

    result = [[]]
    for v in range(max_n):
        n = v + 1
        G = full_G.induced_subgraph(list(range(n)))
        H = full_H.induced_subgraph(list(range(n)))
        sys.stderr.write("Working on n={}...\n".format(n))
        result = max_common_induced_subgraph(G, H)
        G_vtx_counts = [0] * n
        H_vtx_counts = [0] * n
        G_densities = []
        H_densities = []
        for m in result:
            G_densities.append(G.induced_subgraph([t for t, u in m]).density())
            H_densities.append(H.induced_subgraph([u for t, u in m]).density())
            for t, u in m:
                G_vtx_counts[t] += 1
                H_vtx_counts[u] += 1
        print("SUMMARY {},{},{}".format(n, len(result[0]), len(result)))

        print("A {},{},{},{}".format(n, -1, "G", len(result)))
        print("A {},{},{},{}".format(n, -1, "H", len(result)))
        for u in range(n):
            print("A {},{},{},{}".format(n, u, "G", G_vtx_counts[u]))
            print("A {},{},{},{}".format(n, u, "H", H_vtx_counts[u]))
        for i, m in enumerate(result):
            real_density = G.induced_subgraph([t for t, u in m]).density()
            fake_density = G.induced_subgraph(random.sample(G.nodes(), len(m))).density()
            print("B {},{},{},{}".format(n, i, real_density, "real"))
            print("B {},{},{},{}".format(n, i, fake_density, "fake"))

        print("* {:5} {:5} {:5} {} {} [{}]".format(n, len(result[0]), len(result),
                G_vtx_counts, H_vtx_counts,
                " ".join("{:.2f}".format(d) for d in sorted(G_densities))))

    print(tmp_counter)
