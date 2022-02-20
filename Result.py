
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import Counter





from utility import sort_dict
from utility import my_plot
from logger import MyLog

class Results(object):
    def __init__(self):
        self.hitrates = []
        self.iter_hitrates = []
        self.iter_findrates = []
        self.final_hitrate = 0
    
    def set_title(self, title):
        self.title = title

    def plot(self):
        my_plot(self.title, self.hitrates, self.iter_hitrates, self.iter_findrates)

