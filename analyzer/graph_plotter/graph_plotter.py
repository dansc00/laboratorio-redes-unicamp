import matplotlib.pyplot as plt
from enum import Enum
import sys

# colors supported by matplotlib (except white)
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
    CYAN = "cyan"
    MAGENTA = "magenta"
    PINK = "pink"
    BROWN = "brown"
    LIME = "lime"
    NAVY = "navy"
    GOLD = "gold"
    SILVER = "silver"
    TEAL = "teal"

    ALICEBLUE = "aliceblue"
    ANTIQUEWHITE = "antiquewhite"
    AQUA = "aqua"
    AQUAMARINE = "aquamarine"
    AZURE = "azure"
    BEIGE = "beige"
    BISQUE = "bisque"
    BLANCHEDALMOND = "blanchedalmond"
    BLUEVIOLET = "blueviolet"
    BURLYWOOD = "burlywood"
    CADETBLUE = "cadetblue"
    CHARTREUSE = "chartreuse"
    CHOCOLATE = "chocolate"
    CORAL = "coral"
    CORNFLOWERBLUE = "cornflowerblue"
    CORNSILK = "cornsilk"
    CRIMSON = "crimson"
    DARKBLUE = "darkblue"
    DARKCYAN = "darkcyan"
    DARKGOLDENROD = "darkgoldenrod"
    DARKGRAY = "darkgray"
    DARKGREEN = "darkgreen"
    DARKKHAKI = "darkkhaki"
    DARKMAGENTA = "darkmagenta"
    DARKOLIVEGREEN = "darkolivegreen"
    DARKORANGE = "darkorange"
    DARKORCHID = "darkorchid"
    DARKRED = "darkred"
    DARKSALMON = "darksalmon"
    DARKSEAGREEN = "darkseagreen"
    DARKSLATEBLUE = "darkslateblue"
    DARKSLATEGRAY = "darkslategray"
    DARKTURQUOISE = "darkturquoise"
    DARKVIOLET = "darkviolet"
    DEEPPINK = "deeppink"
    DEEPSKYBLUE = "deepskyblue"
    DIMGRAY = "dimgray"
    DODGERBLUE = "dodgerblue"
    FIREBRICK = "firebrick"
    FLORALWHITE = "floralwhite"
    FORESTGREEN = "forestgreen"
    FUCHSIA = "fuchsia"
    GAINSBORO = "gainsboro"
    GHOSTWHITE = "ghostwhite"
    GOLDENROD = "goldenrod"
    GREENYELLOW = "greenyellow"
    HONEYDEW = "honeydew"
    HOTPINK = "hotpink"
    INDIANRED = "indianred"
    INDIGO = "indigo"
    IVORY = "ivory"
    KHAKI = "khaki"
    LAVENDER = "lavender"
    LAVENDERBLUSH = "lavenderblush"
    LAWNGREEN = "lawngreen"
    LEMONCHIFFON = "lemonchiffon"
    LIGHTBLUE = "lightblue"
    LIGHTCORAL = "lightcoral"
    LIGHTCYAN = "lightcyan"
    LIGHTGOLDENRODYELLOW = "lightgoldenrodyellow"
    LIGHTGRAY = "lightgray"
    LIGHTGREEN = "lightgreen"
    LIGHTPINK = "lightpink"
    LIGHTSALMON = "lightsalmon"
    LIGHTSEAGREEN = "lightseagreen"
    LIGHTSKYBLUE = "lightskyblue"
    LIGHTSLATEGRAY = "lightslategray"
    LIGHTSTEELBLUE = "lightsteelblue"
    LIGHTYELLOW = "lightyellow"
    LIMEGREEN = "limegreen"
    LINEN = "linen"
    MAROON = "maroon"
    MEDIUMAQUAMARINE = "mediumaquamarine"
    MEDIUMBLUE = "mediumblue"
    MEDIUMORCHID = "mediumorchid"
    MEDIUMPURPLE = "mediumpurple"
    MEDIUMSEAGREEN = "mediumseagreen"
    MEDIUMSLATEBLUE = "mediumslateblue"
    MEDIUMSPRINGGREEN = "mediumspringgreen"
    MEDIUMTURQUOISE = "mediumturquoise"
    MEDIUMVIOLETRED = "mediumvioletred"
    MIDNIGHTBLUE = "midnightblue"
    MINTCREAM = "mintcream"
    MISTYROSE = "mistyrose"
    MOCCASIN = "moccasin"
    NAVAJOWHITE = "navajowhite"
    OLDLACE = "oldlace"
    OLIVE = "olive"
    OLIVEDRAB = "olivedrab"
    ORANGERED = "orangered"
    ORCHID = "orchid"
    PALEGOLDENROD = "palegoldenrod"
    PALEGREEN = "palegreen"
    PALETURQUOISE = "paleturquoise"
    PALEVIOLETRED = "palevioletred"
    PAPAYAWHIP = "papayawhip"
    PEACHPUFF = "peachpuff"
    PERU = "peru"
    PLUM = "plum"
    POWDERBLUE = "powderblue"
    REBECCAPURPLE = "rebeccapurple"
    ROSYBROWN = "rosybrown"
    ROYALBLUE = "royalblue"
    SADDLEBROWN = "saddlebrown"
    SALMON = "salmon"
    SANDYBROWN = "sandybrown"
    SEAGREEN = "seagreen"
    SEASHELL = "seashell"
    SIENNA = "sienna"
    SLATEBLUE = "slateblue"
    SLATEGRAY = "slategray"
    SNOW = "snow"
    SPRINGGREEN = "springgreen"
    STEELBLUE = "steelblue"
    TAN = "tan"
    THISTLE = "thistle"
    TOMATO = "tomato"
    TURQUOISE = "turquoise"
    VIOLET = "violet"
    WHEAT = "wheat"
    WHITESMOKE = "whitesmoke"
    YELLOWGREEN = "yellowgreen"

