from simulator.node import Node
import json
import sys
#json.load(x)  x json -> dict
#json.dumps(x)  x dict -> jsonn


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.id = id #
        self.edges = [] #lof all edges
        self.weights = {} #weights keyed by edges
        self.nodes = [] #lof nodes to help with dijsktras
        self.seq = 0  

    # Return a string
    #can be mostly ignored, used for debugging
    def __str__(self):
        #return "Rewrite this function to define your node dump printout"
        res = ''
        for edge in self.edges: 
            res+="edge is " + str(edge)
        res+= "weeightss are" + str(self.weights)
        return res

    # Fill in this function
    # if a new link is added, update your graph, then create a message to update your neighbors
    def link_has_been_updated(self, neighbor, latency):
        #create an edge
        edge = frozenset({self.id, neighbor})
        if latency == -1 and edge in self.edges: #remove if you have to
            self.edges.remove(edge)
            del self.weights[edge]
            for node in edge:
                self.nodes.remove(node)
            return
        if edge not in self.edges: #else if its not already in the graph, add it
            self.edges.append(edge)
            for node in edge:
                self.nodes.append(node)
        self.weights[edge] = latency #update the cost if necessary
        message = {"src": self.id, "dest": neighbor, "cost": latency, "seq": self.seq} #send message
        self.send_to_neighbors(json.dumps(message))
        self.seq+=1 #increment number
        # latency = -1 if delete a link


    # Fill in this function
    #when you receive a message, only if its new: add to your graph, then send to all neighbors except the one you just got it for
    def process_incoming_routing_message(self, m):
        m = json.loads(m)
        if m["seq"] >= self.seq: #if the sequence number received is not less than your sequence number, indicating newness
            #store it in the graph
            edge = frozenset({m["src"], m["dest"] })
            self.edges.append(edge)
            self.nodes.append(m["src"])
            self.nodes.append(m["dest"])
            self.weights[edge] = m["cost"]
            #send to all neighbors except who you recceived it 
            for edge in self.edges: #all edges
                if self.id in edge: #only your specific edges
                    for v in edge: #
                        if v != self.id and v != m["src"]: #find the node that isn't you, and isn't the node you received this message from
                            self.send_to_neighbor(v, json.dumps(m)) #retransmit the message



    # Return a neighbor, -1 if no path to destination
    #****Tested and working the below code runs dijkstras properly
    def get_next_hop(self, destination):
        #dijkstras
        dist = {}
        prev = {}
        for edge in self.edges:
            for v in edge:
                dist[v] = sys.maxsize
                prev[v] = None
        dist[id] = 0
        Q = self.nodes.copy()
        
        while len(Q) > 0:
            u = self.get_min_vertex(Q, dist) #gets the vertex u in the Q with min dist[u]
            Q.remove(u)

            for edge in self.edges: #for each edge
                if u in edge: #allows you to access only neighbors of u
                    alt = dist[u] + self.weights[edge]
                    for v in edge: 
                        if v != u: #since we're using a set, how you access the node u is connected to (v)
                            if alt < dist[v]:
                                dist[v] = alt
                                prev[v] = u
        
        try:
            #back track from destination till you get to the hop that comes right after the source
            res = destination
            while res != None and prev[res] and prev[res] != id:
                res = prev[res]
            return res
        except:
            return -1
        


    def get_min_vertex(self, loNodes, dist):
        min = sys.maxsize
        minNode = loNodes[0]
        for node in loNodes:
            if dist[node] < min:
                min = dist[node]
                minNode = node      
        return minNode
    