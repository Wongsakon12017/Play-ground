def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y != 0:
        return x / y
    else:
        return "Can't devide by 0"

while True:
    print("Select option:")
    print("1. Plus")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Devide")

    choice = int(input("Input number (1/2/3/4): "))

    if choice in [1,2,3,4]:
        
        num1 = float(input("Number 1: "))
        num2 = float(input("Number 2: "))

        if choice == 1:
            print(num1, "+", num2, "=", add(num1, num2))
        elif choice == 2:
            print(num1, "-", num2, "=", subtract(num1, num2))
        elif choice == 3:
            print(num1, "*", num2, "=", multiply(num1, num2))
        elif choice == 4:
            print(num1, "/", num2, "=", divide(num1, num2))
        else:
            print("Error! Please try again.")
    else:
        print('Type 1 2 3 4 to select ')
        pass