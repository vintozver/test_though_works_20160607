#!/usr/bin/env python3

# Test command (sh, bash)
# $ cat task3.1.dat | ./task3.py
#
# Basic idea: collect strings, tokenize, check tokens, parse.
# Currency exchange is represented by graph to allow currency exhange through intermediate currencies.
# For example, exhange rates Silver/Credits, Gold/Credits, Iron/Credits are defined, but Silver/Gold, Iron/Silver, Gold/Iron and backwards can be calculated from existing
# If exchange is not avaiable directly and cannot be traversed through intermediate currencies, user will be notified about this condition
#
# It's highly recommended to store currency exchange rates as fractions because floating point formats or decimal formats with fixed point may loose the precision
# As long as we don't perform any irrational operations, storing exchange rates as fractions will guarantee precision calculations.
# Fractions may be converted to decimals on the final stage when displayed to the user.
#
# Financial applications require precision calculations ;)


import sys
import operator
import functools
import fractions
import heapq
import copy
import math


class TokenMap(object):
    def __init__(self):
        self.items = dict()

    def add_digit(self, token, value):
        self.items[token] = {'type': 'roman_digit', 'value': value}

    def add_alias(self, token, value):
        self.items[token] = {'type': 'alias', 'value': value}

    def lookup_token(self, token):
        result = None
        while token in self.items:
            mapping = self.items[token]
            if mapping['type'] == 'roman_digit':
                return mapping['value']
            elif mapping['type'] == 'alias':
                token = mapping['value']
            else:
                pass

    def lookup_tokens(self, tokens):
        for token in tokens:
            digit = self.lookup_token(token)
            if digit is not None:
                yield digit
            else:
                raise ValueError


def roman_to_int(number_str):
    number_str = number_str.upper()
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50, 10, 5, 1]
    places = []
    for i in range(len(number_str)):
        c = number_str[i]
        value = ints[nums.index(c)]
        # If the next place holds a larger number, this value is negative.
        try:
            if ints[nums.index(number_str[i + 1])] > value:
                value *= -1
        except IndexError:
            # there is no next place.
            pass
        places.append(value)
    return functools.reduce(operator.add, places, 0)


class ConverterProcessed(object):
    def set_node_rate(self, node, value):
        self.currencies.setdefault(node, dict())['rate'] = value

    def get_node_rate(self, node):
        return self.currencies[node].get('rate', math.inf)

    def set_node_previous(self, node, value):
        self.currencies.setdefault(node, dict())['previous'] = value

    def set_node_visited(self, node):
        self.currencies.setdefault(node, dict())['visited'] = True

    def get_nodes_unvisited(self):
        return [(node_options.get('rate', math.inf), node_key) for (node_key, node_options) in self.currencies.items() if not node_options.get('visited', False)]

    def __init__(self, currencies, xchg_graph, currency_from):
        self.currencies = copy.deepcopy(currencies)
        self.xchg_graph = copy.deepcopy(xchg_graph)

        # Set the rate to one
        self.set_node_rate(currency_from, 1)

        # Put tuple pair into the priority queue
        unvisited_queue = self.get_nodes_unvisited()
        heapq.heapify(unvisited_queue)

        while len(unvisited_queue):
            distance, node_current = heapq.heappop(unvisited_queue)
            self.set_node_visited(node_current)
            del distance

            for node_adj in self.xchg_graph.get(node_current, {}).keys():
                if self.xchg_graph[node_current][node_adj].get('visited', False):
                    continue
                new_rate = self.get_node_rate(node_current) / self.xchg_graph[node_current][node_adj]['rate']
                if not math.isinf(new_rate) and math.isinf(self.get_node_rate(node_adj)):
                    self.set_node_rate(node_adj, new_rate)
                    self.set_node_previous(node_adj, node_current)

            # Rebuild heap
            # 1. Pop every item
            while len(unvisited_queue):
                heapq.heappop(unvisited_queue)

            # 2. Put all vertices not visited into the queue
            unvisited_queue = self.get_nodes_unvisited()
            heapq.heapify(unvisited_queue)


