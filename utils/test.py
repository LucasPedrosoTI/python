def sum_digits(n):
  if n < 10:
    return n
  else:
    return n % 10 + sum_digits(n // 10)

def palindrome(p):
  if len(p) <= 1:
    return True
  if p[0] != p[-1]:
    return False
  return palindrome(p[1:-1])

def prime(n):
  def prime_aux(n, i):
    if n == 2:
      return True
    if n % i == 0:
      return False
    if i * i > n:
      return True
    return prime_aux(n, i + 1)
  return prime_aux(n, 2)

def fun1(x, y):
  valor = 3
  if x > y:
    return -1
  
  for i in range(x,y):
    valor += x

  return valor 

print(fun1(1, 2))
