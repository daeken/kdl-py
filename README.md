# kdl-py

A Python library for the [KDL Document Language](https://github.com/kdl-org/kdl).

## Install

    pip install kdl-py

kdl-py is fully Python 2.7 and Python 3 friendly.

## Usage

```py
from kdl import parse, Document, Node
print(parse('''// Nodes can be separated into multiple lines
title \
  "Some title"


// Files must be utf8 encoded!
smile "😁"

// Instead of anonymous nodes, nodes and properties can be wrapped
// in "" for arbitrary node names.
"!@#$@$%Q#$%~@!40" "1.2.3" "!!!!!"=true

// The following is a legal bare identifier:
foo123~!@#$%^&*.:'|?+ "weeee"

// And you can also use unicode!
ノード　お名前="☜(ﾟヮﾟ☜)"

// kdl specifically allows properties and values to be
// interspersed with each other, much like CLI commands.
foo bar=true "baz" quux=false 1 2 3
'''))

# Creating documents from scratch is currently very gross
print()
doc = Document()
doc.append(Node(name='simple-name', properties=None, arguments=[123], children=[Node(name='complex name here!', properties=None, arguments=None, children=None)]))
print(doc)
```

```
title "Some title"
smile "😁"
!@#$@$%Q#$%~@!40 !!!!!=true "1.2.3"
foo123~!@#$%^&*.:'|/?+ "weeee"
ノード お名前="☜(ﾟヮﾟ☜)"
foo bar=true quux=false "baz" 1 2 3

simple-name 123 {
        "complex name here!"
}
```

## License

The code is available under the [MIT license](LICENSE). The example above is
made available from https://github.com/kdl-org/kdl under
[Creative Commons Attribution-ShareAlike 4.0 International](https://github.com/kdl-org/kdl/blob/main/LICENSE.md).
