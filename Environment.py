from Ast import *
from Token import Token
from TokenTypes import tokType
import Lox

class environment:
    def __init__(self, enclosing = None):
        self.values={}
        self.enclosing=enclosing 

    def get(self, name):
        if self.values.get(name.lexeme,"Not Registered") != "Not Registered":
            return self.values.get(name.lexeme)
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RunTimeError(name,"Undefined variable '"+name.lexeme+"'.")

    def define(self, name, value):
        self.values[name]=value

    def ancestor(self, distance):
        env=self
        for i in range(distance):
            env=env.enclosing
        return env

    def getAt(self, distance, name):
        return self.ancestor(distance).values.get(name)
            
    def assignAt(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme]=value

    def assign(self, name, value):
        if self.values.get(name.lexeme,"Not Registered") != "Not Registered":
            self.values[name.lexeme]=value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name,value)
            return
        raise RunTimeError(name,"Undefined variable '" + name.lexeme + "'.")