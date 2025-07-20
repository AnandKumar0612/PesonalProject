#Guess the correct number which is 9 in this case with only 3 attempt
#purpose of this example to show else of while loop, when while loops complete without break i.e not condition was true
secret_number = 9
guess_count = 0
guess_limit = 3
while guess_count < guess_limit:
    guess = int(input("Guess: "))
    guess_count += 1
    if guess == secret_number:
        print("You guessed the right number")
        break
else:
    print("Maximum limit reached")


