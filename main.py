# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def execute(x, y=20):
    print("Sum:", x + y)
    time.sleep(2)
    return x + y


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    t = time.time()
    results = list()
    for i in range(1,500):
        results.append(execute(i))
    print(results)
    print("Total time is ", time.time() - t)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
