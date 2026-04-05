import csv
import random

# Generate 40x40 = 1600 numbers between 1 and 100
data = [[random.randint(1, 100) for _ in range(40)] for _ in range(40)]

with open('test_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print("test_data.csv created.")
