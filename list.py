#param list will take the list input
#param pos1 will take the index value
#param pos2 will take the index value
# def swap_list(list, pos1, pos2):
#     #Alternate
#     # list[pos1], list[pos2] = list[pos2], list[pos1]
#     temp = list[pos1]
#     list[pos1] = list[pos2]
#     list[pos2] = temp
#     return list
#
# new_list = [1,2,3,4,5]
# print(swap_list(new_list, 0, 4))

#Find length of list without using function
li = [1,2,3,4,5]
#print('Length of list is:' + str(len(li)))
counter = 0
for i in li:
    counter = counter + 1

print('Length of list is:' + str(counter))

#Reverse list using slicing method
li = [1,2,3,4,5]
print(li[::-1])

#Reverse list using insert function
li = [1,2,3,4,5]
l = []
for i in li:
    l.insert(0, i)
print(l)

#Reverse list using 2 pointer approach
li = [1,2,3,4,5]
def reverse_list(list):

    start_ind = 0
    end_ind = len(list)-1
    while(start_ind < end_ind):
        temp = list[start_ind]
        list[start_ind] = list[end_ind]
        list[end_ind] = temp
        start_ind = start_ind + 1
        end_ind = end_ind -1
    return list

print(reverse_list(li))

#WAP to find the occurance of any element ele in a list li
def occur_ele(li, ele):
    count = 0
    for i in li:
        if i == ele:
            count += 1
    return count
el = 1
element = occur_ele([1,2,3,4,1], el)
print(f'{el} occurs {element} times in list')

#WAP to convert ith element with jth element