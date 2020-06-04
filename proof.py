#!/usr/bin/python3

# split this into a few files
# write a hypothesis and conclusion parser

import copy

UNKNOWN_PARITY = -1
EVEN = -2
ODD = -3
UNKNOWN_VALUE = -4
LEFT = -5
RIGHT = -6
END = -7
FAILURE = -8

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
	return FAILURE

def operand_equals(op1, op2, op1_neighbors, op2_neighbors):
	if type(op1) != type(op2):
		return False
	if type(op1) == int:	
		return op1 == op2
	if type(op1) == str: # variable names
		return lookup(op1, op1_neighbors).equals(lookup(op2, op2_neighbors), op1_neighbors, op2_neighbors)
	return op1.equals(op2, op1_neighbors, op2_neighbors) # this covers both the natural and binop cases

class Node:
	def __init__(self, numbers, nodes, dist = 1):
		self.numbers = numbers # these are all naturals
		self.nodes = nodes
		self.discovered = False
		self.dist = dist

	def equals(self, node): # in order to be equal, two nodes need not share all the same connections
		if len(self.numbers) != len(node.numbers):
			return False
		for i in range(0, len(self.numbers)):
			if not self.numbers[i].equals(node.numbers[i], self.numbers, node.numbers):
				return False
		return True
		# this doesn't work I think because nodes could be the same but ordered differently

	def to_string(self, prev = None):
		# retstr = "node\n"
		retstr = "Step " + str(self.dist) + "\n"
		for i in range(0, len(self.numbers)):
			retstr += "\t" + self.numbers[i].to_string() + "\n"
		for i in range(0, len(self.nodes)):
			if prev != None:
				if not prev.equals(self.nodes[i]):
					retstr += self.nodes[i].to_string(self)
			else:
				retstr += self.nodes[i].to_string(self)
		return retstr

	def single_to_string(self):
		retstr = "node\n"
		for i in range(0, len(self.numbers)):
			retstr += "\t" + self.numbers[i].to_string() + "\n"
		return retstr

	def get_var_names(self):
		names = []
		for i in range(0, len(self.numbers)):
			names.append(self.numbers[i].name)
		return names

def node_redundancy(nodes, node):
	# make sure that new nodes generated are not equivalent to existing nodes
	i = 0
	length = len(nodes)
	while i < length:
		for j in range(0, len(node.nodes)):
			if nodes[i].equals(node.nodes[j]):
				nodes.pop(i)
				i -= 1
				length -= 1
				break
			# else: # comment this out??? - ya
			# 	node.nodes.append(nodes[i])
		if nodes[i].equals(node):
			nodes.pop(i)
			i -= 1
			length -= 1
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
				new_node.nodes = [] # [node]
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
					new_node.nodes = [] # [node]
					new_node.numbers[i].parity = EVEN
					nodes.append(new_node)
	return node_redundancy(nodes, node)

def new_factored_node(node, factor, left, right, i):
	new_node = copy.deepcopy(node)
	new_node.nodes = [] # [node]
	new_node.numbers[i].value = Binop('*', factor, Binop('+', left, right))
	return new_node

def try_factorization_combos(binop1, binop2, node, i):
	# coerce them to be able to call equals by encasing them in naturals
	# left and left
	if Natural('x', UNKNOWN_PARITY, binop1.l).equals(Natural('x', UNKNOWN_PARITY, binop2.l), node.numbers, node.numbers):
		return new_factored_node(node, binop1.l, binop1.r, binop2.r, i)
	# left and right
	elif Natural('x', UNKNOWN_PARITY, binop1.l).equals(Natural('x', UNKNOWN_PARITY, binop2.r), node.numbers, node.numbers):
		return new_factored_node(node, binop1.l, binop1.r, binop2.l, i)
	# right and left
	elif Natural('x', UNKNOWN_PARITY, binop1.r).equals(Natural('x', UNKNOWN_PARITY, binop2.l), node.numbers, node.numbers):
		return new_factored_node(node, binop1.r, binop1.l, binop2.r, i)
	# right and right
	elif Natural('x', UNKNOWN_PARITY, binop1.r).equals(Natural('x', UNKNOWN_PARITY, binop2.r), node.numbers, node.numbers):
		return new_factored_node(node, binop1.r, binop1.l, binop2.l, i)
	else:
		return "FAILURE"

# if a = bc + bd --> a = b(c + d)
# if a = (+ (* b c) (* b d)) --> a = (* b (+ c d))
# currently this is only called on top level binops, which could lead to many problems later
# if I make a redefinition axiom then this problem ^^^ is fixed
def factor_forward(node):
	nodes = []
	# must go through numbers and apply axiom if applicable and add to nodes list to be returned
	for i in range(0, len(node.numbers)):
		target = node.numbers[i].value
		if type(target) == Binop:
			if target.op == '+':
				if type(target.l) == Binop and type(target.r) == Binop:
					l_target = target.l
					r_target = target.r
					if l_target.op == '*' and r_target.op == '*':
						result = try_factorization_combos(l_target, r_target, node, i)
						if result != "FAILURE":
							nodes.append(result)
	return node_redundancy(nodes, node)

def factor_reverse(node):
	pass

def find_var_in_binop(binop, path, node):
	if type(binop.l) == str:
		if lookup(binop.l, node.numbers).value != UNKNOWN_VALUE:
			path.append(LEFT)
			path.append(END)
			return path
	elif type(binop.l) == Binop:
		path.append(LEFT)
		new_path = find_var_in_binop(binop.l, path, node)
		if len(new_path) != 0:
			if new_path[len(new_path) - 1] == END:
				return new_path
		path.pop()
	if type(binop.r) == str:
		if lookup(binop.r, node.numbers).value != UNKNOWN_VALUE:
			path.append(RIGHT)
			path.append(END)
			return path
	elif type(binop.r) == Binop:
		path.append(RIGHT)
		new_path = find_var_in_binop(binop.r, path, node)
		if len(new_path) != 0:
			if new_path[len(new_path) - 1] == END:
				return new_path
		path.pop()
	return []

