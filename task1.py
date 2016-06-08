#!/usr/bin/env python3


import sys
import re
import operator
import itertools
import functools
import heapq
import copy
import math


class Graph(object):
    def __init__(self, nodes=None, vertex_map=None):
        self.nodes = nodes or dict()
        self.vertex_map = vertex_map or dict()

    def add_vertex(self, node_from, node_to, options):
        self.nodes.setdefault(node_from, dict())
        self.nodes.setdefault(node_to, dict())
        vertex_options = self.vertex_map.setdefault(node_from, dict()).setdefault(node_to, dict())
        for option_key, option_value in options.items():
            vertex_options[option_key] = option_value

    def set_node_distance(self, node, distance):
        self.nodes.setdefault(node, dict())['distance'] = distance

    def get_node_distance(self, node):
        return self.nodes[node].get('distance', math.inf)

    def set_node_previous(self, node, value):
        self.nodes.setdefault(node, dict())['previous'] = value

    def set_node_visited(self, node):
        self.nodes.setdefault(node, dict())['visited'] = True

    def get_nodes_unvisited(self):
        return [(node_options.get('distance', math.inf), node_key) for (node_key, node_options) in self.nodes.items() if not node_options.get('visited', False)]

    @classmethod
    def from_str(cls, str_value):
        re_vertex = re.compile('^(\\w)(\\w)(\\d+)$')
        graph = cls()
        for vertex in [item.strip() for item in str_value.split(',')]:
            re_vertex_match = re_vertex.match(vertex)
            if re_vertex_match is None:
                raise AssertionError('Unexpected input', vertex)
            node_from = re_vertex_match.group(1)
            node_to = re_vertex_match.group(2)
            distance = re_vertex_match.group(3)
            try:
                distance = int(distance)
            except (TypeError, ValueError):
                raise AssertionError('Distance value is not expected')
            graph.add_vertex(node_from, node_to, {'distance': distance})
        return graph

    def distance_immediate(self, node1, node2):
        try:
            return self.vertex_map[node1][node2]['distance']
        except KeyError:
            raise GraphException()

    def distance_nodes(self, nodes):
        if len(nodes) < 2:
            raise GraphException('Path must have at least two nodes')
        return functools.reduce(operator.add, map(lambda node_pair: self.distance_immediate(node_pair[0], node_pair[1]), zip(nodes[:-1], nodes[1:])), 0)

    def backtrack(self, start_node, end_node, match_predicate, terminate_predicate, context=None):
        results = list()
        context = context or dict(path=[], distance=0)
        if match_predicate(context) and start_node == end_node:
            results.append({'path': context['path'], 'distance': context.get('distance')})
        if terminate_predicate(context):
            return results
        adjanced_nodes = self.vertex_map.get(start_node, {}).keys()
        for adjanced_node in adjanced_nodes:
            results += self.backtrack(adjanced_node, end_node, match_predicate, terminate_predicate, {
                'path': context['path'] + [adjanced_node],
                'distance': context['distance'] + self.vertex_map[start_node][adjanced_node]['distance'],
            })
        return results

    def dijkstra(self, node_from):
        graph = type(self)(copy.deepcopy(self.nodes), copy.deepcopy(self.vertex_map))
        # Set the distance for the start node to zero 
        graph.set_node_distance(node_from, 0)

        # Put tuple pair into the priority queue
        unvisited_queue = graph.get_nodes_unvisited()
        heapq.heapify(unvisited_queue)

        while len(unvisited_queue):
            distance, node_current = heapq.heappop(unvisited_queue)
            graph.set_node_visited(node_current)
            del distance

            for node_adj in graph.vertex_map.get(node_current, {}).keys():
                if graph.vertex_map[node_current][node_adj].get('visited', False):
                    continue
                new_dist = graph.get_node_distance(node_current) + graph.vertex_map[node_current][node_adj]['distance']
                if new_dist < graph.get_node_distance(node_adj):
                    graph.set_node_distance(node_adj, new_dist)
                    graph.set_node_previous(node_adj, node_current)

            # Rebuild heap
            # 1. Pop every item
            while len(unvisited_queue):
                heapq.heappop(unvisited_queue)

            # 2. Put all vertices not visited into the queue
            unvisited_queue = graph.get_nodes_unvisited()
            heapq.heapify(unvisited_queue)

        return graph


class GraphException(Exception):
    pass


def main():
    graph = Graph.from_str(sys.stdin.read())
    # Output 1
    sys.stdout.write('Output #1: ')
    try:
        sys.stdout.write('%d\n' % graph.distance_nodes(['A', 'B', 'C']))
    except GraphException:
        sys.stdout.write('NO SUCH ROUTE\n')
    # Output 2
    sys.stdout.write('Output #2: ')
    try:
        sys.stdout.write('%d\n' % graph.distance_nodes(['A', 'D']))
    except GraphException:
        sys.stdout.write('NO SUCH ROUTE\n')
    # Output 3
    sys.stdout.write('Output #3: ')
    try:
        sys.stdout.write('%d\n' % graph.distance_nodes(['A', 'D', 'C']))
    except GraphException:
        sys.stdout.write('NO SUCH ROUTE\n')
    # Output 4
    sys.stdout.write('Output #4: ')
    try:
        sys.stdout.write('%d\n' % graph.distance_nodes(['A', 'E', 'B', 'C', 'D']))
    except GraphException:
        sys.stdout.write('NO SUCH ROUTE\n')
    # Output 5
    sys.stdout.write('Output #5: ')
    try:
        sys.stdout.write('%d\n' % graph.distance_nodes(['A', 'E', 'D']))
    except GraphException:
        sys.stdout.write('NO SUCH ROUTE\n')
    # Output 6
    print('Output #6: %d' % len(graph.backtrack('C', 'C',
                              lambda context: 0 < len(context.get('path', [])) <= 3,
                              lambda context: len(context.get('path', [])) >= 3,
                              )))
    # Output 7
    print('Output #7: %d' % len(graph.backtrack('A', 'C',
                              lambda context: 0 < len(context.get('path', [])) == 4,
                              lambda context: len(context.get('path', [])) >= 4,
                              )))
    # Output 8
    processed_graph = graph.dijkstra('A')
    try:
        distance = processed_graph.get_node_distance('C')
    except KeyError:
        distance = math.inf
    if not math.isinf(distance):
        print('Output #8: %d' % distance)
    else:
        print('Output #8: NO PATH FOUND')
    # Output 9
    def match_predicate(context):
        path = context.get('path', [])
        path_len = len(path)
        return path_len > 0 and len(set(path)) == path_len
    loops = graph.backtrack('B', 'B',
                            match_predicate,
                            lambda context: len(context.get('path', [])) >= 10,
                            )
    del match_predicate
    if loops:
        print('Output #9: %d' % min([loop.get('distance') for loop in loops]))
    else:
        print('Output #9: NO REQESTED LOOP')
    # Output 10
    print('Output #10: %d' % len(graph.backtrack('C', 'C',
                                    lambda context: 0 < context.get('distance', []) < 30,
                                    lambda context: context.get('distance', 0) >= 30,
                              )))

if __name__ == '__main__':
    main()
