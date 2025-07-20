def occur_ele(li, ele):
    count = 0
    for i in li:
        if i == ele:
            count += 1
    return count

for i in 'anand':
    element = occur_ele('anand', i)
    print(f'{i} occurs {element} times in list')
