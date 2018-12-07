"""
5TH VERSION 0.1
"""

class Word:
	def __init__(self, label="", action=lambda: None, immediate=False):
		self.label = label
		self.action = action
		self.defination = []
		self.immediate = immediate

	@property
	def is_immediate(self):
		return self.immediate

	@is_immediate.setter
	def is_immediate(self, truth):
		self.immediate = truth

	def __str__(self):
		return f'Word{{label: {self.label}, defination:{self.defination}}}'
	
	
class ForthMachine:
	def __init__(self):
		self._source = ''
		self.data_stack = []
		self.in_compile_mode = False
		self.words = []
		self.cell_size = 1
		self.dictionary = [
			Word(label='+', action=self.add),
			Word(label='*', action=self.multiply),
			Word(label='/', action=self.divide),
			Word(label='%', action=self.modulus),

			Word(label='=', action=self.equals),
			Word(label='>', action=self.greater_than),

			Word(label='nand', action=self.nand),

			Word(label='.', action=self.out),

			Word(label='compiling', action=self.compiling),
			Word(label='immediate', action=self.immediate),
			Word(label='interpreting', action=self.interpreting),
			Word(label='create', action=self.create),

			Word(label='pick', action=self.pick),
			Word(label='roll', action=self.roll),

			Word(label='quit', action=exit),
			Word(label='drop', action=self.data_stack.pop),
			Word(label='var', action=self.variable),
			Word(label='!', action=self.store),
			Word(label='@', action=self.fetch),
			Word(label='const', action=self.constant),
			Word(label='alloc', action=self.allocate),
			Word(label='here', action=lambda: self.data_stack.push(self.next_address))
		]

		self.heap = [0 for _ in range(128)]
		self.next_address = 0

	def init_stdlib(self):
		self.source = 'create ; compiling interpreting'
		self.interpret()
		self.in_compile_mode = False
		self.source = 'immediate'
		self.interpret()

		self.source = 'create : compiling create compiling ;'
		self.interpret()
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
			': cells ' + str(self.cell_size) + ' * ;',
			': cell 1 cells ;',
			': ? @ . ;',
			': +! dup @ rot + swap ! ;',
		]

		for i in stdlib:
			self.source = i
			self.interpret()

	def cbool(self, a):
		return 1 if a else 0


	def emplace(self, label, action):
		self.dictionary.append(Word(label=label, action=action))

	def append(self, word):
		wrd = self.dictionary.pop()
		wrd.defination.append(word)
		self.dictionary.append(wrd)

	def find(self, label):
		wrd = Word()
		if label:
			for word in self.dictionary:
				if word.label == label:
					wrd = word
					break
			else:
				return None
			return wrd


	@property
	def source(self):
		return self._source

	@source.setter
	def source(self, source):
		self._source = source
		self.words = self._source.split(' ')

	def get_next_word(self):
		if self.words:
			x = self.words.pop(0)
			return x
		return None

	def execute(self, i):
		for word in self.dictionary[i].defination:
			word.action()

	# PRIMARY WORDS
	def add(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(op1 + op2)

	def multiply(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(op1 * op2)

	def divide(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(op1 / op2)

	def modulus(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(op1 % op2)

	def equals(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(self.cbool(op1 == op2))

	def greater_than(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(self.cbool(op1 > op2))

	def nand(self):
		op2 = self.data_stack.pop()
		op1 = self.data_stack.pop()
		self.data_stack.append(self.cbool(not(op1 and op2)))

	def out(self):
		print(self.data_stack.pop())

	def compiling(self):
		self.in_compile_mode = True

	def immediate(self):
		self.dictionary[-1].is_immediate = True

	def interpreting(self):
		self.in_compile_mode = False

	def create(self):
		curr_pos = len(self.dictionary)
		wrd = Word(
			label=self.get_next_word(),
			action=lambda: self.execute(curr_pos)
		)
		self.dictionary.append(wrd)

	def pick(self):
		op = self.data_stack.pop()
		idx = len(self.data_stack) - 1 - op
		self.data_stack.append(self.data_stack[idx])

	def roll(self):
		op = self.data_stack.pop()
		idx = len(self.data_stack) - 1 - op
		self.data_stack.append(self.data_stack.pop(idx))

	def variable(self):
		addr = self.next_address
		wrd = Word(
			label=self.get_next_word(),
			action=lambda: self.data_stack.append(addr)
		)
		self.data_stack.append(addr)
		self.next_address += 1
		self.dictionary.append(wrd)

	def store(self):
		addr = self.data_stack.pop()
		val = self.data_stack.pop()

		self.heap[addr] = val

	def fetch(self):
		addr = self.data_stack.pop()
		self.data_stack.append(self.heap[addr])

	def fetch_into_out(self):
		addr = self.data_stack.pop()
		print(self.heap[addr])

	def plus_store(self):
		addr = self.data_stack.pop()
		val = self.data_stack.pop()

		self.heap[addr] += val

	def constant(self):
		val = self.data_stack.pop()
		wrd = Word(
			label=self.get_next_word(),
			action=lambda: self.data_stack.append(val)
		)
		self.dictionary.append(wrd)

	def allocate(self):
		size = self.data_stack.pop()
		addr = self.data_stack.pop()
		self.next_address += size

	def interpret(self):
		while True:
			word = self.get_next_word()
			if not word:
				break
			result = self.find(word)
			if result:
				if not self.in_compile_mode or result.is_immediate:
					result.action()
				else:
					self.append(result)
			else:
				try:
					val = int(word)
					if not self.in_compile_mode:
						self.data_stack.append(val)
					else:
						self.append(Word(action=lambda: self.data_stack.append(val)))
				except:
					print('ERROR: ', word, self.source)

	def show_stack(self):
		if len(self.data_stack) <= 5:
			print('=>', *self.data_stack)
			print('->', *self.heap[:16])
		else:
			print('=> ..', *self.data_stack[-5:])

m = ForthMachine()
m.init_stdlib()

while True:
	m.source = input('forth> ')
	m.compile()
	if len(m.data_stack) > 5:
		print('=> ...', *m.data_stack[:-5])
	else:
		print(m.data_stack)