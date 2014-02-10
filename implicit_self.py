#!/usr/bin/env python3
'''Inheriting from ImplicitSelf will make your class's methods have
implicit self and cls variables (without being declared explicitly),
similar to how Javascript works. See the A class for an example.

'''



class ImplicitSelfDecorator:

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        func = self.func
        selfvar = obj
        clsvar = type(obj) if obj is not None else cls

        def decorated(*args, **kw):
            self_defined = 'self' in func.__globals__
            if self_defined:
                oldself = func.__globals__['self']
            cls_defined = 'cls' in func.__globals__
            if cls_defined:
                oldcls = func.__globals__['cls']

            func.__globals__['self'] = selfvar
            func.__globals__['cls'] = clsvar
            result = func(*args, **kw)

            if self_defined:
                func.__globals__['self'] = oldself
            else:
                del func.__globals__['self']
            if cls_defined:
                func.__globals__['cls'] = oldcls
            else:
                del func.__globals__['cls']

            return result

        return decorated


class ImplicitSelfMetaclass(type):

    def __new__(cls, name, bases, d):
        for key in d:
            if callable(d[key]):
                d[key] = ImplicitSelfDecorator(d[key])
        return type.__new__(cls, name, bases, d)


class ImplicitSelf(metaclass=ImplicitSelfMetaclass):
    '''Inherit from this class to have implicit self and cls defined
    within your method bodies, using global namespace munging.'''
    pass


class A(ImplicitSelf):
    '''
    >>> a = A()
    >>> a.m()
    self is <implicit_self.A object at 0x25df8d0>
    cls is <class 'implicit_self.A'>
    >>> self
    Traceback (most recent call last):
      File "<pyshell#38>", line 1, in <module>
        self
    NameError: name 'self' is not defined
    >>> cls
    Traceback (most recent call last):
      File "<pyshell#39>", line 1, in <module>
        cls
    NameError: name 'cls' is not defined
    >>>
    '''

    def m():
        print('self is {}'.format(self))
        print('cls is {}'.format(cls))



### Second approach: using sys._getframe ###

import sys

def resolve_dynamic_var(name):
    frame = sys._getframe(0)
    while frame is not None:
        if name in frame.f_locals:
            return frame.f_locals[name]
        frame = frame.f_back

def self():
    return resolve_dynamic_var('self')

def cls():
    return resolve_dynamic_var('cls')


class SelfClsDescriptor:

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls_=None):

        func = self.func

        def decorated(*args, **kw):
            self = obj
            cls = type(obj) if obj is not None else cls_

            return func(*args, **kw)

        return decorated

class SelfClsMetaclass(type):

    def __new__(cls, name, bases, d):
        for key in d:
            if callable(d[key]):
                d[key] = SelfClsDescriptor(d[key])
        return type.__new__(cls, name, bases, d)

class SelfCls(metaclass=SelfClsMetaclass):
    '''Methods found in classes inheriting from this class can call the
    global functions self() and cls() to dynamically resolve their own
    instance object and class, without explicitly declaring them.

    '''
    pass

class B(SelfCls):
    '''
    >>> from implicit_self import B
    >>> b = B()
    >>> b.m()
    self() is <implicit_self.B object at 0x1182cd0>
    cls() is <class 'implicit_self.B'>
    >>>
    '''

    def m():
        print('self() is {}'.format(self()))
        print('cls() is {}'.format(cls()))
