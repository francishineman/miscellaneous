evens = lambda x: x % 2 == 0

list_of_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

output = []

output = filter(evens, list_of_numbers)

for o in output:
    print(o)
