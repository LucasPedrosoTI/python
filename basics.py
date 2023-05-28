import random

"""
This file contains the basics of Python
Suchs as language syntax, basic features, libraries, and functions
"""
# To print something, use print command
print("Python version is great")

# To get input from user, use input command
# name: str = input("Type your name: ")
# print(f"Welcome to Python, {name}")

# Types
age: int = 29
height: float = 1.75
weight = 80
is_overwight = False

# functions
def calc_bmi(weight: float, height: float) -> float:
  return weight/(height**2)

bmi = calc_bmi(weight, height)
is_overwight = bmi > 29.9
print(f"BMI calculation: {bmi}")
print(f"Overwight? {'yes' if is_overwight else 'no'}")

# Getting the type
print(type(bmi))
# Verifying the type
print(isinstance(bmi, float))

# Operators
"""
- Sum: +
- Subtraction: - 
- Multiply: *
- Division: /
- Int Division: // - discard decimal part
- Mod: %
- Exponentiation: **
"""
print(weight // height)
print(f"Is even? {'yes' if random.randint(1, 10) % 2 == 0 else 'no'}")

# Type conversions
num = '10'
num = int(num)
num = float(num)

arr = ['Yes', 'No', 1, 0, 'Y', 'N', '1', '0', '']
rand_bool = arr[random.randint(0, len(arr)-1)]
print(rand_bool)
print('yes' if bool(rand_bool) else 'no')

# Contional structures
if (age >= 18):
  print("Is not under age")
elif (age <= 0):
  print("Not a valid age")
else:
  print("Is under age")

# While Loop 
while (age <= 40):
  print(f"You can't retire, you can retire at age of 40, and  you're {age}")
  age += 1

# For Loop
for i in range(len(arr)):
  print(i)

for value in arr:
  print(value)

# defines start and end values
for i in range(5, 10):
  print(i * 10)

# defines start, end, and interval values 
arr = [];
for i in range(0, 100, 10):
  arr.append(i)
print(arr) # [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]