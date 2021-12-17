import random
from typing import List, Dict
import json
import heapq

data_copy = {}

def find_obstacles(data):
    obstacles= []
    #for coor in data["you"]["body"]:
    #  obstacles.append(coor)

    for snake in data["board"]["snakes"]:
        for coor in snake["body"]:
            obstacles.append(coor)
            
    return obstacles



def is_valid_move(data, obstacles, proposed_move):
    """Function that validates if we can perform given action without hitting wall, self, or other snake"""

    if proposed_move["x"]<0 or proposed_move["y"]<0:
        return False

    board_height = data["board"]["height"]
    board_width = data["board"]["width"]

    if proposed_move["x"]==board_width or proposed_move["y"]==board_height:
        return False

    if proposed_move in obstacles:
        return False
    return True

class GameNode:
    """
    Class GameNode: Provides a structure for performing A* search in snake Game
    """
    def __init__(self, head, body, last_action=None,
                 parent=None, real_cost=0, h_cost=None):
        """
        Initialization for parameters that we will need during our A* search
        
        """
        self.head = head
        self.body = body

        
        self.parent = parent
        self.real_cost = real_cost
        self.heuristic_cost = h_cost
        self.last_action = last_action


    def __repr__(self):
        return self.body.__repr__()

    def __str__(self):
        """More accurate and robust representation of Puzzle Node"""
        return self.body.__repr__()

    def __hash__(self):
        """
        Making our state hashable, so we can store it in the dictionary
        based on just state.
        
        PLEASE NOTE that we are not taking into account the cost.
        This allows us to make the comparison only based on states. It is
        easier for cases when we are comparing uniqness in dictionaries and
        sets.
        """
        return hash(json.dumps(tuple(self.body)))

    def __lt__(self, other):
        """
        Assuming we are planning to use a heap to save the nodes in the
        Frontier. Heap allows us to be able to pop elements in required order
        with minimal computational complexity"""
        return self.get_cost() < other.get_cost()

    def __eq__(self, other):
        """Similar as __hash__
        
        PLEASE NOTE that we are not taking into account the cost.
        This allows us to make the comparison only based on states. It is
        easier for cases when we are comparing uniqness in dictionaries and
        sets.
        """
        if not isinstance(other, type(self)): return NotImplemented
        return hash(self) == hash(other)
    
    def get_cost(self):
        """
        Computes the estimated cost of reaching 
        """
        if self.heuristic_cost is None:
            raise ValueError("Heuristic cost is not defined.")
        
        return self.heuristic_cost + self.real_cost
    
    def generate_successors(self):
        """
        Generates successor states, avoids state that looks like parent
        """
        global obstacles
        # There are 4 possible movements in general
        successors_positions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        successors_actions   = ["left","right","down","up"]
        successors = []
        for i,pos in enumerate(successors_positions):
            
            
            proposed_coor = {"x":self.head["x"]+pos[0],
                             "y":self.head["y"]+pos[1]}
            if is_valid_move(data_copy, obstacles, proposed_coor):
                new_head = proposed_coor
                new_body = [proposed_coor] + self.body[:-1]
                
                node = GameNode(new_head,new_body, parent=self,
                                real_cost=self.real_cost + 1,
                               last_action=successors_actions[i])
                
                if hash(self.parent) != hash(node):
                    successors.append(node)
        return successors

# Distance from the food source heuristic

def h1(node):
    """
    This function returns the distance towards nearest food, if there is 
    no food available, return 9999
    """
    shortest_distance = 9999


    for food in data_copy["board"]["food"]:
        distance = abs(food["x"]-node.head["x"])+abs(food["y"]-node.head["y"])
        if distance < shortest_distance:
            shortest_distance = distance
    return shortest_distance




