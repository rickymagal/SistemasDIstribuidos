import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import random
import math
import time

def merge(*args):
    left, right = args[0] if len(args) == 1 else args
    left_length, right_length = len(left), len(right)
    left_index, right_index = 0, 0
    merged = []
    while left_index < left_length and right_index < right_length:
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1
    if left_index == left_length:
        merged.extend(right[right_index::])
    else:
        merged.extend(left[left_index::])
    return merged

def merge_sort(data):
    length = len(data)
    if length <= 1:
        return data
    middle = int(length / 2)
    left = merge_sort(data[:middle])
    right = merge_sort(data[middle:])
    return merge(left, right)


def merge_sort_process(data, k):
    pool = mp.Pool(k)
    size = int(math.ceil(float(len(data))/k))
    data = [data[i * size:(i + 1) * size] for i in range(k)]
    data = pool.map(merge_sort, data)
    iteration = 1
    while len(data) > 1:
        print("Iteration", iteration, data)
        iteration +=1
        extra = data.pop() if len(data) % 2 == 1 else None
        data = [(data[i], data[i + 1]) for i in range(0, len(data), 2)]
        data = pool.map(merge, data) + ([extra] if extra else [])
    print("Iteration", iteration, data)
    pool.close()
    return data[0] 

def merge_sort_thread(data, k):
    size = int(math.ceil(float(len(data))/k))
    data = [data[i * size:(i + 1) * size] for i in range(k)]
    pool = mp.pool.ThreadPool(processes=k)
    data = pool.map(merge_sort, data)
    iteration = 1
    while len(data) > 1:
        print("Iteration", iteration, data)
        iteration +=1
        extra = data.pop() if len(data) % 2 == 1 else None
        data = [(data[i], data[i + 1]) for i in range(0, len(data), 2)]
        data = pool.map(merge, data) + ([extra] if extra else [])
    print("Iteration", iteration, data)
    pool.close()
    return data[0] 

if __name__ == "__main__":
    n = int(input("Size of vector:"))
    k = int(input("Number of initial chunks:"))
    vector_unsorted = [random.randint(0,n) for i in range(n)]
    print("--------- Process Run -----------------")
    print("Unsorted vector ", vector_unsorted)
    start = time.time()
    vector_sorted = merge_sort_process(vector_unsorted, k)
    end = time.time() - start
    print("Sorted Vector: ", vector_sorted, "time: ", end)
    print("--------- Thread Run -----------------")
    print("Unsorted vector ", vector_unsorted)
    start = time.time()
    vector_sorted = merge_sort_thread(vector_unsorted, k)
    end = time.time() - start
    print("Sorted Vector: ", vector_sorted, "time: ", end)
