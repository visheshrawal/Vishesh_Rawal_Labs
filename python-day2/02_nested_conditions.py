age= int(input("Enter your age:"))
citizen = input("Are you a Indian citizen? (yes/no):")

if age >=18:
    if citizen.lower() == "yes":
        print("You're eligible to vote in India.")
    else:
        print("you must be a citizen to vote.")

else:
    print("You're too young to vote")