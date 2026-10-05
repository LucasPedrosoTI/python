# python permutação e combinação

## Pequeno programa que cálcula o número de permutações ou combinações possíveis de um conjunto em python

```python
def fatorial(num):
    resultado = 1
    while num >= 1:
        resultado *= num
        num -= 1
    return resultado

n = int(input("Número de escolhas possíveis(n): "))
r = int(input("Quantos você pode escolher?(r): "))

ordem = input("A ordem importa(s/n): ")

if (ordem != "s" and ordem != "n" ):
    print("A resposta deve ser s ou n")
else:
    if ordem == "s":
        ordem = True
    else:
        ordem = False

    repete = input("Pode repetir as escolhas (s/n): ")

    if (repete != "s" and  repete != "n"):
        print("A resposta deve ser s ou n")
    else:
        if repete == "s":
            repete = True
        else:
            repete = False
    print("========================================")
    if (ordem and repete):
        result = n ** r
        print("Resultado: ", result, " permutações")
    elif ordem:
        result = fatorial(n) / fatorial(n-r)
        print("Resultado: ", result, " permutações")
    elif repete:
        result = fatorial(n + r - 1) / (fatorial(r) * fatorial(n - 1))
        print("Resultado: ", result, " combinações")
    else:
        result = fatorial(n) / (fatorial(r) * fatorial(n -r))
        print("Resultado: ", result, " combinações")

print("========================================")
print("Fim do programa!")
```
