from functools import reduce

sum_of_numbers = lambda x, y: x+y

list_of_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

output = []

output = reduce(sum_of_numbers, list_of_numbers)

print(output)