def findFood(state, heuristic):
    """This function finds the path to food source in snake game.
    Inputs:
        -state: The initial state of the puzzle as a list of lists
        -heuristic: a handle to a heuristic function.  Will be one of those defined in Question 2.
    Outputs:
        -steps: The number of steps to optimally solve the puzzle (excluding the initial state)
        -exp: The number of nodes expanded to reach the solution
        -max_frontier: The maximum size of the frontier over the whole search
        -opt_path: The optimal path as a list of list of lists.  That is, opt_path[:,:,i] should give a list of lists
                    that represents the state of the board at the ith step of the solution.
        -err: An error code.  If state is not of the appropriate size and dimension, return -1.  For the extention task,
          if the state is not solvable, then return -2
    """
    heuriscics_cache = {}
    def add_to_forntier(node):
        """
        Helper function that:
        - calculates the heuristics costs
        - manages the cache of the heuristics
        - adds to frontier
        
        Note: Sorry for typo in function name, it should be frontier
        """
        global heuristic_cache
        # If we have seen the state before
        if node in heuriscics_cache[heuristic]:
            # use the value from cache
            h_cost = heuriscics_cache[heuristic][node]
        else:
            # calculate the new value and save it in cache
            h_cost = heuristic(node)
            heuriscics_cache[heuristic][node] = h_cost
            
        node.heuristic_cost = h_cost
        heapq.heappush(frontier, node)
    
    # Let´s go solving
    # Make sure our heuristic cache knows the heuristic algorithm
    global heuristic_cache
    if not heuristic in heuriscics_cache:
        heuriscics_cache[heuristic] = {}
        
    # Definiting variables needed for solving
    expanded = 0
    steps = -1
    
    # I Prefered set, but dictionary allows us to lookup the value too
    visited = {}
    frontier = []  # Heap
    frontier_history=[]
    
    # Calculate the final state, that we want to reach
    # Note that for comparison, the flattned version is completely enough
    FINAL = data_copy["board"]["food"]

    # We start with initial state in our frontier
    # Frontier is a heap that alwas pops the node with smallest cost
    add_to_forntier(state)

    
    emergency_brake = 0
    while frontier:
        # Emergency stop to avoid going over the time limit
        emergency_brake +=1
            
        # Update stats
        frontier_history.append(len(frontier))
        steps += 1
        
        current_node = heapq.heappop(frontier)

        # Check if we reached the final node:
        if current_node.head in FINAL or emergency_brake > 2500:
            
            # Yay we reached the end
            # Return all interesting variables
            # trace back to the top
            path = []
            
            # We go backwards to find the optimal path that we found
            node =current_node
            while node.parent:
                path.append(node)
                node = node.parent
                
            # We should also include the start state
            path.append(node)
            
            return len(path)-1, expanded, max(frontier_history), path[::-1], emergency_brake

        # Else we continue procedure of adding
        visited[current_node] = current_node

        # Ok, there is nothing else that we can do except hoping that next
        # generation of kids gets closer to the goal :)
        expanded += 1
        for node in current_node.generate_successors():

            if node in visited:
                # We compare if we found the node with less real cost and if
                # yes, we add it to forntier otherwise, lets just prune it 
                if node.real_cost < visited[node].real_cost:
                    # Let´s be honest, it never happens in case of 8-puzzle
                    # But it could happen in more advanced search space
                    # like Romanian map from our classes
                    print("Fancyyyyyy")
                    
                else:
                    # we are not interested, let´s try other child
                    continue
            add_to_forntier(node)

    return None, None, None, None, -1


def find_snakes_around(coor, previous_coor):
    """Identifies enemy snakes that can reach the point"""
    global data_copy
    threads = []
    for snake in data_copy["board"]["snakes"]:
        other  = snake["head"]
        me = coor
        # We are also appearing in list of snakes
        if other != previous_coor:
            if abs(other["x"]-coor["x"]) + abs(other["y"]-coor["y"]) ==1:
                # High risk of colision
                if len(snake["body"]) < len(data_copy["you"]["body"]):
                    # Snake is smaler, we do not care.
                    pass
                else:
                    # Snake is equal or larger, we really do care
                    # lets run away
                    # Is the enemy snake interested in going here?
                    start_state = GameNode(snake["head"], snake["body"], )

                    a, b, c, d, e = findFood(start_state, h1)
                    if coor == d[1].head:
                        # There is going to be serious colission
                        threads.append(coor)

    return threads




def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    global data_copy
    data_copy = data
    print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    print(f"All board data this turn: {data}")
    global obstacles
    obstacles = find_obstacles(data)

    start_state = GameNode(data["you"]["head"],data["you"]["body"],)

    if len(data["board"]["food"])==0:
        #There is no food there si nothing else to do
        return random.choice(start_state.generate_successors()).last_action

    a1,b1,c1,d1,e1 = findFood(start_state, h1)
    print("A-star STATS:",a1,b1,c1,e1)
    if d1 is None:
        # there is not much we can do, brace for impact and go in random direction
        return random.choice(start_state.generate_successors()).last_action
    else:
        try:
            threads = find_snakes_around(d1[1].head, data["you"]["head"])
            if threads:
                obstacles = obstacles + threads
                start_state = GameNode(data["you"]["head"], data["you"]["body"], )
                a, b, c, d, e = findFood(start_state, h1)
                print("A-star STATS:", a, b, c, e)
        except:
            pass
    try:

        return d1[1].last_action
    except IndexError:
        return random.choice(start_state.generate_successors()).last_action
