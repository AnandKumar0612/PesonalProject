# weight = int(input('Weight: '))
# unit = input('(K)g or (l)bs: ')
#
# if unit.upper() == 'K':
#     weight = weight * 2.20462
#     print('Weight in lbs: ' + str(weight))
# elif unit.upper() == 'L':
#     weight = weight / 2.20462
#     print('Weight in Kg: ' + str(weight))
# else:
#     print('No input')

# i = 1
# while i<=5:
#     print(i * '*')
#     i += 1

# name = "Anand is great"
# if " " in name:
#     print(name.replace(" ", ""))

num = [1, 2, 3, 4, 5]
for val in num:
    print(val)

for val in range(1, 6):
    print(val)

first = 'Anand'
last = 'Kumar'
message = first + ' [' + last + '] is a Coder'
msg = f'{first} [{last}] is a coder'
print(message)
print(msg)

#Covert Decimal to Binary
def decimal_to_binary(decimal):
    binary = ""
    while decimal > 0:
        rem = decimal % 2 #get the reminder
        binary = str(rem) + binary #conactenate reminder to binary
        decimal = decimal // 2 #get the quotient

    return binary

decimal = int(input("Please enter the decimal number to get the binary output: "))
print(decimal_to_binary(decimal)) #type is string

#Small exercise with If statement
price = 1000000
is_good_credit = False
if is_good_credit:
    down_payment = 0.1 * price
else:
    down_payment = 0.2 * price
print(f"Down payment is: ${down_payment}")