class Converter(object):
    def __init__(self):
        self.token_map = TokenMap()
        self.currencies = dict()
        self.xchg_graph = dict()

    def add_xchg(self, currency_from, value_from, currency_to, value_to):
        currencies = self.currencies
        currencies.setdefault(currency_from, dict())
        currencies.setdefault(currency_to, dict())
        xchg_graph = self.xchg_graph
        xchg_graph.setdefault(currency_from, dict()).setdefault(currency_to, dict())['rate'] = fractions.Fraction(value_from, value_to)
        xchg_graph.setdefault(currency_to, dict()).setdefault(currency_from, dict())['rate'] = fractions.Fraction(value_to, value_from)

    def get_xchg(self, currency_from, value_from, currency_to):
        xchg_graph = self.xchg_graph
        if currency_to in xchg_graph and currency_from in xchg_graph[currency_to]:
            return float(xchg_graph[currency_to][currency_from]['rate'] * value_from)
        else:
            processor = ConverterProcessed(self.currencies, xchg_graph, currency_from)
            rate = processor.get_node_rate(currency_to)
            if math.isinf(rate):
                raise KeyError
            return value_from * rate

    def process_line(self, line):
        token_map = self.token_map
        xchg_graph = self.xchg_graph

        line = line.strip()
        tokens = list(map(lambda token: token.strip(), line.split(' ')))
        if len(tokens) < 3:
            sys.stderr.write('WARNING: too few tokens, line ignored. Line: %s\n' % line)
            return
        try:
            is_index = tokens.index('is')
        except ValueError:
            sys.stderr.write('WARNING: line has no "is" token, line ignored. Line: %s\n' % line)
            return

        if tokens[0] == 'how':
            # query clause
            if tokens[1] == 'much':
                lvalue = tokens[2:is_index]
                if lvalue:  # extra tokens between "how much" and "is"
                    sys.stderr.write('WARNING: extra tokens between "how much" and "is", line ignored. Line: %s\n' % line)
                    return
                if tokens[-1] != '?':
                    sys.stderr.write('WARNING: no question mark in question, line ignored. Line: %s\n' % line)
                    return
                rvalue = tokens[is_index + 1:-1]  # strip "?"
                try:
                    roman_value = list(token_map.lookup_tokens(rvalue))
                except ValueError:
                    sys.stderr.write('WARNING: currency assignment left clause has unknown alias, line ignored. Line: %s\n' % line)
                    return
                try:
                    numeric_value = roman_to_int(''.join(roman_value))
                except ValueError:
                    sys.stderr.write('WARNING: roman number conversion failed, line ignored. Line: %s\n' % line)
                    return
                # response on "how much" question
                print('%s is %d' % (' '.join(rvalue), numeric_value))
            elif tokens[1] == 'many':
                lvalue = tokens[2:is_index]
                if len(lvalue) != 1:  # extra tokens between "how much" and "is"
                    sys.stderr.write('WARNING: currency name should be exact one token, line ignored. Line: %s\n' % line)
                    return
                currency_to = lvalue[0]
                if tokens[-1] != '?':
                    sys.stderr.write('WARNING: no question mark in question, line ignored. Line: %s\n' % line)
                    return
                rvalue = tokens[is_index + 1:-1]  # strip "?"
                if len(rvalue) < 2:
                    sys.stderr.write('WARNING: right clause must have at least one digit and a currency token, line ignored. Line: %s\n' % line)
                    return
                currency_from = rvalue[-1]
                try:
                    numbers_from = list(token_map.lookup_tokens(rvalue[:-1]))
                except ValueError:
                    sys.stderr.write('WARNING: right clause has wrong roman aliased number, line ignored. Line: %s\n' % line)
                    return
                try:
                    value_from = roman_to_int(''.join(numbers_from))
                except ValueError:
                    sys.stderr.write('WARNING: right clause has wrong roman aliased number, line ignored. Line: %s\n' % line)
                    return
                # response on "how many" question
                try:
                    print('%s is %f %s' % (' '.join(rvalue), self.get_xchg(currency_from, value_from, currency_to), currency_to))
                except KeyError:
                    sys.stderr.write('WARNING: no exchange rates for the specied currency. Line: %s\n' % line)
                    return
            else:
                sys.stderr.write('I have no idea what you are talking about\n')
                return
        else:
            # assignment clause
            lvalue = tokens[:is_index]
            rvalue = tokens[is_index + 1:]
            if not lvalue:
                sys.stderr.write('WARNING: line has wrong assignment, line ignored. Line: %s\n' % line)
                return
            if len(lvalue) == 1:
                # alias assignment
                if len(rvalue) == 1 and (rvalue[0] in ['I', 'V', 'X', 'L', 'C', 'D', 'M']):
                    token_map.add_digit(lvalue[0], rvalue[0])
                elif len(rvalue) == 1:
                    token_map.add_alias(lvalue[0], rvalue[0])
                else:
                    sys.stderr.write('WARNING: mapping of alias to two tokens is not yet supported, line ignored. Line: %s\n' % line)
                    return
            else:
                # currency exchange assignment
                if len(rvalue) != 2:
                    sys.stderr.write('WARNING: currency assignment right clause must have value and currency, line ignored. Line: %s\n' % line)
                    return
                try:
                    numbers_from = list(token_map.lookup_tokens(lvalue[:-1]))
                except ValueError:
                    sys.stderr.write('WARNING: currency assignment left clause has unknown alias, line ignored. Line: %s\n' % line)
                    return
                try:
                    value_from = roman_to_int(''.join(numbers_from))
                except ValueError:
                    sys.stderr.write('WARNING: currency assignment left clause has wrong roman aliased number, line ignored. Line: %s\n' % line)
                    return
                currency_from = lvalue[-1]
                try:
                    value_to = int(rvalue[0])
                except (TypeError, ValueError):
                    sys.stderr.write('WARNING: currency assignment right clause must have decimal value, line ignored. Line: %s\n' % line)
                    return
                currency_to = rvalue[1]
                # currency exchange graph assignment
                self.add_xchg(currency_from, value_from, currency_to, value_to)


def main():
    converter = Converter()
    for line in sys.stdin.readlines():
        converter.process_line(line)


if __name__ == '__main__':
    main()
