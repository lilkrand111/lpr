import asyncio
import time


async def work(name, delay):
    print(f'{name}: start')
    await asyncio.sleep(delay)
    print(f'{name}: stop | Waited {delay} seconds')


async def work_blocking(name, delay):
    print(f'{name}: start')
    time.sleep(delay)
    print(f'{name}: stop | Waited {delay} seconds')


async def work_to_thread(name, delay):
    print(f'{name}: start')
    await asyncio.to_thread(time.sleep, delay)
    print(f'{name}: stop | Waited {delay} seconds')


def cpu_task():
    return sum(i * i for i in range(10**7))

async def cpu_work():
    return cpu_task()


async def exp1():
    start = time.perf_counter()
    await work('A', 1)
    await work('B', 2)
    await work('C', 3)
    return time.perf_counter() - start


async def exp2():
    start = time.perf_counter()
    await asyncio.gather(
        work('A', 1),
        work('B', 2),
        work('C', 3)
        )
    return time.perf_counter() - start


async def exp3():
    start = time.perf_counter()
    await asyncio.gather(
        work_blocking('A', 1),
        work_blocking('B', 2),
        work_blocking('C', 3)
    )
    return time.perf_counter() - start

async def exp4():
    t = time.perf_counter()
    cpu_task()
    return time.perf_counter() - t

async def exp5():
    t = time.perf_counter()
    await asyncio.gather(
        cpu_work(),
        cpu_work(),
        cpu_work()
    )
    return time.perf_counter() - t


async def exp6():
    start = time.perf_counter()
    await asyncio.gather(
        work_to_thread('A', 1),
        work_to_thread('B', 2),
        work_to_thread('C', 3)
    )
    return time.perf_counter() - start


async def ticker():
    while True:
        print("Tik")
        await asyncio.sleep(0.5)


async def main():
    task = asyncio.create_task(ticker())
    print("Start experiment 1:")
    t = await exp1()
    print(f"Experiment 1 has ended. Final time: {t} с.\n")
    print("Start experiment 2:")
    t = await exp2()
    print(f"Experiment 2 has ended. Final time: {t} с.\n")
    print('Start experiment 3:')
    t = await exp3()
    print(f"Experiment 3 has ended. Final time: {t} с.\n")
    print('Start experiment 4:')
    t = await exp4()
    print(f"Experiment 4 has ended. Final time: {t} с.\n")
    print('Start expirement 5:')
    t = await exp5()
    print(f'Expetiment 5 has ended. Final time {t} с.\n')
    print('Start experiment 6')
    t = await exp6()
    print(f'Experiment 6 has ended. Final time {t} с.\n')
    task.cancel()




if __name__ == '__main__':
    asyncio.run(main())