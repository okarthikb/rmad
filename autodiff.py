from math import log


class Var:
  def __init__(self, val, param=False, args=(), grads=()):
    self.val = val  # value of Var
    self.grad = 0  # gradient of objective (or loss) w.r.t this Var
    self.args = args  # Vars used to create this Var
    self.param = param  # compute gradient or not?
    self.grads = grads  # gradients of self.val w.r.t arg vals

  def __repr__(self):
    return f"Var({self.val}, param=True)" if self.param else f"Var({self.val})"

  def par(self, val, o=None, grads=()):
    return Var(val, self.param | (o.param if o else False), (self, o), grads)

  def __mul__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    return self.par(self.val * o.val, o, (o.val, self.val))

  def __neg__(self):
    return self * -1

  def __add__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    return self.par(self.val + o.val, o, (1, 1))

  def __sub__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    return self.par(self.val - o.val, o, (1, -1))

  def __truediv__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    if self.param:
      return self.par(self.val / o.val, o, (1 / o.val, -self.val / (o.val * o.val)))
    return self.par(self.val / o.val, o)

  def __pow__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    if self.param:
      grads = (o.val * self.val ** (o.val - 1), log(abs(self.val) + 1e-10) * self.val ** o.val)
      return self.par(self.val ** o.val, o, grads)
    return self.par(self.val ** o.val, o)

  def log(self):
    if self.param:
      return self.par(log(self.val), grads=(1 / self.val,))
    return self.par(log(self.val))

  def __radd__(self, o):
    return self + o

  def __rsub__(self, o):
    return -self + o

  def __rmul__(self, o):
    return self * o

  def __rtruediv__(self, o):
    return o * self ** -1

  def __rpow__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    return o ** self

  def __lt__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    return self.val < o.val

  def __gt__(self, o):
    o = o if isinstance(o, Var) else Var(o)
    return self.val > o.val

  def backpass(self):
    for arg, grad in zip(self.args, self.grads):
      if arg and arg.param:
        arg.grad += self.grad * grad  # chain rule
        arg.backpass()  # recursive part

  def backward(self):
    self.grad = 1  # grad of objective w.r.t itself is 1
    self.backpass()
