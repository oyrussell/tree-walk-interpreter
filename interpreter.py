from Ast import *
from Class import *
from Callable import *
from Function import *
import Lox
import Environment

class Interpreter(Visitor,StmtVisitor):
    globalEnv=Environment.environment(None)
    def __init__(self):
        self.environment=self.globalEnv
        self.locals=dict()
        self.globalEnv.define("clock",ClockCallable())

    def interpret(self,statments:list):
        try:
            for statment in statments:
                self.execute(statment)
        except RunTimeError as e:
            Lox.lox.runtimeError(e)

    def execute(self, stmt:Stmt):
        stmt.accept(self) 

    def resolve(self, expr:Expr, depth:int):
        self.locals[expr]=depth
       
    def evaluate(self, expr:Expr):
        return expr.accept(self)

    def isTruthy(self,val):
        if val is None: 
            return False
        if type(val) is bool:
            return bool(val)
        return True

    def isEqual(self,a,b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a==b
    
    def executeBlock(self,statments:list,env):
        previous=self.environment
        try:
            self.environment=env 
            for s in statments:
                self.execute(s)
        finally:
            self.environment=previous

    def numOperandsCheck(self,operator, *operands):
        statusOk=True
        for operand in operands:
            if type(operand) is not float:
                statusOk=False
        if statusOk is False:
            raise RunTimeError(operator,"Operand must be a number")

    def stringify(self,obj):
        if obj is None:
            return "nil"

        if type(obj) is float:
            text=str(obj)
            if text.endswith(".0"):
                text=text[0:len(text)-2]
            return text

        return str(obj)

    def varLoopUp(self, name, expr):
        distance=self.locals.get(expr)
        if distance is not None:
            return self.environment.getAt(distance,name.lexeme)
        else:
            return self.globalEnv.get(name)

    def visitExpressionStmt(self, stmt:Expression):
        self.evaluate(stmt.expression)
        return None 

    def visitPrintStmt(self, stmt:Print):
        value=self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visitVarStmt(self, stmt:Var):
        value=None
        if stmt.initializer is not None:
            value=self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme,value)
        return None

    def visitBlockStmt(self, stmt:Block):
        inner_env=Environment.environment(self.environment)
        
        self.executeBlock(stmt.statments,inner_env)
        return None

    def visitIfStmt(self, stmt:If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)
        return None

    def visitWhileStmt(self,stmt:While):
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visitFunctionStmt(self, stmt:Function):
        function=LoxFunction(stmt,self.environment,False) 
        self.environment.define(stmt.name.lexeme,function)
        return None

    def visitReturnStmt(self,stmt:Return):
        value=None
        if(stmt.value!=None):
            value=self.evaluate(stmt.value)
        raise ReturnException(value)
    
    def visitClassStmt(self,stmt:Class):
        superclass=None
        if stmt.superclass is not None:
            superclass=self.evaluate(stmt.superclass)
            if not isinstance(superclass,FLOXclass):
                raise RunTimeError(stmt.superclass.name,"super class must be class")
        self.environment.define(stmt.name.lexeme,None)
        
        if stmt.superclass is not None:
            self.environment=Environment.environment(self.environment)
            self.environment.define("super",superclass)
        methods={}
        for m in stmt.methods:
            isInit=m.name.lexeme == "init"
            func=LoxFunction(m,self.environment,isInit)
            methods[m.name.lexeme]=func
        
        klass=FLOXclass(stmt.name.lexeme,superclass,methods)
        if stmt.superclass is not None:
            self.environment=self.environment.enclosing
        self.environment.assign(stmt.name,klass)
        return None

    def visitLiteralExpr(self, expr:Literal):
        return expr.value

    def visitBinaryExpr(self, expr:Binary):
        left=self.evaluate(expr.left)
        right=self.evaluate(expr.right)
        t=expr.operator.type
        if t==tokType.MINUS:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)-float(right)
        elif t==tokType.PLUS:
            if type(left) is float and type(right) is float:
                return float(left)+float(right)
            elif type(left) is str and type(right) is str:
                return str(left)+str(right)
            else:
                raise RunTimeError(expr.operator,"Operands must be two numbers or two strings")
        elif t==tokType.SLASH:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)/float(right)
        elif t==tokType.STAR:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)*float(right)
        elif t==tokType.GREATER:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)>float(right)
        elif t==tokType.GREATER_EQUAL:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)>=float(right)
        elif t==tokType.LESS:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)<float(right)
        elif t==tokType.LESS_EQUAL:
            self.numOperandsCheck(expr.operator,left,right)
            return float(left)<=float(right)
        elif t==tokType.BANG_EQUAL:
            return not self.isEqual(left,right)
        elif t==tokType.EQUAL_EQUAL:
            return self.isEqual(left,right)
        return None

    def visitGroupingExpr(self, expr:Grouping):
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr:Unary):
        rightVal=self.evaluate(expr.right)
        t=expr.operator.type
        if t==tokType.MINUS:
            return -1.0*float(rightVal)
        if t==tokType.BANG:
            return not self.isTruthy(rightVal)
        return None

    def visitVariableExpr(self, expr:Variable):
        
        return self.varLoopUp(expr.name,expr) 

    def visitAssignExpr(self,expr:Assign):
        value=self.evaluate(expr.value)
        distance=self.locals.get(expr)
        if distance is not None:
            self.environment.assignAt(distance,expr.name,value)
        else:
            self.globalEnv.assign(expr.name,value)
        return value

    def visitLogicalExpr(self,expr:Logical):
        left=self.evaluate(expr.left)
        if expr.operator.type==tokType.OR:
            if self.isTruthy(left):
                return left
            else:
                if not self.isTruthy(left):
                    return left
        return self.evaluate(expr.right)

    def visitCallExpr(self, expr:Call):
        callee=self.evaluate(expr.callee) 
        arguments=[]
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee,LoxCallable):
            raise RunTimeError(expr.paren,"can only call function and classes")
        function=callee 
        if len(arguments) != function.arity():
            raise RuntimeError(expr.paren,"Expected {} arguments but got {}.".format(function.arity(),len(arguments)))
        return function.call(self,arguments)

    def visitGetExpr(self, expr:Get):
        object=self.evaluate(expr.obj)
        if isinstance(object,FLOXInstance):
            return object.get(expr.name)
        raise RunTimeError(expr.name,"Only instances have properties")

    def visitSetExpr(self,expr:Set):
        object=self.evaluate(expr.obj)
        if not isinstance(object,FLOXInstance):
            raise RunTimeError(expr.name,"Only instances have properties")
        value=self.evaluate(expr.value)
        object.set(expr.name,value)
        return value

    def visitThisExpr(self,expr:This):
        return self.varLoopUp(expr.keyword,expr)

    def visitSuperExpr(self,expr:Super):
        distance=self.locals.get(expr)
        superclass=self.environment.getAt(distance,"super")
        obj=self.environment.getAt(distance-1,"this")
        method=superclass.findMethod(expr.method.lexeme)
        if method is None:
            raise RunTimeError(expr.method,"Undefined propety {} in super".format(expr.method.lexeme))
        return method.bind(obj)
