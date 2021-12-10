import sys
from typing import Match
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QWidget, QVBoxLayout, QPushButton, QMessageBox


class Calculator(QWidget):
    def __init__(self):
        super(Calculator, self).__init__()

        self.expressionTokens = []
        self.line = ''

        #input and layouts
        self.vbox = QVBoxLayout(self)
        self.input = QLineEdit(self)
        self.hboxes_numbers = [
            QHBoxLayout(), QHBoxLayout(), QHBoxLayout(), QHBoxLayout()]
        self.hboxes_buttons = QHBoxLayout()
        self.hbox_input = QHBoxLayout()
        self.hbox_input.addWidget(self.input)

        self.vbox.addLayout(self.hbox_input)
        for i in self.hboxes_numbers:
            self.vbox.addLayout(i)
        self.vbox.addLayout(self.hboxes_buttons)
        self.vbox.addWidget(self.input)
        # number buttons
        self.buttons = []

        def buttonClickedGen_addchar(obj, num):
            i = num
            return lambda: obj.buttonClicked(i)

        def buttonClickedGen_addtoken(obj, num):
            i = num
            return lambda: obj.expressionTokens.append(Expression_token('number', i))
        for i in range(0, 10):
            self.buttons.append(QPushButton(str(i), self))
            self.hboxes_numbers[i//3].addWidget(self.buttons[i])

            self.buttons[i].clicked.connect(buttonClickedGen_addchar(self, i))
            self.buttons[i].clicked.connect(buttonClickedGen_addtoken(self, i))

        # buttons
        self.b_plus = QPushButton("+", self)
        self.b_plus.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('plus', '+')))
        self.b_plus.clicked.connect(lambda: self.buttonClicked('+'))
        self.hboxes_numbers[3].addWidget(self.b_plus)
        self.b_minus = QPushButton("-", self)
        self.b_minus.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('minus', '-')))
        self.b_minus.clicked.connect(lambda: self.buttonClicked('-'))
        self.hboxes_numbers[3].addWidget(self.b_minus)
        self.b_dot = QPushButton(".", self)
        self.b_dot.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('dot', '.')))
        self.b_dot.clicked.connect(lambda: self.buttonClicked('.'))
        self.hboxes_numbers[3].addWidget(self.b_dot)
        self.back = QPushButton("<-", self)
        self.back.clicked.connect(
            lambda: self.rmLast())
        self.hboxes_numbers[3].addWidget(self.back)
        self.b_star = QPushButton("*", self)
        self.b_star.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('star', '*')))
        self.b_star.clicked.connect(lambda: self.buttonClicked('*'))
        self.hboxes_buttons.addWidget(self.b_star)
        self.b_slash = QPushButton("/", self)
        self.b_slash.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('slash', '/')))
        self.b_slash.clicked.connect(lambda: self.buttonClicked('/'))
        self.hboxes_buttons.addWidget(self.b_slash)
        self.b_openp = QPushButton("(", self)
        self.b_openp.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('openp', '(')))
        self.b_openp.clicked.connect(lambda: self.buttonClicked('('))
        self.hboxes_buttons.addWidget(self.b_openp)
        self.b_closep = QPushButton(")", self)
        self.b_closep.clicked.connect(
            lambda: self.expressionTokens.append(Expression_token('closep', ')')))
        self.b_closep.clicked.connect(lambda: self.buttonClicked(')'))
        self.hboxes_buttons.addWidget(self.b_closep)
        self.b_result = QPushButton("=", self)
        self.b_result.clicked.connect(lambda: self.Evaluate())  # не забыть
        self.hboxes_buttons.addWidget(self.b_result)

    def buttonClicked(self, button):

        self.line += str(button)
        self.input.setText(self.line)

    def rmLast(self):
        if(len(self.expressionTokens) > 0):
            self.expressionTokens.pop()
            self.line = self.line[:-1]
            self.input.setText(self.line)

    def Evaluate(self):
        try:
            tree_builder = TreeBuilder(self.expressionTokens)
            tree = tree_builder.Build()
            result = Evaluate(tree)
        except:
            QMessageBox.about(self, "Error", "Не удалось считать выражение")
            result = 0
        if (result % 1 == 0):
            result = int(result)
        self.line = str(result)
        self.expressionTokens = [Expression_token("number", result)]
        self.input.setText(self.line)


