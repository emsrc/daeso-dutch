"""
greedy binning (partitioning)
"""


def greedy_bin(objects, sizes, n=10):
    """
    Greedy binning of objects of different sizes into n bins of approximately
    equal size (aka the partitioning problem). 
    
    Returns a tuple of which the first element is a list of bin sizes and the
    second elements a list of bins, where each bin is a list of objects.
    """
    pairs = zip(sizes, objects)
    pairs.sort()
    
    bins = [ [0, []] for i in range(n) ]
    
    while pairs:
        size, obj = pairs.pop()
        smallest = bins[0]
        smallest[0] += size
        smallest[1].append(obj)
        bins.sort()
    
    return zip(*bins)
        
    
if __name__ == "__main__":    
    import random
    
    n_obj = 100
    objects = [ "e%d" % i for i in range(n_obj) ]
    sizes = [ random.randint(0, 1000) for i in range(n_obj) ]
    bin_sizes, bins = greedy_bin(objects, sizes)

    for s, b in zip(bin_sizes, bins):
        print "%4d%4d: %s" % (s, len(b), b)




