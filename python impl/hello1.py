class MinHeap:
    def __init__(self):
        self.heap = [None] * 100
        self.size = 0

    def push(self, data):
        if self.size < 100:
            self.heap[self.size] = data
            self._heapify_up(self.size)
            self.size += 1
        else:
            if data[-1] > self.heap[0][-1]:
                self.heap[0] = data
                self._heapify_down(0)

    def _heapify_up(self, index):
        while index > 0:
            parent_index = (index - 1) // 2
            if self.heap[index][-1] < self.heap[parent_index][-1]:
                self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
                index = parent_index
            else:
                break

    def _heapify_down(self, index):
        while True:
            left_child_index = 2 * index + 1
            right_child_index = 2 * index + 2
            smallest_index = index

            if (left_child_index < self.size and
                    self.heap[left_child_index][-1] < self.heap[smallest_index][-1]):
                smallest_index = left_child_index

            if (right_child_index < self.size and
                    self.heap[right_child_index][-1] < self.heap[smallest_index][-1]):
                smallest_index = right_child_index

            if smallest_index != index:
                self.heap[index], self.heap[smallest_index] = self.heap[smallest_index], self.heap[index]
                index = smallest_index
            else:
                break

    def get_top_100(self):
        return sorted(self.heap[:self.size], key=lambda x: -x[-1])

# 初始化最小堆，用于存储最大的100个元组
min_heap = MinHeap()

# 模拟海量数据，数据是5元的元组，其中最后一个元素是排序标准
massive_data = [(1, 2, 3, 4, 1,10), (5, 6, 7, 8,1, 15), (9, 10, 11, 12,1, 5)]  # 你的数据集

# 找出最大的100个元组，按最后一个元素排序
for data in massive_data:
    min_heap.push(data)

result = min_heap.get_top_100()
print(result)
