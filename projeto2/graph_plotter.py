import matplotlib.pyplot as plt
from enum import Enum
import sys

# colors
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    PURPLE = "purple"
    BLACK = "black"
    GRAY = "gray"
    ORANGE = "orange"
    SKY = "skyblue"
    WHITE = "white"
    CYAN = "cyan"
    MAGENTA = "magenta"

# plot graphs
class GraphPlotter:

    def __init__(self, title=None, xLabel=None, yLabel=None, grid=True, legendFlag=True, colors=[], plotCount=0):
        self.title = title # graph title
        self.xLabel = xLabel # axis x label
        self.yLabel = yLabel # axis y label
        self.grid = grid # graph grid option
        self.legendFlag = legendFlag # graph legend option
        self.colors = colors if colors else list(Color) # list of Color enum
        self.plotCount = plotCount # number of plots
        self.fig, self.axis = plt.subplots() 
    
    # get color from Color enum
    def getColor(self, color):

        if color is None:
            enumColor = self.colors[self.plotCount % len(self.colors)]
            colorValue = enumColor.value
        else:
            colorValue = color.value if isinstance(color, Color) else color
        
        return colorValue

    def showGraph(self):

        if self.legendFlag == True:
            self.axis.legend() 
        plt.show()

    def saveGraph(self, filename="graph.png", dpi=300, bbox_inches="tight"):
  
        try:
            self.fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        except Exception as e:
            print(f"Error saving graph: {e}")

    # plot using object attributes or method arguments 
    def plotLineGraph(self, x, y, color=None, plotLabel=None, xLabel=None, yLabel=None, title=None, grid=None, marker='o', linestyle='-'):

        color = self.getColor(color)
        self.plotCount += 1

        self.axis.plot(x, y, marker=marker, linestyle=linestyle, color=color, label=plotLabel)

        self.axis.set_xlabel(xLabel or self.xLabel)
        self.axis.set_ylabel(yLabel or self.yLabel)
        self.axis.set_title(title or self.title)
        self.axis.grid(self.grid if grid is None else grid)

    # custom user input plot
    def plotUserInput(self):

        try:
            nPlots = int(input("Number of plots: "))
            self.xLabel = input("x label: ")
            self.yLabel = input("y label: ")
            self.title = input("Graph title: \n")
        
        except ValueError:
            print("Invalid input")
            sys.exit(1)

        # input axis data
        for i in range(nPlots):
            print(f"Plot{i+1}: ")
            try:
                xData = list((map(float, input("x data (a b c ...): ").split())))
                yData = list((map(float, input("y data (a b c ...): ").split())))
            
            except ValueError:
                print("Invalid input")
                sys.exit(1)

            # color select
            plotColor = None
            colorInput = input(f"Plot {i+1} color (red, blue, etc. Leave empty for auto): ").upper().strip()
            if colorInput:
                if colorInput in Color.__members__:
                    plotColor = Color[colorInput]
                else:
                    print("Invalid color. Using auto-color.")

            # line label
            plotLabel = input(f"Plot {i+1} label: ")

            self.plotLineGraph(xData, yData, plotColor, plotLabel, self.xLabel, self.yLabel, self.title)  
            
        self.showGraph()       

if __name__ == "__main__":

    plt = GraphPlotter()
    plt.plotUserInput()