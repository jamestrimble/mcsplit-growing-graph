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

    def __init__(self, G, H, prev_results):
        self.G = G
        self.H = H
        self.prev_results = prev_results
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
        n = self.G.number_of_nodes()
        max_v = n - 1
        for w in range(n):
            vv = [u for u in sorted(self.G.nodes()) if u != max_v]
            ww = [u for u in sorted(self.H.nodes()) if u != w]
            new_label_classes = self.refine_label_classes([LabelClass(vv, ww)], max_v, w)
            self.search(new_label_classes, {max_v : w}, target)
        for v in range(max_v):
            vv = [u for u in sorted(self.G.nodes()) if u != v and u != max_v]
            ww = [u for u in sorted(self.H.nodes()) if u != max_v]
            new_label_classes = self.refine_label_classes([LabelClass(vv, ww)], v, max_v)
            self.search(new_label_classes, {v : max_v}, target)
        if self.list_of_mcs:
            return [set(mcs.items()) for mcs in self.list_of_mcs]
        else:
            return None


def max_common_induced_subgraph(G, H, prev_results):
    """
    Find a maximum common induced subgraph
    """
    prev_best_size = len(prev_results[0])
    target = prev_best_size + 1
    search_result = PartitioningMCISFinder(G, H, prev_results).find_common_subgraph(target)
    if search_result is not None:
        return search_result
    target = prev_best_size
    return prev_results + PartitioningMCISFinder(G, H, prev_results).find_common_subgraph(target)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {} MAX_N".format(sys.argv[0]))
        exit(1)
    max_n = int(sys.argv[1])

    random.seed(1)

    G = Graph()
    H = Graph()
    result = [[]]
    for v in range(max_n):
        G.add_node()
        H.add_node()
        for w in range(v):
            if random.random() < 0.5:
                G.add_edge(v, w)
            if random.random() < 0.5:
                H.add_edge(v, w)
        result = max_common_induced_subgraph(G, H, result)
        G_vtx_counts = [0] * (v + 1)
        H_vtx_counts = [0] * (v + 1)
        G_densities = []
        H_densities = []
        for m in result:
            G_densities.append(G.induced_subgraph([t for t, u in m]).density())
            H_densities.append(H.induced_subgraph([u for t, u in m]).density())
            for t, u in m:
                G_vtx_counts[t] += 1
                H_vtx_counts[u] += 1
        sys.stderr.write("Working on n={}...\n".format(v+1))
        print("SUMMARY {},{},{}".format(v + 1, len(result[0]), len(result)))

        print("A {},{},{},{}".format(v + 1, -1, "G", len(result)))
        print("A {},{},{},{}".format(v + 1, -1, "H", len(result)))
        for u in range(v + 1):
            print("A {},{},{},{}".format(v + 1, u, "G", G_vtx_counts[u]))
            print("A {},{},{},{}".format(v + 1, u, "H", H_vtx_counts[u]))
        for i, m in enumerate(result):
            real_density = G.induced_subgraph([t for t, u in m]).density()
            fake_density = G.induced_subgraph(random.sample(G.nodes(), len(m))).density()
            print("B {},{},{},{}".format(v + 1, i, real_density, "real"))
            print("B {},{},{},{}".format(v + 1, i, fake_density, "fake"))

        print("* {:5} {:5} {:5} {} {} [{}]".format(v + 1, len(result[0]), len(result),
                G_vtx_counts, H_vtx_counts,
                " ".join("{:.2f}".format(d) for d in sorted(G_densities))))

    print(tmp_counter)
