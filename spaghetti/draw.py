import networkx
import os
import time
import matplotlib.pyplot as plt
from spaghetti.state import Mode


# Creates an image of the supplied Networkx graph and saves it to a relative folder
def draw_graph(nxg, title, mode=Mode.NORMAL):
    if mode is Mode.SIMPLE:
        node_size = 400
        width = 4
        font_size = 20
    else:
        plt.title(title)
        node_size = 75
        width = 2
        font_size = 10

    # pos = networkx.spectral_layout(nxg)  # More symmetrical but can't handle larger graphs well
    pos = networkx.spring_layout(nxg, k=3)
    networkx.draw_networkx_nodes(nxg, pos, node_size=node_size)
    networkx.draw_networkx_edges(nxg, pos, edge_color='blue', arrowsize=40, width=width)
    description = networkx.draw_networkx_labels(nxg, pos, font_size=font_size, font_family='sans-serif',
                                                font_weight='bold')
    # Prevents label text from being obstructed
    for node, t in description.items():
        t.set_clip_on(False)

    # Creates a relative directory if it does not already exist
    directory = "dependency_graphs"
    if not os.path.isdir(directory):
        os.mkdir(directory)

    # Saves the image to a file
    filename = "graph_" + repr(time.time()) + ".png"
    plt.axis('off')
    plt.savefig(directory + os.sep + filename)
