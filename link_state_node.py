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
        self.seq = {}
        self.lastMsgs ={}
        self.nodes = [id] #lof nodes to help with dijsktras

    # Return a string
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
        edge = frozenset({self.id, neighbor})
        time = self.get_time()
        self.seq[edge] = time
        if latency == -1 and edge in self.edges: #remove the edge if you have to
            self.edges.remove(edge)
            del self.weights[edge]
            del self.seq[edge]
            del self.lastMsgs[edge]
            self.nodes.remove(neighbor)
        else: 
            if edge not in self.edges: #else if its not already in the graph, add it
                self.edges.append(edge)
                self.nodes.append(neighbor)
                for key, value in self.lastMsgs.items(): #since its a new node, update it with all your recent messaages
                    self.send_to_neighbor(neighbor, value)
            
            self.weights[edge] = latency #update the cost

        #retransmit all your most recent messages from each node - do this because a new node doesn't have information about the graphh so it needs it
        #also send along this new message 
        message = json.dumps({"src": self.id, "dest": neighbor, "cost": latency, "seq": time}) #send message
        self.send_to_neighbors(message)
        self.lastMsgs[edge] = message
        



    # Fill in this function
    #if you get an old message, get your neighbors up to date
    #else either add this new connection, or update, and retransmit to your neighbors
    def process_incoming_routing_message(self, m):
        m = json.loads(m)
        edge = frozenset({m["src"], m["dest"] })
        if edge not in self.seq or m["seq"] > self.seq[edge]: #if old message, update your neighbors with your latest information concerning this edge
            self.seq[edge] = m["seq"]
            if m["cost"] == -1 and edge in self.edges: #remove the edge if you have to
                self.edges.remove(edge)
                del self.weights[edge]
                #del self.seq[edge]
                del self.lastMsgs[edge]
                for node in edge:
                    if node != id:
                        self.nodes.remove(node)
            else: 
                if edge not in self.edges: #if youu don't have this edge add it
                    self.edges.append(edge)
                    if m["src"] != id:
                        self.nodes.append(m["src"])
                    if m["dest"] != id:
                        self.nodes.append(m["dest"])
                    for key, value in self.lastMsgs.items():
                        self.send_to_neighbor(m["src"], value)
                        self.send_to_neighbor(m["dest"], value)
                #update accordingly
                self.weights[edge] = m["cost"]
                self.lastMsgs[edge] = json.dumps(m)
            self.send_to_neighbors(json.dumps(m)) #retransmit the message
        else: #if old message, update your neighbors with your latest information concerning this edge 
            if m["seq"] < self.seq[edge]:
                self.send_to_neighbor(m["src"], self.lastMsgs[edge])


     
        ##logic here is off


    # Return a neighbor, -1 if no path to destination
    #****Tested and working the below code runs dijkstras properly
    def get_next_hop(self, destination):
        #dijkstras
        dist = {}
        prev = {}
        Q = self.nodes.copy()
        for v in Q:
                dist[v] = sys.maxsize
                prev[v] = None
        dist[destination] = 0
        
        while len(Q) > 0:
            u = self.get_min_vertex(Q, dist) #gets the vertex u in the Q with min dist[u]
            Q.remove(u)


            # for v in self.get_all_neighbors(u):
            #     alt = dist[u] + self.weights[frozenset({u,v})]
            #     if alt < dist[v]:
            #         dist[v] = alt
            #         prev[v] = u

                
            for edge in self.edges: #for each edge
                if u in edge: #allows you to access only neighbors of u
                    alt = dist[u] + self.weights[edge]
                    for v in edge: 
                        if v != u: #since we're using a set, how you access the node u is connected to (v)
                            if alt < dist[v]:
                                dist[v] = alt
                                prev[v] = u
        
        return prev.get(self.id)
        


    def get_min_vertex(self, loNodes, dist):
        min = sys.maxsize
        minNode = loNodes[0]
        for node in loNodes:
            if dist[node] < min:
                min = dist[node]
                minNode = node      
        return minNode
    
    def get_all_neighbors(self, u):
        res = []
        for edge in self.edges:
            if u in edge:
                for node in edge:
                    if node !=u: res.append(node)
        return res