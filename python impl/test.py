import pandas as pd
import numpy as np
from count_min import CountMinSketch
from pympler.classtracker import ClassTracker
from count_min import *

def load_data(file_name = 'Data/packet-trace.csv'):
    packet_trace = pd.read_csv(file_name)
    flow_grouped = packet_trace.groupby(['Source_IP','Destination_IP','Source_Port','Destination_Port','Protocol']).sum()
    return packet_trace,flow_grouped

def get_rand_flow(flow_grouped):
    ind = np.random.randint(flow_grouped.shape[0])
    flow_X = flow_grouped.index[ind]
    gt_freq = flow_grouped.iloc[ind]['flow_freq']
    return flow_X, gt_freq

if __name__ == "__main__":
    tracker = ClassTracker()
    tracker.track_class(CountMinSketch)

    print("Loading Data.....")
    packet_trace,flow_grouped = load_data()
    
    
    print("Initialising Sketch.....")
    """ YOUR CODE HERE
        TODO: Initialise the sketch with the required parameters
        Example:
            width = ...
            depth = ...
            data_type = ...
            sketch = CountMinSketch(width, depth, data_type)
    """
    sketch = CountMinSketch()

    tracker.create_snapshot("Sketch Initialised")

    #Updating sketch with all packets in trace
    print("Updating sketch with all packets in trace, this may take a while...")
    i = 0

    for row in packet_trace.itertuples(index=False):
        i += 1
        sketch.add_item(row[0:5],row[5])
        print("这是第{}条数据".format(i))
        if i%500000 == 0:
            print("Processed {:.2f}% of packets".format(i*100/packet_trace.shape[0]))
    tracker.create_snapshot("Sketch Updated with all packets")
    print("Sketch Updated with all packets")


    print("\n\n~~~~~~~Task I - Frequency Estimation~~~~~~~")
    # Estimating frequency of a Randomly chosen flow
    flow_X, gt_freq = get_rand_flow(flow_grouped)
    est_freq = sketch.estimate_frequency(flow_X)
    tracker.create_snapshot("Query I")

    print("Estimated frequency of flow :", est_freq)
    print("Actual frequency of flow :", gt_freq)
    

    print("\n\n~~~~~~~Task II - Cardinality Estimation~~~~~~~")
    # Estimating cardinality of the sketch
    cardinality = sketch.count_unique_flows()
    gt_cardinality = flow_grouped.shape[0]
    tracker.create_snapshot("Query II")

    print("Estimated cardinality of sketch :", cardinality)
    print("Actual cardinality of sketch :", gt_cardinality)

    print("\n\n~~~~~~~Task III - Heavy Hitter Detection~~~~~~~")
    # Finding heavy hitters
    heavy_hitters, heavy_hitters_size = sketch.find_heavy_hitters()
    tracker.create_snapshot("Query III")
    top_100 = flow_grouped.sort_values(by='frame.len', ascending=False).head(100)
    gt_heavy_hitters = top_100.index.to_list()
    print(top_100)
    gt_heavy_hitter_size = top_100['frame.len'].values
    
    print("Correctly identified heavy hitters (out of 100) :", len(set(top_100.index) & set(heavy_hitters)))

    print("\n\n~~~~~~~ Sketch Memory Usage Report~~~~~~~")
    tracker.create_snapshot("End of Script")
    tracker.stats.print_summary()
    tracker.stats.dump_stats('Data/class_profile.dat')