def subst_using_path(binop, path, node):
	path.pop()
	binop_copy = copy.deepcopy(binop)
	edit_path = "binop_copy"
	target = binop_copy
	for i in range(0, len(path)):
		if path[i] == LEFT:
			edit_path += ".l"
			target = target.l
		elif path[i] == RIGHT:
			edit_path += ".r"
			target = target.r
	exec("%s = %s" % (edit_path, "lookup(target, node.numbers).value"))
	if binop.equals(binop_copy, node.numbers, node.numbers):
		print("substitution error")
	return binop_copy

def substitution(node):
	nodes = []
	# must go through numbers and apply axiom if applicable and add to nodes list to be returned
	for i in range(0, len(node.numbers)):
		target = node.numbers[i].value
		if type(target) == Binop:
			path = find_var_in_binop(target, [], node)
			if len(path) > 0:
				if path[len(path) - 1] == END:
					new_node = copy.deepcopy(node)
					new_node.nodes = [] # [node]
					new_node.numbers[i].value = subst_using_path(target, path, node)
					nodes.append(new_node)
		elif type(target) == str:
			new_node = copy.deepcopy(node)
			new_node.nodes = [] # [node]
			new_node.numbers[i].value = lookup(target, node.numbers).value
			nodes.append(new_node)
	return node_redundancy(nodes, node)

# new definition/reduction of complicated formulas

axioms = [even_forward, even_reverse, factor_forward, substitution]

def populate_graph(node, dist):
	nodes = []
	for i in range(0, len(axioms)):
		nodes = nodes + axioms[i](node)
	for i in range(0, len(nodes)):
		nodes[i].dist = dist + 1
		node.nodes.append(nodes[i])
		populate_graph(nodes[i], dist + 1)
	return node

def DFS(start_v, goal, path):
	path = copy.deepcopy(path)
	path.append(start_v)
	start_v.discovered = True
	if start_v.equals(goal):
		return path
	found = False
	# start_v.nodes.reverse()
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
	graph = populate_graph(hypothesis, 1)

	path = DFS(graph, conclusion, [])
	if not path:
		print("conclusion not found in graph")
		return

	path = process_path(path)

	print(path[0].to_string())

def trivial_proofs():
	print("TRIVIAL PROOFS:")
	print("Proof 1: given x even, prove x = 2k for some k")
	hypothesis = Node([Natural('x', EVEN, UNKNOWN_VALUE)], [])
	conclusion = Node([Natural('x', EVEN, Binop('*', 2, 'a')), Natural('a', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	prove(hypothesis, conclusion)
	print("---------------------------------")

	print("Proof 2: given x = 2k for some k, prove x even")
	hypothesis = Node([Natural('x', UNKNOWN_PARITY, Binop('*', 2, 'k')), Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	conclusion = Node([Natural('x', EVEN, Binop('*', 2, 'k')), Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	prove(hypothesis, conclusion)
	print("---------------------------------")

	print("Proof 3: given x = 2k + 2l for some k and l, prove x = 2(k + l)")
	hypothesis = Node([
		Natural('x', UNKNOWN_PARITY, Binop('+', Binop('*', 2, 'k'), Binop('*', 2, 'l'))), 
		Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE),
		Natural('l', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	conclusion = Node([
		Natural('x', UNKNOWN_PARITY, Binop('*', 2, Binop('+', 'k', 'l'))),
		Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE),
		Natural('l', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	prove(hypothesis, conclusion)
	print("---------------------------------")

	print("Proof 4: given x = 2k for k = 4, prove x = 2 * 4")
	hypothesis = Node([
		Natural('x', UNKNOWN_PARITY, Binop('*', 2, 'k')), 
		Natural('k', UNKNOWN_PARITY, 4)], [])
	conclusion = Node([
		Natural('x', UNKNOWN_PARITY, Binop('*', 2, 4)), 
		Natural('k', UNKNOWN_PARITY, 4)], [])
	prove(hypothesis, conclusion)
	print("---------------------------------")

	# prove transitivity

def non_trivial_proofs():
	print("NONTRIVIAL PROOFS:")
	print("Proof 5: given x = 2k + 2l for some k and l, prove x even")
	hypothesis = Node([
		Natural('x', UNKNOWN_PARITY, Binop('+', Binop('*', 2, 'k'), Binop('*', 2, 'l'))),
		Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE),
		Natural('l', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	conclusion = Node([
		Natural('x', EVEN, Binop('*', 2, Binop('+', 'k', 'l'))),
		Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE),
		Natural('l', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	prove(hypothesis, conclusion)
	print("---------------------------------")
	
	print("Proof 6: given x even, y = even, z = x + y, prove z even")
	hypothesis = Node([
		Natural('x', EVEN, UNKNOWN_VALUE),
		Natural('y', EVEN, UNKNOWN_VALUE),
		Natural('z', UNKNOWN_PARITY, Binop('+', 'x', 'y'))], [])
	conclusion = Node([
		Natural('x', EVEN, Binop('*', 2, 'k')),
		Natural('y', EVEN, Binop('*', 2, 'l')),
		Natural('z', EVEN, Binop('*', 2, Binop('+', 'k', 'l'))),
		Natural('k', UNKNOWN_PARITY, UNKNOWN_VALUE),
		Natural('l', UNKNOWN_PARITY, UNKNOWN_VALUE)], [])
	prove(hypothesis, conclusion)
	print("---------------------------------")

trivial_proofs()
non_trivial_proofs()
