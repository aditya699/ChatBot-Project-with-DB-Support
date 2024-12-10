'''
This is developer attempt to learn async programming.

NOTE :
1.In synchronous programming, tasks are executed one after another. A task must complete before the next task starts.

2.In asynchronous programming, tasks can start before the previous one finishes, saving time.
'''

# Synchronous (old way)
# import time

# def make_coffee():
#     print("Starting to make coffee")
#     time.sleep(2)  # This blocks everything!
#     print("Coffee ready")

# def make_toast():
#     print("Starting to make toast")
#     time.sleep(3)  # This blocks everything!
#     print("Toast ready")

# # This takes 5 seconds total because it runs one after another
# make_coffee()
# make_toast()


import asyncio

async def make_coffee():
    print("Starting to make coffee")
    await asyncio.sleep(2)  # This lets other tasks run!
    print("Coffee ready")

async def make_toast():
    print("Starting to make toast")
    await asyncio.sleep(3)  # This lets other tasks run!
    print("Toast ready")

async def main():
    # This takes only 3 seconds because they run at the same time!
    await asyncio.gather(make_coffee(), make_toast())

# Run our async program
asyncio.run(main())