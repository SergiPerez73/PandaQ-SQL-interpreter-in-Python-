grammar: pandaQ.g4
	antlr4 -Dlanguage=Python3 -no-listener -visitor pandaQ.g4

clear:
	rm -f *.interp
	rm -f *.tokens
	rm -f pandaQLexer.py
	rm -f pandaQVisitor.py
	rm -f pandaQParser.py
