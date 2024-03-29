from heapq import heappush, heappop # for priority queue
import math
import time
import random

# Licensed by: http://code.activestate.com/recipes/tags/meta:license=mit/
# http://code.activestate.com/recipes/577519-a-star-shortest-path-algorithm/

class node:
    xPos = 0 # x position
    yPos = 0 # y position
    distance = 0 # total distance already travelled to reach the node
    priority = 0 # priority = distance + remaining distance estimate

    def __init__(self, xPos, yPos, distance, priority):
        self.xPos = xPos
        self.yPos = yPos
        self.distance = distance
        self.priority = priority
    def __lt__(self, other): # comparison method for priority queue
        return self.priority < other.priority
    def updatePriority(self, xDest, yDest,metric='Eucidian'):
# give higher priority to going straight instead of diagonally
        self.priority = self.distance + self.estimate(xDest, yDest,metric) * 10

    def nextMove(self, dirs, d): # d: direction to move
        if dirs == 8 and d % 2 != 0:
            self.distance += 14
        else:
            self.distance += 10
    # Estimation function for the remaining distance to the goal.

    def estimate(self, xDest, yDest,metric='Euclidian'):
        xd = xDest - self.xPos
        yd = yDest - self.yPos
        if metric == 'Euclidian':
            d = math.sqrt(xd * xd + yd * yd)
        elif metric == 'Manhattan':
            d = abs(xd) + abs(yd)
        elif metric == 'Chebyshev':
            d = max(abs(xd), abs(yd))
        else:
            raise()

        return(d)

# A-star algorithm.
# The path returned will be a string of digits of directions.

def pathFind(the_map, n, m, dirs, dx, dy, xA, yA, xB, yB,metric='Euclidian'):
    closed_nodes_map = [] # map of closed (tried-out) nodes
    open_nodes_map = [] # map of open (not-yet-tried) nodes
    dir_map = [] # map of dirs
    row = [0] * n
    for i in range(m): # create 2d arrays
        closed_nodes_map.append(list(row))
        open_nodes_map.append(list(row))
        dir_map.append(list(row))

    pq = [[], []] # priority queues of open (not-yet-tried) nodes
    pqi = 0 # priority queue index
    # create the start node and push into list of open nodes
    n0 = node(xA, yA, 0, 0)
    n0.updatePriority(xB, yB,metric)
    heappush(pq[pqi], n0)
    open_nodes_map[yA][xA] = n0.priority # mark it on the open nodes map
    # A* search
    while len(pq[pqi]) > 0:
        # get the current node w/ the highest priority
        # from the list of open nodes
        n1 = pq[pqi][0] # top node
        n0 = node(n1.xPos, n1.yPos, n1.distance, n1.priority)
        x = n0.xPos
        y = n0.yPos
        heappop(pq[pqi]) # remove the node from the open list
        open_nodes_map[y][x] = 0
        closed_nodes_map[y][x] = 1 # mark it on the closed nodes map
        # quit searching when the goal is reached
        # if n0.estimate(xB, yB) == 0:
        if x == xB and y == yB:
            # generate the path from finish to start
            # by following the dirs
            path = ''
            while not (x == xA and y == yA):
                j = dir_map[y][x]
                c = str((j + dirs / 2) % dirs)
                path = c + path
                x += dx[j]
                y += dy[j]
            return path

        # generate moves (child nodes) in all possible dirs
        for i in range(dirs):
            xdx = x + dx[i]
            ydy = y + dy[i]
            if not (xdx < 0 or xdx > n-1 or ydy < 0 or ydy > m - 1
                    or the_map[ydy][xdx] == 1 or closed_nodes_map[ydy][xdx] == 1):
                # generate a child node
                m0 = node(xdx, ydy, n0.distance, n0.priority)
                m0.nextMove(dirs, i)
                m0.updatePriority(xB, yB,metric)
                # if it is not in the open list then add into that
                if open_nodes_map[ydy][xdx] == 0:
                    open_nodes_map[ydy][xdx] = m0.priority
                    heappush(pq[pqi], m0)
                    # mark its parent node direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                elif open_nodes_map[ydy][xdx] > m0.priority:
                    # update the priority
                    open_nodes_map[ydy][xdx] = m0.priority
                    # update the parent direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                    # replace the node
                    # by emptying one pq to the other one
                    # except the node to be replaced will be ignored
                    # and the new node will be pushed in instead
                    while not (pq[pqi][0].xPos == xdx and pq[pqi][0].yPos == ydy):
                        heappush(pq[1 - pqi], pq[pqi][0])
                        heappop(pq[pqi])
                    heappop(pq[pqi]) # remove the target node
                    # empty the larger size priority queue to the smaller one
                    if len(pq[pqi]) > len(pq[1 - pqi]):
                        pqi = 1 - pqi
                    while len(pq[pqi]) > 0:
                        heappush(pq[1-pqi], pq[pqi][0])
                        heappop(pq[pqi])
                    pqi = 1 - pqi
                    heappush(pq[pqi], m0) # add the better node instead
    return '' # if no route found

def node_path(x_start=None,y_start=None,x_end=None,y_end=None,mask=None,dirs=4,metric='Manhattan',stagger='24'):

    """ start_x,start_y and end_x,end_y are the (integer) grid coordinates
        corresponding to the start and ending stations on a grid with
        shape(mask). Mask values of 0 correspond to valid nodes. Mask values
        of 1 are barriers.  """

    map = []
    n=mask.shape[1] # number of grid longitudes
    m=mask.shape[0] # number of grid latitudes
    # Create a map
    for i in range(m):
        row = mask[i,:].astype(int)
        map.append(list(row))

    if dirs == 4: # number of paths for motion (along C-grid faces)
        dx = [1,0,-1,0]
        dy = [0,1,0,-1]
    elif dirs == 8: # number of paths for motion (across corners)
        dx = [1, 1, 0, -1, -1, -1, 0, 1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
    else:
        print('dirs must be 4 or 8')
        return None

    route = pathFind(map,n,m,dirs,dx,dy,x_start,y_start,x_end,y_end,metric)

    path=[]

    if len(route) > 0:
        x = x_start
        y = y_start
        map[y][x] = 2

        if stagger=='24':
            path.append([y,x,0,0])
        for i in range(len(route)):
            j = int(route[i]) # not very pythonic here
            x += dx[j]
            y += dy[j]
            if dx[j] != 0 and dy[j] != 0:
                map[y][x] = 2
                path.append([y,x,dy[j],dx[j]])
#        map[y][x] = 2
#        path.append([y,x,0,0])

    return path,map
