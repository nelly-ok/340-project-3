from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        #self.my_dv = {} #lists thee [cost, next_hop] for every destination
        self.my_dv = {id: {"cost": 0, "path": []}}
        self.neighbors_dvs = {}
        self.neighbors_prev_seq = {}
        self.neighbors_cost = {} ####please change

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        

        #receive a a message 
        if neighbor not in self.my_dv:
            # temp_dv = self.my_dv.copy()
            # temp_dv[neighbor] = {"cost": latency, "path": [neighbor]}
            self.neighbors_cost[neighbor] = {"cost": latency, "path": [neighbor]}
            temp_dv = self.neighbors_cost.copy()

        elif latency == -1:
            del self.my_dv[neighbor]
            #del self.neighbors_dvs[neighbor]
            del self.neighbors_cost[neighbor]
            temp_dv = self.neighbors_cost.copy()
        else: 
            self.neighbors_cost[neighbor] = {"cost": latency, "path": [neighbor]}
            temp_dv = self.neighbors_cost.copy()
            temp_dv = self.recompute_dv(temp_dv)
        
        if temp_dv != self.my_dv:
            self.my_dv = temp_dv
            m = json.dumps({"src": self.id, "seq": self.get_time(), "dv": self.my_dv})
            #increment sequence nummber
            self.send_to_neighbors(m)

            


        '''
        if neighbor isn't already my neighbor:
            add him to my list of neighbors
            speciify that the cost to get to him is latency, and that the path is neighbor
            store the current list of neighbors costs in new_dv
        elif latency == -1:
            remove neighbors fromm list of neighbords
            pop neighbbor from everywhere it currenntly is
            store the current list of neighbors costs in new_dv
        else: so like neighbor already exists
            update that the cost to get to thtiis neigh is changed, and the path is nneighbbor
            store the current list of neighbors costs in new_dv
            new_dv is self.dv_update//recompute it

        after all that
        if you end up with a new_dv that is different from what you had previously
            update you dv
            blast a message to neighbors

        '''



    # Fill in this function
    def process_incoming_routing_message(self, m):

        m = json.loads(m)
        if m["src"] not in self.my_dv:
            self.neighbors_prev_seq[m["src"]] = m["seq"]
            self.neighbors_dvs[m["src"]] = m["dv"]
        elif m["src"] in self.neighbors_dvs and self.neighbors_prev_seq[m["src"]] < m["seq"]:
            self.neighbors_prev_seq[m["src"]] = m["seq"]
            self.neighbors_dvs[m["src"]] = m["dv"]
        else: return

        temp_dv = self.neighbors_cost.copy() #self.my_dv.copy()
        temp_dv = self.recompute_dv(temp_dv)

        if temp_dv != self.my_dv:
            self.my_dv = temp_dv
            m = json.dumps({"src": self.id, "seq": self.get_time(), "dv": self.my_dv})
            #increment sequence nummber
            self.send_to_neighbors(m)


    '''
        when you receive a message
        if its a node you haven'tseen bbefore and isnt in nyoour neighborrs:
            update a sequence number of the neighbor/edge to the seq number in the mmessage
            update my neighbord_dv_table thaat this node i just got this messaage from has the dv i also just got from the message
        else if seq num received > seq num i have, new mmessage old node, update:
            again updatee the sequence number -****** wait actualaly these cases do the samething
        else: return *** just bbee like - iff blaah bblah bblah - return

        new_dv = deep copy - old dv????
        new_div = self.dv_update (new_dv)

        if locaal dv and new arent the same:
            do the literalysame thing you did previously
               
    ''' 


    def recompute_dv(self,  dv):
        for neighbor in self.my_dv:
            if neighbor in self.neighbors_dvs and neighbor != self.id: #could possibly ommit
                for subNeigh in self.neighbors_dvs[neighbor]:
                    if self.id not in self.neighbors_dvs[neighbor][subNeigh]["path"]:
                        if subNeigh not in dv:
                            dv[subNeigh] = self.neighbors_dvs[neighbor][subNeigh]["cost"] + dv[neighbor]["cost"], dv[neighbor]["path"] + self.neighbors_dvs[neighbor][subNeigh]["path"] #fuck with append
                        else: 
                            if (dv[neighbor]["cost"] + self.neighbors_dvs[neighbor][subNeigh]["cost"]) < dv[subNeigh]["cost"]:
                                dv[subNeigh] = self.neighbors_dvs[neighbor][subNeigh]["cost"] + dv[neighbor]["cost"], dv[neighbor]["path"] + self.neighbors_dvs[neighbor][subNeigh]["path"] #fuck with append
        return dv

        '''
        for each neighboor:
           if nneighbor i is in my neighbors dv table:
                for each neighbor j inside that neighbor i's dv table:
                    if i am not in the path that exists here:
                        if this granular j, isn't in the dv this takes in i.e the one we're tryna change
                           add it - dv[j] = cost, path update cost and path         [self.neighbors_dv_table[i][j][0] + new_dv[i][0], new_dv[i][1] + self.neighbors_dv_table[i][j][1]]
                        else:
                            updaatee it 
                             # update existing cost and path
                            if (new_dv[i][0] + self.neighbors_dv_table[i][j][0]) < new_dv[j][0]:
                                new_dv[j] = [self.neighbors_dv_table[i][j][0] + new_dv[i][0],new_dv[i][1] + self.neighbors_dv_table[i][j][1]]
        return new_dv

        '''

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        if destination in self.my_dv:
            return self.my_dv[destination]["path"][0]
        return -1
