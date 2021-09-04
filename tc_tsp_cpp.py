#    Copyright (C) 2021 Kiyoshi Irie
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are
#    met:
#
#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#
#      * Neither the name of the NetworkX Developers nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import networkx as nx
import matplotlib.pyplot as plt
import networkx.algorithms.approximation.traveling_salesman as tsp


def load_graph(filename):
    graph = nx.Graph()
    with open(filename) as f:
        num_vertices = int(f.readline())
        graph.add_nodes_from(range(num_vertices))
        num_edges = int(f.readline())
        for i in range(num_edges):
            items = f.readline().split(' ')
            graph.add_edge(int(items[0]), int(items[1]), weight=float(items[2]))
            #print(f'{items[0]} {items[1]} weight={float(items[2])}')
        # nx.draw_networkx(G)
        # plt.show()
    return graph


def make_perfect_shortest_path_graph(graph):
    num_vertices = graph.number_of_nodes()
    all_pairs = dict(nx.all_pairs_dijkstra_path_length(graph))
    gcompl = nx.complete_graph(num_vertices)

    for i in range(num_vertices):
        for j in range(i+1, num_vertices):
            gcompl[i][j]['weight'] = all_pairs[i][j]

    return gcompl, nx.all_pairs_dijkstra_path(graph)


def solve_tsp(graph):
    print('--- traveling salesperson problem ---')
    gcompl, _ = make_perfect_shortest_path_graph(graph)
    cycle = tsp.simulated_annealing_tsp(gcompl, tsp.greedy_tsp(gcompl))
    cycle = tsp.threshold_accepting_tsp(gcompl, cycle)
    print(f'approx. TSP solution: {cycle}')
    cost = sum(gcompl[n][nbr]["weight"] for n, nbr in nx.utils.pairwise(cycle))
    print(f'total cost: {cost}')


def solve_cpp(g):
    print('\n--- postman problem ---')
    g2, shortest_paths = make_perfect_shortest_path_graph(g)
    shortest_paths = dict(shortest_paths)

    # make graph of odd degree nodes
    odd_vertices = []
    for n in g:
        if g.degree(n) % 2 == 1:
            odd_vertices.append(n)
        else:
            g2.remove_node(n)
    print(f'odd degree nodes: {odd_vertices}')

    # use negative weight to apply max_weight_matching
    for i, j, d in g2.edges(data=True):
        d['weight'] *= -1
    matching = nx.max_weight_matching(g2, maxcardinality=True)
    assert(nx.is_perfect_matching(g2, matching))
    print(f'min weight matching of odd nodes: {matching}')

    # make eulerian graph
    multig = nx.MultiGraph(g)
    total_weight = g.size(weight="weight")
    print(f'original graph weight = {total_weight}')
    for pair in matching:
        a, b = pair
        total_weight -= g2[a][b]['weight']
        path = shortest_paths[a][b]
        for k in range(len(path)-1):
            i = path[k]
            j = path[k+1]
            multig.add_edge(i, j, weight=g[i][j]['weight'])
        print(f'append edges = {path}')

    print(f'total expanded weight = {total_weight}')

    weight = 0
    circuit = nx.eulerian_circuit(multig)
    for a, b in circuit:
        weight += g[a][b]['weight']
    nodes_list = [u for u,v in nx.eulerian_circuit(multig)]
    print(f'CPP solution {nodes_list}')
    print(f'circuit weight = {weight}')


if __name__ == '__main__':
    g = load_graph(sys.argv[1])
    solve_tsp(g)
    solve_cpp(g)
