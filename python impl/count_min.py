""" CS5229 Programming Assignment 1: 
    Sketch-based Network Monitoring

Name: ye wen
Email: wen_ye@u.nus.edu
Student ID: A0276607W
"""

import numpy as np
from pympler import asizeof

class CountMinSketch:
    def __init__(self): #Allowed to add initialization parameters
        """Initialise the sketch. You may add additional variables to the function call.

            self.sketch: Variable to store the sketch
            self.auxiliary_storage: Additional auxiliary storage (optional)
        """

        ## sketch is a 200000 * 3 list

        self.sketch = [[0] * 200000 for i in range(3)]
        self.sketch = np.array(self.sketch, dtype=np.uint8)
        ## store top 80
        self.auxiliary_storage = dict()   # Variable to store heavy hitters (optional)





    def hash_func(self, packet_flow, i = None):
        """Function handles the hashing functionality for the sketch

        Args:
            packet_flow: Tuple of (Source_IP, Destination_IP, Source_Port, Destination_Port, Protocol)
            i (optional): Optional arguement to specify the hash function ID to be used. Defaults to None.

        Returns:
            Hashed value of the packet_flow
        """

        """ YOUR CODE HERE
        TODO: Implement the hash functions
        """
        if i == None:
        ## change 5-tuple to string
            str_prehash = str(packet_flow)
            hash_val = hash(str_prehash)
            col_index = hash_val % 200000
            row_index = (hash_val // 200000) % 3
            return row_index, col_index

        ## another method of hash(change the order of tuple
        if i == 1:
            str_prehash = str( (packet_flow[2],packet_flow[3],packet_flow[4],packet_flow[1],packet_flow[0]))
            letter1 = "cs5223"
            letter2 = "5223cs"
            str_prehash = str_prehash[:2] + letter1 + str_prehash[2:]
            str_prehash = str_prehash[:14] + letter2 + str_prehash[14:]
            hash_val = hash(str_prehash)
            col_index = hash_val % 200000
            row_index = (hash_val // 200000) % 3
            return row_index, col_index
        if i  == 2:
            str_prehash = str((packet_flow[3], packet_flow[4], packet_flow[0], packet_flow[1], packet_flow[2]))
            letter1 = "it5221"
            letter2 = "5221it"
            str_prehash = str_prehash[:2] + letter1 + str_prehash[2:]
            str_prehash = str_prehash[:14] + letter2 + str_prehash[14:]
            hash_val = hash(str_prehash)
            col_index = hash_val % 200000
            row_index = (hash_val // 200000) % 3
            return row_index, col_index



        return 0    #Return the hashed value of the packet_flow
    
    def add_item(self, packet_flow, packet_len):
        """ Update sketch for the current packet in stream

        Args:
            packet_flow : Tuple of (Source_IP, Destination_IP, Source_Port, Destination_Port, Protocol)
            packet_len: Integer value of packet length
        """
        """ YOUR CODE HERE
        TODO: Implement the sketch update algorithm
        """

        ## if the packet is a large flow, sperate it to auxiliary_storage
        if len(self.auxiliary_storage) < 800 and packet_flow not in self.auxiliary_storage:
            ## insert flow to auxiliary
            self.auxiliary_storage[packet_flow] = 1
        elif packet_flow in self.auxiliary_storage:
            self.auxiliary_storage[packet_flow] += 1
        elif len(self.auxiliary_storage) >= 800 and packet_flow not in self.auxiliary_storage:
            ## if we want to add data to the sketch
            ## 3 times hash and add 3 counter
            row1, col1 = self.hash_func(packet_flow)
            self.sketch[row1][col1] = self.sketch[row1][col1] + 1
            row2, col2 = self.hash_func(packet_flow, i=1)
            self.sketch[row2][col2] = self.sketch[row2][col2] + 1
            row3, col3 = self.hash_func(packet_flow, i=2)
            self.sketch[row3][col3] = self.sketch[row3][col3] + 1

            ## update
            frequency = list()
            frequency.append(self.sketch[row1][col1])
            frequency.append(self.sketch[row2][col2])
            frequency.append(self.sketch[row3][col3])
            flow_freq = min(frequency)
            min_val = min(self.auxiliary_storage.values())
            min_key = [key for key, value in self.auxiliary_storage.items() if value == min_val][0]

            if min_val <= flow_freq:
                del self.auxiliary_storage[min_key]
                self.auxiliary_storage[packet_flow] = flow_freq

                self.sketch[row1][col1] = self.sketch[row1][col1] - flow_freq
                self.sketch[row2][col2] = self.sketch[row2][col2] - flow_freq
                self.sketch[row3][col3] = self.sketch[row3][col3] - flow_freq
                row1, col1 = self.hash_func(min_key)
                self.sketch[row1][col1] = self.sketch[row1][col1] + min_val
                row2, col2 = self.hash_func(min_key, i=1)
                self.sketch[row2][col2] = self.sketch[row2][col2] + min_val
                row3, col3 = self.hash_func(min_key, i=2)
                self.sketch[row3][col3] = self.sketch[row3][col3] + min_val



            ## change position



    def estimate_frequency(self, flow_X):
        """Estimate the frequency of flow_X using the sketch

        Args:
            flow_X: Tuple of (Source_IP, Destination_IP, Source_Port, Destination_Port, Protocol)

        Returns:
            Observed frequency of flow_X
        """

        ###### Task I - Freuqency Estimation ######
        flow_freq = 0 

        """ YOUR CODE HERE
        TODO: Implement the frequency estimation algorithm
        """
        ## obtain the frequency
        frequency = list()
        row1, col1 = self.hash_func(flow_X)
        row2, col2 = self.hash_func(flow_X, i=1)
        row3, col3 = self.hash_func(flow_X, i=2)
        frequency.append(self.sketch[row1][col1])
        frequency.append(self.sketch[row2][col2])
        frequency.append(self.sketch[row3][col3])
        flow_freq = min(frequency)
        if flow_X in self.auxiliary_storage:
            flow_freq = self.auxiliary_storage[flow_X]


        return flow_freq 
    
    def count_unique_flows(self):
        """ Estimate the number of unique flows(Cardinality) using the sketch

        Returns:
            Cardinality of the packet trace
        """

        ###### Task II - Cardinality Estimation ######
        num_unique_flows = 0
        sum_zeros = 0
        # sum zero leaf
        for number in self.sketch[0]:
            if number == 0:
                sum_zeros = sum_zeros + 1
        sum_zero = sum_zeros
        len = 200000
        result = 0
        x = sum_zero / len
        ## calculate log
        for n in range(1, 1001):
            result += ((-1) ** (n + 1)) * (x - 1) ** n / n
        num_unique_flows = -1 * len * result
        return num_unique_flows







        """ YOUR CODE HERE
        TODO: Implement the cardinality estimation algorithm
        """

    
    def find_heavy_hitters(self):
        """ Find the heavy hitters using the sketch

        Returns:
            heavy_hitters: 5-Tuples representing the heavy hitter flows
            heavy_hitters_size: Sizes of the heavy hitter flows
        """
        ###### Task III - Heavy Hitter Detection ######
        heavy_hitters = []  # List to store heavy hitter flows
        heavy_hitters_size = []  # List to store heavy hitter sizes

        """ YOUR CODE HERE
        TODO: Implement the heavy hitter detection algorithm
        """
        self.auxiliary_storage = dict(sorted(self.auxiliary_storage.items(), key=lambda item: item[1], reverse=True ))
        #obtain top 100
        heavy_hitters_size = [value for key, value in self.auxiliary_storage.items()][:100]
        heavy_hitters = [key for key, value in self.auxiliary_storage.items()][:100]

        return heavy_hitters, heavy_hitters_size

