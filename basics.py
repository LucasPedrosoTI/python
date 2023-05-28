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
