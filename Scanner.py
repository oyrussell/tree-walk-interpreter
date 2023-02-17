from Token import Token
from TokenTypes import tokType
import Lox

keywords={
    'and':tokType.AND,
    'class':tokType.CLASS,
    'else':tokType.ELSE,
    'false':tokType.FALSE,
    'for':tokType.FOR,
    'fun':tokType.FUN,
    'if':tokType.IF,
    'nil':tokType.NIL,
    'or':tokType.OR,
    'print':tokType.PRINT,
    'return':tokType.RETURN,
    'super':tokType.SUPER,
    'this':tokType.THIS,
    'true':tokType.TRUE,
    'var':tokType.VAR,
    'while':tokType.WHILE
}

class Scanner(object):
    def __init__(self, source):
        self.source=source
        self.tokens=list()
        self.start=0
        self.current=0
        self.line=1

    def scanToken(self):
        c=self.advance()
        if c=='(':
            self.addToken(tokType.LEFT_PAREN)
        elif c==')':
            self.addToken(tokType.RIGHT_PAREN)
        elif c=='{':
            self.addToken(tokType.LEFT_BRACE)
        elif c=='}':
            self.addToken(tokType.RIGHT_BRACE)
        elif c==',':
            self.addToken(tokType.COMMA)
        elif c=='.':
            self.addToken(tokType.DOT)
        elif c=='-':
            self.addToken(tokType.MINUS)
        elif c=='+':
            self.addToken(tokType.PLUS)
        elif c==';':
            self.addToken(tokType.SEMICOLON)
        elif c=='*':
            self.addToken(tokType.STAR)
        elif c=="!":
            if self.match('='):
                self.addToken(tokType.BANG_EQUAL)
            else:
                self.addToken(tokType.BANG)
        elif c=='=':
            if self.match('='):
                self.addToken(tokType.LESS_EQUAL)
            else:
                self.addToken(tokType.EQUAL)
        elif c=='<':
            if self.match('='):
                self.addToken(tokType.LESS_EQUAL)
            else:
                self.addToken(tokType.LESS)
        elif c=='>':
            if self.match('='):
                self.addToken(tokType.GREATER_EQUAL)
            else:
                self.addToken(tokType.GREATER)
        elif c=='/':
            if self.match('/'): 
                while self.peek()!='\n' and not self.isAtEnd():
                    self.advance()
            else:
                self.addToken(tokType.SLASH)
        elif c in [' ','\r','\t']:
            pass
        elif c=='\n':
            self.line+=1
            pass
        elif c=='"':
            self.string() 
        else:
            if self.isDigit(c):
                self.number()
            elif self.isAlpha(c):
                self.identifier()
            else:
                Lox.lox.error(self.line,"Unexpected Character")
                
    def match(self, expected):
        if self.isAtEnd():
            return False
        if self.source[self.current]!=expected:
            return False
        self.current+=1
        return True

    def isAtEnd(self):
        return self.current>=len(self.source)

    def advance(self):
        self.current+=1
        return self.source[self.current-1]

    
    def peek(self):
        if self.isAtEnd():
            return '\0'
        else:
            return self.source[self.current]


    def peekNext(self):
        if self.current+1>=len(self.source):
            return '\0'
        return self.source[self.current+1]

    def string(self):
        while self.peek()!='"' and not self.isAtEnd():
            if self.peek()=='\n':
                self.line+=1
            self.advance()
        if self.isAtEnd():
             Lox.lox.error(self.line,"Unterminated string.")
             return
        self.advance()
        value=self.source[self.start+1:self.current-1] 
        self.addToken(tokType.STRING,value)

    def isDigit(self, char):
        return char>='0' and char<='9'

    def isAlpha(self,char):
        return (char>='a' and char<='z') or (char>='A' and char<='Z') or char=='_'

    def isAlphaNumeric(self,char):
        return self.isAlpha(char) or self.isDigit(char)

    def number(self):
        while self.isDigit(self.peek()):
            self.advance()
        if self.peek()=='.' and self.isDigit(self.peekNext()):
            self.advance()
            while self.isDigit(self.peek()):
                self.advance()
        self.addToken(tokType.NUMBER,float(self.source[self.start:self.current]))
    
    def identifier(self):
        while self.isAlphaNumeric(self.peek()):
            self.advance()
        text=self.source[self.start:self.current]
        type=keywords.get(text)
        if type is None:
            type=tokType.IDENTIFIER
        self.addToken(type)

    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()
        self.tokens.append(Token(tokType.EOF,"",None,self.line))
        return self.tokens

    def addToken(self, type, literal=None):
        text=self.source[self.start:self.current]
        self.tokens.append(Token(type,text,literal,self.line))