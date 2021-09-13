from collections import OrderedDict
from .grammar import KdlParser
import regex, sys

if sys.version_info.major == 3:
	unicode = str
	unichr = chr

model = KdlParser(whitespace='', parseinfo=False)

namedEscapes = {
	'\\': '\\', 
	'/': '/', 
	'r': '\r', 
	'n': '\n', 
	't': '\t', 
	'"': '"', 
	'b': '\b',
	'f': '\f',
}
namedEscapeInverse = {v : k for k, v in namedEscapes.items()}

exists = lambda ast, name: ast is not None and name in ast and ast[name] is not None

identRe = regex.compile(r'^[^\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$')
def formatIdentifier(ident):
	if identRe.match(ident):
		return ident
	else:
		return formatString(ident)

def formatString(val):
	if '\\' in val and '"' not in val:
		return u'r#"%s"#' % val
	return u'"%s"' % u''.join('\\' + namedEscapeInverse[c] if c in namedEscapeInverse else c for c in val)

def formatValue(val):
	if isinstance(val, Symbol):
		return ':' + formatIdentifier(val.value)
	elif isinstance(val, str) or isinstance(val, unicode):
		return formatString(val)
	elif isinstance(val, bool):
		return 'true' if val else 'false'
	elif val is None:
		return 'null'
	else:
		return str(val)

class Document(list):
	def __init__(self, document=None, preserve_property_order=False, symbols_as_strings=False):
		list.__init__(self)
		if document is not None:
			parse(document, preserve_property_order, symbols_as_strings, dlist=self)

	def __str__(self):
		return u'\n'.join(map(unicode, self))

class Node(object):
	def __init__(self, name, properties, arguments, children):
		self.name = name
		self.properties = properties
		self.arguments = arguments
		self.children = children

	def __str__(self):
		return self.format()

	def format(self, indent=False):
		fmt = formatIdentifier(self.name)
		if self.properties:
			for k, v in self.properties.items():
				fmt += u' %s=%s' % (formatIdentifier(k), formatValue(v))
		if self.arguments:
			for v in self.arguments:
				fmt += ' ' + formatValue(v)
		if self.children:
			fmt += ' {\n'
			for child in self.children:
				fmt += child.format(indent=True) + '\n'
			fmt += '}'
		return u'\n'.join('\t' + line for line in fmt.split('\n')) if indent else fmt

	def __repr__(self):
		return 'Node(name=%r%s%s%s)' % (
			self.name, 
			', properties=%r' % self.properties if self.properties else '', 
			', arguments=%r' % self.arguments if self.arguments else '', 
			', children=%r' % self.children if self.children else '')

	def items(self):
		return self.properties.items() if self.properties else ()

	def __iter__(self):
		if self.properties:
			for prop in self.properties.items():
				yield prop
		if self.arguments:
			for arg in self.arguments:
				yield arg
		if self.children:
			for child in self.children:
				yield child

	def __getattr__(self, name):
		return self[name]

	def __getitem__(self, name):
		if isinstance(name, int):
			return self.arguments[name]
		else:
			return self.properties[name]

class Symbol(object):
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return 'Symbol(%r)' % self.value

	def __str__(self):
		return ':%s' % self.value

	def __eq__(self, right):
		return (isinstance(right, Symbol) and right.value == self.value) or self.value == right

	def __ne__(self, right):
		return not (self == right)

class Parser(object):
	def __init__(self, document, preserve_property_order, symbols_as_strings, dlist):
		self.preserve_property_order = preserve_property_order
		self.symbols_as_strings = symbols_as_strings

		if hasattr(document, 'read') and callable(document.read):
			document = document.read()
		if str is not unicode and isinstance(document, str):
			document = document.decode('utf-8')
		ast = model.parse(document)

		self.document = Document() if dlist is None else dlist
		self.document += self.parseNodes(ast)

	def parseNodes(self, ast):
		if ast[0] == [None] or (isinstance(ast[0], list) and len(ast[0]) > 0 and isinstance(ast[0][0], unicode)):
			# TODO: Figure out why empty documents are so strangely handled
			return []
		nodes = map(self.parseNode, ast)
		return [node for node in nodes if node is not None]

	def parseNode(self, ast):
		if len(ast) == 0 or exists(ast, 'commented'):
			return
		name = self.parseIdentifier(ast['name'])
		children = props = args = None
		if exists(ast, 'props_and_args'):
			props, args = self.parsePropsAndArgs(ast['props_and_args'])
		if exists(ast, 'children') and not exists(ast['children'], 'commented'):
			children = self.parseNodes(ast['children']['children'])
		return Node(name, props, args, children)

	def parseIdentifier(self, ast):
		if exists(ast, 'bare'):
			return u''.join(ast['bare'])
		return self.parseString(ast['string'])

	def parsePropsAndArgs(self, ast):
		props = OrderedDict() if self.preserve_property_order else {}
		args = []
		for elem in ast:
			if exists(elem, 'commented'):
				continue
			if exists(elem, 'prop'):
				props[self.parseIdentifier(elem['prop']['name'])] = self.parseValue(elem['prop']['value'])
			else:
				args.append(self.parseValue(elem['value']))
		return props if len(props) else None, args if len(args) else None

	def parseValue(self, ast):
		if exists(ast, 'hex'):
			v = ast['hex'].replace('_', '')
			return int(v[0] + v[3:] if v[0] != '0' else v[2:], 16)
		elif exists(ast, 'octal'):
			v = ast['octal'].replace('_', '')
			return int(v[0] + v[3:] if v[0] != '0' else v[2:], 8)
		elif exists(ast, 'binary'):
			v = ast['binary'].replace('_', '')
			return int(v[0] + v[3:] if v[0] != '0' else v[2:], 2)
		elif exists(ast, 'decimal'):
			v = ast['decimal'].replace('_', '')
			if '.' in v or 'e' in v or 'E' in v:
				return float(v)
			else:
				return int(v)
		elif exists(ast, 'escstring') or exists(ast, 'rawstring'):
			return self.parseString(ast)
		elif exists(ast, 'symbol'):
			v = self.parseIdentifier(ast['symbol'])
			if self.symbols_as_strings:
				return v
			return Symbol(v)
		elif exists(ast, 'boolean'):
			return ast['boolean'] == 'true'
		elif exists(ast, 'null'):
			return None
		raise 'Unknown AST node! Internal failure: %r' % ast

	def parseString(self, ast):
		if exists(ast, 'escstring'):
			val = u''
			for elem in ast['escstring']:
				if exists(elem, 'char'):
					val += elem['char']
				elif exists(elem, 'escape'):
					esc = elem['escape']
					if exists(esc, 'named'):
						val += namedEscapes[esc['named']]
					else:
						val += unichr(int(esc['unichar'], 16))
			return val
		return ast['rawstring']

def parse(document, preserve_property_order=False, symbols_as_strings=False, dlist=None):
	parser = Parser(document, preserve_property_order, symbols_as_strings, dlist)
	return parser.document
