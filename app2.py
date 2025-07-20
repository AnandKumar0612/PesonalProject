#exercise for loop
prices = [10, 20, 30]
price = 0
for item in prices:
    price = price + item
print(f"Price of item is {price}")

#Nested loop
#To print coordinates
for x in range(4):
    for y in range(3):
        print(f"({x}, {y})")

#Draw F using x
number = [5, 2, 5, 2, 2]
for item in number:
    output = ''
    for i in range(item):
        output += 'x'
    print(output)

#Draw L using x
number = [1, 1, 1, 1, 5]
for item in number:
    output = ''
    for i in range(item):
        output += 'x'
    print(output)

#WAP to find largest number in list
number = [3, 4, 5, 1, 8, 10]
max = number[0]
for num in number:
    if num > max:
        max = num
print(max)

#WAP to remove duplicates from a list
number = [2, 3, 2, 4, 5, 6, 4, 6]
dup = []
for i in number:
    if i not in dup:
        dup.append(i)
print(dup)

#Emojis Converter
message = input(">")
words = message.split(' ')
emojis_dic = {
    ":)": "😊",
    ":(": "😒",
    ":P": "😜"
}
output = ""
for ch in words:
    output += emojis_dic.get(ch, ch) + " "
print(output)