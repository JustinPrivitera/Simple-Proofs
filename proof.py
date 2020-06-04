#!/usr/bin/python3

# split this into a few files

import copy

UNKNOWN_PARITY = -1
EVEN = -2
ODD = -3
UNKNOWN_VALUE = -4

def const_to_string(const):
	if const == UNKNOWN_PARITY:
		return "UNKNOWN_PARITY"
	if const == UNKNOWN_VALUE:
		return "UNKNOWN_VALUE"
	if const == EVEN:
		return "EVEN"
	if const == ODD:
		return "ODD"
	else:
		return "ERROR"

class Natural:
	def __init__(self, name, parity, value):
		self.name = name
		self.parity = parity
		self.value = value

	def equals(self, natural, neighbors, nat_neighbors):
		if self.parity == natural.parity:
			if type(self.value) != type(natural.value):
				return False
			elif type(self.value) == int:
				return self.value == natural.value
			# if type(self.value) == str:
			# 	if self.value == natural.value:
			# 		return True
			# 	return False
			else:
				return self.value.equals(natural.value, neighbors, nat_neighbors)
		return False

	def to_string(self):
		retstr = self.name + " = [" + const_to_string(self.parity) + ", "
		if type(self.value) == int:
			if self.value == UNKNOWN_VALUE:
				retstr += const_to_string(self.value)
			else:
				retstr += str(self.value)
		elif type(self.value) == str:
			retstr += self.value
		elif type(self.value == Binop):
			retstr += self.value.to_string()
		else:
			retstr += "error"
		retstr += "]"
		return retstr

class Binop:
	def __init__(self, op, l, r):
		self.op = op
		self.l = l
		self.r = r

	def equals(self, binop, neighbors, nat_neighbors):
		if self.op == binop.op:
			return operand_equals(self.l, binop.l, neighbors, nat_neighbors) and operand_equals(self.r, binop.r, neighbors, nat_neighbors)
		return False

	def to_string(self):
		retstr = "(" + self.op + " "
		if type(self.l) == int:
			retstr += str(self.l)
		elif type(self.l) == str:
			retstr += self.l
		elif type(self.l == Binop):
			retstr += self.l.to_string()
		else:
			retstr += "error"
		retstr += " "
		if type(self.r) == int:
			retstr += str(self.r)
		elif type(self.r) == str:
			retstr += self.r
		elif type(self.r == Binop):
			retstr += self.r.to_string()
		else:
			retstr += "error"
		retstr += ")"
		return retstr

def lookup(name, numbers):
	for i in range(0, len(numbers)):
		if numbers[i].name == name:
			return numbers[i]
	print("error lookup failed")
	return numbers[0]

def operand_equals(op1, op2, op1_neighbors, op2_neighbors):
	if type(op1) != type(op2):
		return False
	if type(op1) == int:	
		return op1 == op2
	if type(op1) == str: # variable names
		return lookup(op1, op1_neighbors).equals(lookup(op2, op2_neighbors), op1_neighbors, op2_neighbors)
	return op1.equals(op2) # this covers both the natural and binop cases

class Node:
	def __init__(self, numbers, nodes):
		self.numbers = numbers # these are all naturals
		self.nodes = nodes
		self.discovered = False

	def equals(self, node): # in order to be equal, two nodes need not share all the same connections
		if len(self.numbers) != len(node.numbers):
			return False
		for i in range(0, len(self.numbers)):
			if not self.numbers[i].equals(node.numbers[i], self.numbers, node.numbers):
				return False
		return True
		# this doesn't work I think because nodes could be the same but ordered differently

	def to_string(self):
		# retstr = "node\n"
		retstr = "\n"
		for i in range(0, len(self.numbers)):
			retstr += "\t" + self.numbers[i].to_string() + "\n"
		for i in range(0, len(self.nodes)):
			retstr += self.nodes[i].to_string()
		return retstr

	def get_var_names(self):
		names = []
		for i in range(0, len(self.numbers)):
			names.append(self.numbers[i].name)
		return names

