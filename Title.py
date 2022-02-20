class Title:
    def __init__(self) -> None:
        pass
    def setScannerName(self, _scanner_name):
        self.scanner_name = _scanner_name
    def setTreeName(self, _tree_name):
        self.tree_name = _tree_name
    def setRangeBudgetSeedn(self, range, budget, seedn):
        self.range = range
        self.budget = budget
        self.seedn = seedn
    def getTitle(self):
        """scannername + treename + range of random + budget + number of seed
            eg: ZMap_Echo_Tree_6hit_1000000_50000_5000_
        """
        return "{}_{}_{}_{}_{}_".format(self.scanner_name, self.tree_name, self.range, self.budget, self.seedn)