# plot graphs using matplotlib
class GraphPlotter:

    def __init__(self, title=None, xLabel=None, yLabel=None, grid=True, legendFlag=True, legendPosition=None, colors=[], plotCount=0):
        self.title = title # graph title
        self.xLabel = xLabel # axis x label
        self.yLabel = yLabel # axis y label
        self.grid = grid # graph grid option
        self.legendFlag = legendFlag # graph legend option
        self.legendPosition = legendPosition # legend position option (right, bottom, left)
        self.colors = colors if colors else list(Color) # colors input or list of Color enum
        self.plotCount = plotCount # number of plots
        self.fig, self.axis = plt.subplots() # subplots objects for each instance, avoid error using plt global 
    
    # get color from Color enum or color passed by argument
    def getColor(self, color=None, i=0):

        if color is None:
            enumColor = self.colors[i % len(self.colors)] # choose another color
            colorValue = enumColor.value
        else:
            colorValue = color.value if isinstance(color, Color) else color
        
        return colorValue

    def showGraph(self):

        if self.legendFlag == True:
            if self.legendPosition == "right":
                self.axis.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                self.fig.tight_layout()

            elif self.legendPosition == "bottom":
                self.axis.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
                self.fig.tight_layout()

            elif self.legendPosition == "left":
                self.axis.legend(loc='center right', bbox_to_anchor=(-0.1, 0.5))
                self.fig.tight_layout()

            else:
                self.axis.legend()

        plt.show()

    def saveGraph(self, filename="graph.png", dpi=300, bbox_inches="tight"):
        
        if self.legendFlag == True:
            if self.legendPosition == "right":
                self.axis.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                self.fig.tight_layout()

            elif self.legendPosition == "bottom":
                self.axis.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1))
                self.fig.tight_layout()

            elif self.legendPosition == "left":
                self.axis.legend(loc='center right', bbox_to_anchor=(-0.1, 0.5))
                self.fig.tight_layout()
                
            else:
                self.axis.legend()

        try:
            self.fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        except Exception as e:
            print(f"Error saving graph: {e}")

    # plot using object attributes or method arguments 
    def plotLineGraph(self, x, y, color=None, plotLabel=None, xLabel=None, yLabel=None, title=None, grid=None, marker="o", linestyle="-", autoScaleY=False, 
                      autoScaleX=False, yScaleFactor=3, xScaleFactor=3, yScaleStart=0, xScaleStart=0, yScale="linear", xScale="linear", base=10):

        color = self.getColor(color, self.plotCount)
        self.plotCount += 1

        self.axis.plot(x, y, color=color, label=plotLabel, marker=marker, linestyle=linestyle)

        self.axis.set_xlabel(xLabel or self.xLabel)
        self.axis.set_ylabel(yLabel or self.yLabel)
        self.axis.set_title(title or self.title)
        self.axis.grid(self.grid if grid is None else grid)

        # adjustment type of scale
        if yScale == "log":
            self.axis.set_yscale(yScale, base=base)
        
        if xScale == "log":
            self.axis.set_xscale(xScale, base=base)

        # automatic scale adjustment, to better visualization of the graph
        if autoScaleY and len(y) > 0:
            yMean = sum(y) / len(y)
            self.axis.set_ylim(yScaleStart, yMean * yScaleFactor)

        if autoScaleX and len(x) > 0:
            xMean = sum(x) / len(x)
            self.axis.set_xlim(xScaleStart, xMean * xScaleFactor)

    def plotBarGraph(self, x, y, color=None, plotLabel=None, xLabel=None, yLabel=None, title=None, grid=None, align="center", edgecolor="black", horizontal=False):

        self.plotCount += 1

        if isinstance(color, list) and isinstance(plotLabel, list):
            for i in range(len(x)):
                barColor = self.getColor(color[i], self.plotCount) if isinstance(color[i], (Color, str)) else self.getColor(None, self.plotCount)

                if horizontal:
                    self.axis.barh(x[i], y[i], color=barColor, label=None, align=align, edgecolor=edgecolor)
                else:
                    self.axis.bar(x[i], y[i], color=barColor, label=plotLabel[i], align=align, edgecolor=edgecolor)

        else:
            barColor = [self.getColor(color, i) for i in range(len(x))]

            if horizontal:
                self.axis.barh(x, y, color=barColor, label=None, align=align, edgecolor=edgecolor)
            else:
                self.axis.bar(x, y, color=barColor, label=plotLabel, align=align, edgecolor=edgecolor)

        self.axis.set_xlabel(xLabel or self.xLabel)
        self.axis.set_ylabel(yLabel or self.yLabel)
        self.axis.set_title(title or self.title)
        self.axis.grid(self.grid if grid is None else grid)

    def plotPizzaGraph(self, labels, sizes, colors=None, explode=None, startangle=90, autopct='%1.1f%%', shadow=False):

        if colors is None:
            colors = [self.getColor(None, i) for i in range(len(labels))]

        self.axis.clear()
        self.axis.pie(sizes, labels=labels, colors=colors, explode=explode, startangle=startangle, autopct=autopct, shadow=shadow)
        self.axis.set_title(self.title or "")
        self.axis.axis('equal')  # circle

    def plotHistogram(self, data, bins=10, color=None, plotLabel=None, xLabel=None, yLabel=None, title=None, grid=None, edgecolor="black", density=False, histtype="bar"):

        color = self.getColor(color, self.plotCount)
        self.plotCount += 1

        self.axis.hist(data, bins, color=color, label=plotLabel, edgecolor=edgecolor, density=density, histtype=histtype)

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

            self.plotLineGraph(xData, yData, color=plotColor, plotLabel=plotLabel, xLabel=self.xLabel, yLabel=self.yLabel, title=self.title)  
            
        self.showGraph()       

if __name__ == "__main__":

    plot = GraphPlotter()
    plot.plotUserInput()