def node_redundancy(nodes, node):
	# make sure that new nodes generated are not equivalent to existing nodes
	i = 0
	while i < len(nodes):
		for j in range(0, len(node.nodes)):
			if nodes[i].equals(node.nodes[j]):
				nodes.pop(i)
				i -= 1
			else: # comment this out???
				node.nodes.append(nodes[i])
		i += 1
	return nodes

def get_var_name(node):
	num = ord('a')
	names = node.get_var_names()
	while chr(num) in names:
		num += 1
	return chr(num)

# if parity of x is even --> x = 2k for some k
def even_forward(node):
	nodes = []
	# must go through numbers and apply axiom if applicable and add to nodes list to be returned
	for i in range(0, len(node.numbers)):
		if node.numbers[i].parity == EVEN:
			if node.numbers[i].value == UNKNOWN_VALUE:
				new_node = copy.deepcopy(node)
				var_name = get_var_name(node)
				k = Natural(var_name, UNKNOWN_PARITY, UNKNOWN_VALUE)
				new_node.numbers.append(k)
				new_node.numbers[i].value = Binop('*', 2, var_name)
				nodes.append(new_node)
			# else: I am going to regret not having an else
	return node_redundancy(nodes, node)

# if x = 2k for some k --> parity of x is even
def even_reverse(node):
	nodes = []
	# must go through numbers and apply axiom if applicable and add to nodes list to be returned
	for i in range(0, len(node.numbers)):
		target = node.numbers[i].value
		if type(target) == Binop:
			if target.op == '*' and (target.l == 2 or target.r == 2):
				if node.numbers[i].parity == ODD or node.numbers[i].parity == UNKNOWN_PARITY:
					if node.numbers[i].parity == ODD:
						print("parity overwrite error")
					new_node = copy.deepcopy(node)
					new_node.numbers[i].parity = EVEN
					nodes.append(new_node)
	return node_redundancy(nodes, node)

# if a = bc + bd --> a = b(c + d)
# if a = (+ (* b c) (* b d)) --> a = (* b (c + d))
def factor_forward(node):
	pass

def factor_reverse(node):
	pass

# substitution
# new definition

axioms = [even_forward, even_reverse]

def populate_graph(node):
	nodes = []
	for i in range(0, len(axioms)):
		nodes = nodes + axioms[i](node)
	for i in range(0, len(nodes)):
		node.nodes.append(nodes[i])
		populate_graph(nodes[i])
	# print("added " + str(len(nodes)) + " nodes to the graph")
	return node

def DFS(start_v, goal, path):
	path.append(start_v)
	start_v.discovered = True
	if start_v.equals(goal):
		return path
	found = False
	for i in range(0, len(start_v.nodes)):
		if not start_v.nodes[i].discovered:
			found = found or DFS(start_v.nodes[i], goal, path)
	return found

def process_path(path):
	for i in range(0, len(path) - 1):
		path[i].nodes = [path[i + 1]]
	path[len(path) - 1].nodes = []
	return path

def prove(hypothesis, conclusion):
	graph = populate_graph(hypothesis)
	# print(graph.to_string())
	# print(len(graph.nodes))
	path = DFS(graph, conclusion, [])
	if not path:
		print("conclusion not found in graph")
		return
	path = process_path(path)

	print(path[0].to_string())

print("given x even, prove x = 2k for some k")
hypothesis = Node([Natural('x', EVEN, UNKNOWN_VALUE)], [])
conclusion = Node([Natural('x', EVEN, Binop('*', 2, 'a')), Natural('a', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
prove(hypothesis, conclusion)
print("---------------------------------")

print("given x = 2k for some k, prove x even")
hypothesis = Node([Natural('x', UNKNOWN_PARITY, Binop('*', 2, 'k')), Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
conclusion = Node([Natural('x', EVEN, Binop('*', 2, 'k')), Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
prove(hypothesis, conclusion)
print("---------------------------------")
