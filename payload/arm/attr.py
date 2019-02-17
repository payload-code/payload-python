from six import with_metaclass
import operator

class Filter(object):

    def __init__(self, attr, val):
        self.attr  = str(attr)
        self.val   = val
        self.opval = self.op+str(val)

    def __or__(self, other):
        if not isinstance( other, Filter ):
            raise TypeError('invalid type')
        if other.attr != self.attr:
            raise ValueError('`or` only works on the same attribute')
        return Filter( self.attr, '|'.join(
            self.opval.split('|') + other.opval.split('|') ) )

class Equal(Filter):
    op = ''

class NotEqual(Filter):
    op = '!'

class GreaterThan(Filter):
    op = '>'

class LessThan(Filter):
    op = '<'

class GreaterThanEqual(Filter):
    op = '>='

class LessThanEqual(Filter):
    op = '<='

class Contains(Filter):
    op = '?*'

class MetaAttr(type):
    def __getattr__(cls, key):
        return Attr(key)
    def __iter__(cls):
        yield '*'

class Attr(with_metaclass(MetaAttr)):
    is_method = False

    def __init__(self, param, parent=None):
        self.param = param
        self.parent = parent
        if not parent:
            self.key = self.param
        else:
            self.key = '{}[{}]'.format( self.parent.key, self.param )

    def __getattr__(self, key):
        if self.is_method:
            raise ValueError('cannot get attr of method')
        return Attr(key,parent=self)

    def __str__(self):
        if self.is_method:
            return '{}({})'.format( self.param, self.parent.key )
        return self.key

    def __eq__(self, other):
        return Equal( self, other )

    def __ne__(self, other):
        return NotEqual( self, other )

    def __gt__(self, other):
        return GreaterThan( self, other )

    def __lt__(self, other):
        return LessThan( self, other )

    def __ge__(self, other):
        return GreaterThanEqual( self, other )

    def __le__(self, other):
        return LessThanEqual( self, other )

    def contains(self, other):
        return Contains( self, other )

    def __call__(self):
        self.is_method = True
        return self
