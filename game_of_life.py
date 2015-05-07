#!/usr/bin/env python

import sys
import getopt
import random
import math
import time
import signal
import traceback


"""
RULES:

1. Any live cell with fewer than two live neighbours dies, as if by needs caused by underpopulation.
2. Any live cell with more than three live neighbours dies, as if by overcrowding.
3. Any live cell with two or three live neighbours lives, unchanged, to the next generation.
4. Any dead cell with exactly three live neighbours cells will come to life.

IMPLEMENTATION:

1. Array of 1024 cells (32^2), 32x32 grid

2. Initialize array with a pass of 'rand()' or GOD's WORDS

3. Sweep the array to apply the rules, saving the live/die results in a parallel array.

4. Re-write the main array based on the results

5. Display the grid

6. sleep 1 second

Repeat 3-6

"""

def usage():
	sys.stderr.write("usage: {0} [-n iterations] [-s size of grid (default 1024)]\n".format(sys.argv[0]))
	sys.exit(1)

def sighandler(signum, frame):
	sys.stderr.write("\nYou ended the Game of Life\n")
	sys.exit()

class GameOfLife():

	grid       = []
	res        = []
	size       = 1024
	dim        = 0
	iterations = 0

	def __init__(self, opts):
		self.size       = opts['size']
		self.iterations = opts['iter']
		self.god        = opts['god']
		self.dim        = int(math.sqrt(self.size))
		self.play()


	def initialize(self):
		if self.god:
			self.initialize_by_gods_word()

		random.seed()
		for i in xrange(self.size):
			self.grid.append(random.random() >= 0.5)


	def initialize_by_gods_word(self):
		with open('./gods_word') as fh:
			words = fh.read()

		# make sure it is long enough
		while len(words) < self.size:
			words += words

		for i in xrange(self.size):
			self.grid.append(bool(ord(words[i]) % 2))


	def count_neighbors(self, idx):
		"""
		Find the 'box' surrounding this node in the grid,
		copy the value from self.grid into neighbors.
		If the index is 'off the edge of the grid', the value is False
		Count the neighbors according to the RULES and return True/False for Lives On or Dies
		"""
		neighbors = []

		# walk the '9' nodes around the current one (what's on the tic-tac-toe here?)

		# nodes "above"
		p = idx - self.dim
		if p < 0:
			neighbors.extend([False, False, False])
		else:
			neighbors.append(False if (p % self.dim) == 0 else self.grid[p - 1])
			neighbors.append(self.grid[p])
			neighbors.append(False if (p + 1) % self.dim == 0 else self.grid[p + 1])

		# one node back
		neighbors.append(False if (idx % self.dim) == 0 else self.grid[idx - 1])

		#node in front
		neighbors.append(False if (idx + 1) % self.dim == 0 else self.grid[idx + 1])

		# nodes "below"
		p = idx + self.dim
		if p >= self.size:
			neighbors.extend([False, False, False])
		else:
			neighbors.append(False if (p % self.dim) == 0 else self.grid[p - 1])
			neighbors.append(self.grid[p])
			neighbors.append(False if (p + 1) % self.dim == 0 else self.grid[p + 1])

		return neighbors



	def assess_neighbors(self, idx):
		c = self.count_neighbors(idx).count(True)

		# apply rules
		if c not in (2, 3): # rules 1, 2 - too few or too many neighbors
			return False

		if self.grid[idx]:
			return c in (2,3) # rule 3 - alive, and 2 or 3 living neighbors
		else:
			return c == 3 # rule 4 - dead and 3 live neighbors


	def sweep(self):
		self.res = []
		for i in xrange(len(self.grid)):
			self.res.append(self.assess_neighbors(i))


	def display(self):
		# u'\u00B7' - dot
		# "\033[0;32m*\033[0m" - green 'star' (or 'splat' if you're cynical)
		tmp = []
		try:
			for i in xrange(self.size):
				tmp.append(u'\u00B7' if not self.grid[i] else "\033[0;32m*\033[0m")
		except Exception as e:
			print i
			raise Exception(e)


		print "\x1b[2J\x1b[H" # clear screen and reset to top (yeah, yeah, ascii terms only)

		print "+" + "-" * (self.dim * 2 - 1) + "+"
		for i in xrange(0, self.size, self.dim):
			print "|" + "|".join(tmp[i:i + self.dim]) + "|"
		print "+" + "-" * (self.dim * 2 - 1) + "+"


	def play(self):
		self.initialize()
		generations = 0
		while True:
			self.display()
			time.sleep(1)
			generations += 1

			if self.iterations and generations > self.iterations:
				print "The Game of Life is Over\n"
				sys.exit()

			self.sweep()
			self.grid = self.res[:]



if __name__ == '__main__':

	signal.signal(signal.SIGINT, sighandler)

	opts = {'size': 1024, 'iter': None, 'god': False}

	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'hgs:n:', [])
		for o, a in optlist:
			if o == '-s':
				opts['size'] = int(a)
			if o == '-n':
				opts['iter'] = int(a)
			if o == '-g':
				opts['god'] = 1
			if o == '-h':
				print "Conway's Game of Life"
				usage()

        except Exception as e:
                sys.stderr.write("{0}\n".format(e))
                usage()

	# sanity check for a square-shaped grid
	x = math.sqrt(opts['size'])
	if x != int(x):
		m = "specified size {0} does not have an integer square root. Please choose again\n".format(opts['size'])
		sys.stderr.write(m)

	GameOfLife(opts)


