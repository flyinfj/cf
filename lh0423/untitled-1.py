def bubble_sort(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # 最后i个元素已经排好序
        for j in range(0, n-i-1):
            # 如果当前元素大于下一个元素
