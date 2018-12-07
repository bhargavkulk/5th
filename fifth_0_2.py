"""
FIFTH VERSION 0.2
"""

from pprint import pprint

class Word:
	def __init__(self, name="", action=lambda: None, definition=None, immediate=False):
		self.name = name
		self.action = action
		self.definition = definition
		self.is_immediate = immediate

	def __str__(self):
		return f'Word{{name: {self.name}, definition:{self.definition}}}'

class ForthMachine:
	def __init__(self):
		# for lexer
		self._source = ''
		self.words = []

		# all numbers on interpreting mode go here
		self.data_stack = []

		# for special stuff
		self.return_stack = []

		# currently for saving addresses to words
		# primitive words
		def cbool():
			return 1 if True else 0

		def add():
			op2 = self.pop()
			op1 = self.pop()
			self.push(op1 + op2)

		def multiply():
			op2 = self.data_stack.pop()
			op1 = self.data_stack.pop()
			self.data_stack.append(op1 * op2)

		def divide():
			op2 = self.data_stack.pop()
			op1 = self.data_stack.pop()
			self.data_stack.append(op1 / op2)

		def modulus():
			op2 = self.data_stack.pop()
			op1 = self.data_stack.pop()
			self.data_stack.append(op1 % op2)

		def equals():
			op2 = self.data_stack.pop()
			op1 = self.data_stack.pop()
			self.data_stack.append(cbool(op1 == op2))

		def greater_than():
			op2 = self.data_stack.pop()
			op1 = self.data_stack.pop()
			self.data_stack.append(cbool(op1 > op2))

		def nand():
			op2 = self.data_stack.pop()
			op1 = self.data_stack.pop()
			self.data_stack.append(cbool(not(op1 and op2)))

		def literal():
			self.push(self.heap[self.ptr])
			self.ptr += 1

		def create():
			curr_pos = len(self.dictionary)
			name = self.get_next_word()
			self.emplace(name, lambda: self.execute(curr_pos))

		def interpreting():
			self.compiling = False

		def compiling():
			self.compiling = True

		def immediate():
			self.dictionary[-1].is_immediate = True

		def pick():
			op = self.data_stack.pop()
			idx = len(self.data_stack) - 1 - op
			self.data_stack.append(self.data_stack[idx])

		def roll():
			op = self.data_stack.pop()
			idx = len(self.data_stack) - 1 - op
			self.data_stack.append(self.data_stack.pop(idx))

		self.dictionary = [
			Word(name='+', action=add),
			Word(name='*', action=multiply),
			Word(name='/', action=divide),
			Word(name='%', action=modulus),
			Word(name='nand', action=nand),
			Word(name='=', action=equals),
			Word(name='>', action=greater_than),
			Word(name='pick', action=pick),
			Word(name='roll', action=roll),
			Word(name='.', action=lambda: print(self.pop())),
			Word(action=literal),
			Word(name='interpreting', action=interpreting),
			Word(name='compiling', action=compiling),
			Word(name='exit', action=lambda: self.append(-1)),
			Word(name='create', action=create),
			Word(name='immediate', action=immediate),
			Word(name='drop', action=self.pop),
			Word(name='quit', action=exit)
		]

		# all mem saved here
		self.heap = [0 for _ in range(2000)]
		self.next_address = 0

		# states
		self.compiling = False

		# used in the interpreter
		self.ptr = 0

	def init(self):
		self.source = 'create ; compiling exit interpreting'
		self.compile()
		self.compiling = False
		self.source = 'exit immediate'
		self.compile()

		self.source = 'create : compiling create compiling ;'
		self.compile()

		stdlib = [
			': dup 0 pick ;',
			': over 1 pick ;',
			': swap 1 roll ;',
			': rot 2 roll ;',
			': -rot rot rot ;',
			': 2drop drop drop ;',
			': 2dup over over ;',
			': 2over 3 pick 3 pick ;',
			': 3dup dup 2over rot ;',
			': not dup nand ;',
			': and nand not ;',
			': or not swap not nand ;',
			': nor or not ;',
			': xor 2dup and -rot nor nor ;',
			': xnor xor not ;',
			': <> = not ;',
			': < 2dup > -rot = or not ;',
			': <= > not ;',
			': >= 2dup > -rot = or ;',
			': 0> 0 > ;',
			': 0< 0 < ;',
			': 0= 0 = ;',
			': 0<> 0 <> ;',
			': negate -1 * ;',
			': - negate + ;',
			': square dup * ;',
			': cube dup dup * ;',
			': /% 2dup % -rot / ;',
			': 1+ 1 + ;',
			': 1- 1 - ;',
			': 2+ 2 + ;',
			': 2- 2 - ;',
			': 2* 2 * ;',
			': 2/ 2 / ;',
			': true 1 ;',
			': false 0 ;',
		]

		for definition in stdlib:
			self.source = definition
			self.compile()

	# this is pretty much the lexer
	@property
	def source(self):
		return self._source

	@source.setter
	def source(self, source):
		self._source = source
		self.words = self._source.split(' ')

	def get_next_word(self):
		if self.words:
			return self.words.pop(0)

	# data stack convenience methods
	def push(self, val):
		self.data_stack.append(val)

	def pop(self):
		return self.data_stack.pop()

	# dictionary convenience methods
	def dispatch(self, name):
		for word in self.dictionary:
			if word.name == name:
				return word

	def emplace(self, name, action):
		self.dictionary.append(Word(name=name, action=action, definition=self.next_address))

	# "heap" convenience methods
	def append(self, value):
		self.heap[self.next_address] = value
		self.next_address += 1

	def literal(self, value):
		# magic number alert: (∩｀-´)⊃━☆ﾟ.*･｡ﾟ
		self.append(10)
		self.append(value)

	# "heart" of "machine"
	def compile(self):
		# this function doesn't "compile"
		while True:
			word = self.get_next_word()
			if not word:
				break

			result = self.dispatch(word)
			if result:
				if not self.compiling or result.is_immediate:
					result.action()
				else:
					self.append(self.dictionary.index(result))
			else:
				if self.compiling:
					self.literal(int(word))
				else:
					self.push(int(word))

	def execute(self, word):
		temp_ptr = self.ptr
		self.ptr = self.dictionary[word].definition

		while self.heap[self.ptr] != -1:
			wrd = self.dictionary[self.heap[self.ptr]]
			self.ptr += 1
			wrd.action()

		self.ptr = temp_ptr

m = ForthMachine()
m.init_stdlib()

while True:
	m.source = input('forth> ')
	m.compile()
	if len(m.data_stack) > 5:
		print('=> ...', *m.data_stack[:-5])
	else:
		print(m.data_stack)