class Expression_token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


class Unary_expreession_node:
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op


class Binary_expression_node:
    def __init__(self, number, op):
        self.number = number
        self.op = op


class TreeBuilder:
    def __init__(self, tokens):
        self.position = 0
        self.tokens = tokens
        self.MergeNums()

    def Current(self):
        if(self.position < len(self.tokens)):
            return self.tokens[self.position]
        return Expression_token('end', None)

    def Peek(self, length):
        if (length + self.position >= len(self.tokens)):
            return Expression_token("end", None)
        else:
            return self.tokens[self.position + length]

    def Next(self):
        ans = self.Current()
        self.position += 1
        return ans

    def Match(self, kind):
        if(self.Current().kind == kind):
            return self.Current()
        return None

    def MergeNums(self):
        new_tokens = []
        self.position = 0
        num = ''
        while(self.Current().kind != 'end'):
            if(self.Current().kind == 'number' or self.Current().kind == "dot"):
                num += str(self.Next().value)
            else:
                if(num != ''):
                    new_tokens.append(Expression_token('number', float(num)))
                    num = ''
                new_tokens.append(self.Next())
        if(num != ''):
            new_tokens.append(Expression_token('number', float(num)))
            num = ''
        self.tokens = new_tokens
        self.position = 0

    def Build(self):
        return self.ParseTerm()

    def ParseTerm(self):
        left = self.ParseFactor()
        while(self.Current().kind == 'plus' or self.Current().kind == 'minus'):
            op = self.Next()
            right = self.ParseFactor()
            left = Unary_expreession_node(left, op, right)
        return left

    def ParseFactor(self):
        left = self.ParsePrimary()
        while (self.Current().kind == 'star' or self.Current().kind == 'slash'):
            op = self.Next()
            right = self.ParsePrimary()
            left = Unary_expreession_node(left, op, right)
        return left

    def ParsePrimary(self):
        if(self.Current().kind == 'openp'):
            openp = self.Next()
            expression = self.ParseTerm()
            closep = self.Next()
            return Binary_expression_node(expression, Expression_token('plus', '+'))
        elif (self.Current().kind == 'minus'):
            op = self.Next()
            number = self.ParsePrimary()
            return Binary_expression_node(number, op)
        elif (self.Current().kind == 'number'):
            number = self.Next()
            return Binary_expression_node(number, Expression_token('plus', '+'))


def Evaluate(tree):
    if isinstance(tree, Unary_expreession_node):
        left = Evaluate(tree.left)
        right = Evaluate(tree.right)
        if (tree.op.kind == 'plus'):
            return left + right
        elif (tree.op.kind == 'minus'):
            return left - right
        elif (tree.op.kind == 'star'):
            return left * right
        elif (tree.op.kind == 'slash'):
            if(right == 0):
                QMessageBox.about(win, "Error", "Делить на 0 нельзя")
                return 0
            return left / right
    elif isinstance(tree, Binary_expression_node):
        num = tree.number

        if(tree.op.kind == 'plus'):
            if (isinstance(num, Expression_token)):
                return num.value
            else:
                return Evaluate(num)
        elif(tree.op.kind == 'minus'):
            if (isinstance(num, Expression_token)):
                return -num.value
            else:
                return -Evaluate(num)


# APP
app = QApplication(sys.argv)
win = Calculator()
win.show()
sys.exit(app.exec_())
# TREE BUILDING AND EVAULATING
