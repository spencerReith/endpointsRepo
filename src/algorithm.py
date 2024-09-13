# The algorithm

from classes.applicant import Applicant
import matplotlib.pyplot as plt
import networkx as nx
import scipy as sp
import sqlite3
import random
import math


########################################################
### ESTABLISHING GRAPH 'G' #############################
########################################################

testG = nx.DiGraph()

########################################################
### ITERATE THROUGH IN-DEGREE's AND FIND CURRENT OFFERS
########################################################

def findCurrentOffers(G, selfID):
    ## create a list of ID's for all indegree's of self node
    in_degrees = list(G.predecessors(selfID))
    random.shuffle(in_degrees)

    current_offers = []
    for node_id in in_degrees:
        ## assuming you have not yet evaluated or been reffered to this candidate
        if not G.has_edge(selfID, node_id):
            ## they are not an offer if they've blacklisted you
            if G[node_id][selfID]['weight'] == 9:
                continue
            ## they are not an offer if they've rejected you
            elif G[node_id][selfID]['weight'] == 0:
                continue
            ## they are not an offer if they've been refferred to you
            ## this can't actually happen, since if they've been successfull reffered to you,
            ## you either liked them or were reffered to them, so there would be an edge going from self to them
            ## in which case you never would have made it past the last if statement
            ## keeping in here for explanation/ incase of changes to the program in the future so we catch it
            elif G[node_id][selfID]['weight'] == 14:
                continue
            ## otherwise, they must have given you an offer
            else:
                current_offers.append(node_id)
    return current_offers

########################################################
### ITERATE THROUGH NEVER BEFORE SEEN APPLICANTS #######
########################################################


def findUnmetList(G, selfID, unmet_cap):
    unmet_list = []
    sex = G.nodes[selfID]['sex']
    prefSex = G.nodes[selfID]['prefSex']

    ## get a list of all the randomly shuffled nodes
    node_keys = list(G.nodes)
    random.shuffle(node_keys)

    ## iterate through them
    for node_key in node_keys:
        ## assuming you have not yet met the cap for unmet applicants
        if len(unmet_list) < unmet_cap:
            ## if G has already seen, blacklisted, or been successfully refferred to this applicant, move to next applicant
            if G.has_edge(selfID, node_key):
                continue
            ## if G is this applicant, move to next applicant
            if node_key == selfID:
                continue

            ## let b represent the other applicant with key=node_key, where in the expression b.[], [] represents some property of b
            ## this is not to be confused with 'b' meaning bisexual under prefSex
            ## NOW...
            ## if b.sex == self.prefSex, or self.prefSex = bisexual
            if G.nodes[node_key]['sex'] == prefSex or prefSex == 'b':
                ## if self.sex = b.prefSex, or b.prefSex = bisexual
                if sex == G.nodes[node_key]['prefSex'] or G.nodes[node_key]['prefSex'] == 'b':
                    ## only if b has not seen, blacklisted, or been successfully reffered to self, do we show b in algorithm
                    if not G.has_edge(node_key, selfID):
                        unmet_list.append(node_key)
    return unmet_list


########################################################
### EDGE CASE: |unmet|=0, but |response|>0 #############
########################################################

def findResponseList(current_offers, response_cap):
    ## append the response_cap amount of id's onto the response_list from the list of current offers
    response_list = []

    for offer_id in current_offers:
        if len(response_list) < response_cap:
            response_list.append(offer_id)

    return response_list

########################################################
### EXECUTE FUNCIONS ###################################
########################################################


def getCompositeQueue(G, selfID, cap):
    current_offers = findCurrentOffers(G, selfID)
    # set cap for overall queue
    totalCap = cap

    ## would probably be best to change this math up if we're doing stacks larger than 10... will still work well but can get more exact. Still could be right if we are considering allowing you to swipe through 4 full stakcs, regardless of how many people are in them.
    if len(current_offers) > 28:
        ## we never want to show more than 28 offers in a stack
        response_cap = 28
    else:
        ## assume you'll go through 4 stacks of people in a day
        ## assume we want you to see 80% of your active (and unviewed) offers a day
        response_cap = math.ceil(.8 * len(current_offers))

    unmet_cap = totalCap - response_cap

    unmet_list = findUnmetList(G, selfID, unmet_cap)
    ## If |unmet_list| + |about-to-be-calculated-reponse_list| < 10 (if 10 is the total cap)
    ## Adjust the size of the response list to fill up the rest of the queue
    ## For example, |unmet_list| = 4, but the algorithm is only going to show you 3 people on your response list
    ## It might as well just fill up the queue and show you all of them
    ## The point of limiting the response list was so that you get see new people as you swipe, but also go through most of your responses in a day
    ## If you've already seen everyone (aka, |unmet_list| == 0), then you might as well respond to everyone in your response list
    if len(unmet_list) + response_cap < totalCap:
        response_cap = totalCap - len(unmet_list)
    response_list = findResponseList(current_offers, response_cap)

    composite_queue = unmet_list + response_list
    random.shuffle(composite_queue)

    return composite_queue



