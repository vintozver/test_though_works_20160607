#!/usr/bin/env python3

import sys
import re
import operator
import functools


class Graph(object):
    def __init__(self, definition=None):
        self.definition = definition or dict()

    @classmethod
    def from_str(cls, str_value):
        re_vertex = re.compile('(\\w)(\\w)(\\d+)')
        graph = dict()
        for vertex in [item.strip() for item in str_value.split(',')]:
            re_vertex_match = re_vertex.match(vertex)
            if re_vertex_match is None:
                raise AssertionError('Unexpected input', vertex)
            vertex_from = re_vertex_match.group(1)
            vertex_to = re_vertex_match.group(2)
            vertex_distance = re_vertex_match.group(3)
            try:
                vertex_distance = int(vertex_distance)
            except (TypeError, ValueError):
                raise AssertionError('Distance value is not expected')
            graph.setdefault(vertex_from, dict()).setdefault(vertex_to, dict())['distance'] = vertex_distance
        return cls(graph)

    def distance_immediate(self, node1, node2):
        try:
            return self.definition[node1][node2]['distance']
        except KeyError:
            raise GraphException()

    def distance_nodes(self, nodes):
        if len(nodes) < 2:
            raise GraphException('Path must have at least two nodes')
        return functools.reduce(operator.add, map(lambda node_pair: self.distance_immediate(node_pair[0], node_pair[1]), zip(nodes[:-1], nodes[1:])), 0)

    def backtrack_by_steps3(self, start_node, end_node, context=None):
        results = list()
        context = context or dict(path=list())
        if len(context.get('path', [])) == 4 and start_node == end_node:
            results.append(context['path'] + [end_node])
        if len(context.get('path', [])) >= 4:
            return results
        adjanced_nodes = self.definition.get(start_node).keys()
        for adjanced_node in adjanced_nodes:
            results += self.backtrack_by_steps3(adjanced_node, end_node, {'path': context.get('path', []) + [start_node]})
        return results

    def backtrack(self, start_node, end_node, match_predicate, terminate_predicate, context=None):
        results = list()
        context = context or dict(path=list(), distance=0)
        if match_predicate(context) and start_node == end_node:
            results.append(context['path'] + [end_node])
        if terminate_predicate(context):
            return results
        adjanced_nodes = self.definition.get(start_node).keys()
        for adjanced_node in adjanced_nodes:
            results += self.backtrack(adjanced_node, end_node, match_predicate, terminate_predicate, {
                'path': context['path'] + [start_node],
                'distance': context['distance'] + self.definition[start_node][adjanced_node]['distance'],
            })
        return results


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
    sys.stdout.write('Output #6: ')
    print(len(graph.backtrack('C', 'C',
                              lambda context: 0 < len(context.get('path', [])) <= 3,
                              lambda context: len(context.get('path', [])) >= 3,
                              )))
    # Output 7
    sys.stdout.write('Output #7: ')
    print(len(graph.backtrack('A', 'C',
                              lambda context: 0 < len(context.get('path', [])) == 4,
                              lambda context: len(context.get('path', [])) >= 4,
                              )))
    # Output 10
    sys.stdout.write('Output #10: ')
    print(len(graph.backtrack('C', 'C',
                                    lambda context: 0 < context.get('distance', []) < 30,
                                    lambda context: context.get('distance', 0) >= 30,
                              )))

if __name__ == '__main__':
    main()


# Test command (sh, bash)
# $ echo "AB5, BC4, CD8, DC8, DE6, AD5, CE2, EB3, AE7" | ./task1.py
