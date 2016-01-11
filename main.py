import math
import csv
import operator
import random
import sys
import time
import copy
import matplotlib.pyplot as plt

NUMBER_OF_GIFTS = 100000
MAX_SLEIGH_WEIGHT = 1000.0
SLEIGH_WEIGHT = 10.0
M_PI2 = math.pi/2.0
SQRT_12 = math.sqrt(1.0/12.0)

EARTH_R = 1.0 # this is not a joke :-)
SECOND_TRIP_RANDINT_OFFSET = 1

SEED = random.randint(0, 10000000000)
rnd = random.Random(SEED)


class Trip:
    gift_list = []
    
    def __init__(self, gift_id_list, trip_weight):
        self.gift_id_list = gift_id_list
        self.trip_weight = trip_weight
        self.update_wrw = True
        self.trip_wrw = 0.0

    def print_gifts(self):
        for i in range( len(self.gift_id_list) ):
            sys.stdout.write(str(self.gift_id_list[i]) + " ")
        sys.stdout.write("\n")

    def get_gift_id_at_position(self, pos):
        if (pos >= 0) and (pos < len(self.gift_id_list)): 
            return self.gift_id_list[pos]

    def push_gift(self, gift_id):
        self.update_wrw = True
        if self.trip_weight + Trip.gift_list[gift_id][3] <= MAX_SLEIGH_WEIGHT:
            self.gift_id_list.append(gift_id)
            self.trip_weight = self.trip_weight + Trip.gift_list[gift_id][3]
            return True
        else:
            return False

    def swap_gifts(self):
        self.update_wrw = True
        N = len(self.gift_id_list)
        g1 = rnd.randint(0,N-1)
        g2 = rnd.randint(0, N-1)

        temp_gift = self.gift_id_list[g1]
        self.gift_id_list[g1] = self.gift_id_list[g2]
        self.gift_id_list[g2] = temp_gift
        
        return (g1,g2)
        
    def reverse_swap(self, g1, g2):
        self.update_wrw = True
        tempGift = self.gift_id_list[g1]
        self.gift_id_list[g1] = self.gift_id_list[g2]
        self.gift_id_list[g2] = tempGift
        

    def insert_gift(self, i, gift_id):
        self.update_wrw = True
        if self.trip_weight + Trip.gift_list[gift_id][3] <= MAX_SLEIGH_WEIGHT:
            self.gift_id_list.insert(i, gift_id)
            self.trip_weight = self.trip_weight + Trip.gift_list[gift_id][3]
            return True
        else:
            return False
        
    def pop_gift(self, i):
        self.update_wrw = True
        gift_id = self.gift_id_list[i]
        self.trip_weight = self.trip_weight - Trip.gift_list[gift_id][3]
        return self.gift_id_list.pop(i)

    def get_trip_wrw(self):
        
        if self.update_wrw == False:
            return self.trip_wrw
        else:
        
            wrw = 0.0
            current_sleigh_weight = self.trip_weight + SLEIGH_WEIGHT
            
            i_lat = Trip.gift_list[ self.gift_id_list[0] ][1]
            i_lon = Trip.gift_list[ self.gift_id_list[0] ][2]
            wrw = wrw + (current_sleigh_weight)*haversine_d(0.0, M_PI2, i_lon, i_lat)
            current_sleigh_weight = current_sleigh_weight - Trip.gift_list[ self.gift_id_list[0] ][3]
            
            for i in range(1, len(self.gift_id_list)):
                i_minus_1_lat = Trip.gift_list[ self.gift_id_list[i-1] ][1]
                i_minus_1_lon = Trip.gift_list[ self.gift_id_list[i-1] ][2]
                
                i_lat = Trip.gift_list[ self.gift_id_list[i] ][1]
                i_lon = Trip.gift_list[ self.gift_id_list[i] ][2]
                wrw = wrw + (current_sleigh_weight)*haversine_d(i_minus_1_lon, i_minus_1_lat, i_lon, i_lat)
                current_sleigh_weight = current_sleigh_weight - Trip.gift_list[ self.gift_id_list[i] ][3]
            
            i_lat = Trip.gift_list[ self.gift_id_list[-1] ][1]
            i_lon = Trip.gift_list[ self.gift_id_list[-1] ][2]
            wrw = wrw + current_sleigh_weight*haversine_d(0.0, M_PI2, i_lon, i_lat)
        
        self.trip_wrw = wrw
        self.update_wrw = False
        
        return wrw
    
    def get_number_of_gifts_in_trip(self):
        return len(self.gift_id_list)
    
    def sort_trip(self):
        self.update_wrw = True
        self.gift_id_list.sort(key=lambda x: Trip.gift_list[x][3], reverse=True)
        
    def latitudesort_trip(self):
        self.update_wrw = True
        self.gift_id_list.sort(key=lambda x: Trip.gift_list[x][1], reverse=True)


class Journey:
    
    def __init__(self, trip_list):
        self.trip_list = trip_list
    
    def print_journey(self):
        for i in range( len(self.trip_list) ):
            self.trip_list[i].print_gifts()
        
    def print_journey_to_file(self, fileName, comment = "No comment provided"):
        
        f = open(fileName, "w")
        f.write(comment + "\n")
        f.write("SEED: " + str(SEED) + "\n")
        
        f.write("wrw score: " + str(6371.0*self.get_journey_wrw()) + "\n")
        f.write("TripId,gift_id\n")
        
        for i in range( len(self.trip_list) ):
            n_gifts_in_trip = self.trip_list[i].get_number_of_gifts_in_trip()
            for j in range(n_gifts_in_trip):
                gift_id = self.trip_list[i].get_gift_id_at_position(j)
                f.write(str(i) + "," + str(gift_id) + "\n")
        f.close()
                
    
    def push_trip(self, trip):
        self.trip_list.append(trip)
    
    def pop_trip(self, i):
        return self.trip_list.pop(i)
    
    def insert_trip(self, i, trip):
        self.trip_list.insert(i,trip)
    
    def get_journey_wrw(self):
        wrw = 0.0
        for i in range(len(self.trip_list)):
            wrw = wrw + self.trip_list[i].get_trip_wrw()
        return wrw
    
    def get_number_of_gifts_in_journey(self):
        N = 0
        for i in range(len(self.trip_list)):
            N = N + self.trip_list[i].get_number_of_gifts_in_trip()
        return N
    
    def sort_trips(self):
        for i in range(len(self.trip_list)):
            self.trip_list[i].sort_trip()
            
    def get_number_of_trips(self):
        return len(self.trip_list)

    
    def swap_gifts_in_random_trips(self, N):
        # For every trip N the positions of two gifts are swaped.
        # The gifts are swaped in the same trip.
        
        self.swaped_trips = [0 for i in range(N)]
        self.swaped_gifts = [(0,0) for i in range(N)]
        for i in range(N):
            cNTrips = len(self.trip_list)  
            swapTrip = rnd.randint( 0, cNTrips-1 )
            g1, g2 = self.trip_list[swapTrip].swap_gifts()
            
            self.swaped_trips[i] = swapTrip
            self.swaped_gifts[i] = (g1,g2)

    def swap_gifts_between_two_nearest_trips(self):
        self.swap_information = [0, 0, 0, 0, 0]
        
        N = self.get_number_of_trips()
        first_trip_id = rnd.randint( 0, N-1 )
        second_trip_id= 0
        coin_toss = rnd.randint(0, 1)
        
        if first_trip_id == 0:
            if first_trip_id == 0:
                if coin_toss == 0:
                    second_trip_id = 1
                else:
                    second_trip_id = (N-1)
            elif first_trip_id == (N-1):
                if coin_toss == 0:
                    second_trip_id = 1
                else:
                    second_trip_id = (N-2)
            else:
                if coin_toss == 0:
                    second_trip_id = first_trip_id + 1
                else:
                    second_trip_id = first_trip_id - 1
        
        self.swap_information[1] = first_trip_id
        self.swap_information[2] = second_trip_id
        
        f_trip = self.trip_list[first_trip_id]
        s_trip = self.trip_list[second_trip_id]
        
        first_gift_position = rnd.randint( 0, f_trip.get_number_of_gifts_in_trip() - 1 )
        second_gift_position = rnd.randint( 0, s_trip.get_number_of_gifts_in_trip() - 1 )
        
        self.swap_information[3] = first_gift_position
        self.swap_information[4] = second_gift_position
        
        f_gift_id = f_trip.get_gift_id_at_position(first_gift_position)
        s_gift_id = s_trip.get_gift_id_at_position(second_gift_position)
        
        f_gift_weight = Trip.gift_list[f_gift_id][3]
        s_gift_weight = Trip.gift_list[s_gift_id][3]
        
        if (f_trip.trip_weight - f_gift_weight + s_gift_weight < MAX_SLEIGH_WEIGHT) and \
            (s_trip.trip_weight - s_gift_weight + f_gift_weight < MAX_SLEIGH_WEIGHT):
            
            f_trip.gift_id_list[first_gift_position] = s_gift_id
            s_trip.gift_id_list[second_gift_position] = f_gift_id
            
            f_trip.trip_weight = f_trip.trip_weight - f_gift_weight + s_gift_weight
            s_trip.trip_weight = s_trip.trip_weight - s_gift_weight + f_gift_weight
            
            self.swap_information[0] = 1
        else:
            self.swap_information[0] = -1
        


    def reverse_swap_gifts_between_two_nearest_trips(self):
        
        if self.swap_information[0] == 1:
        
            first_trip_id = self.swap_information[1]
            second_trip_id = self.swap_information[2]
            
            first_gift_position = self.swap_information[3]
            second_gift_position = self.swap_information[4]
            
            f_trip = self.trip_list[first_trip_id]
            s_trip = self.trip_list[second_trip_id]
            
            f_gift_id = f_trip.get_gift_id_at_position(first_gift_position)
            s_gift_id = s_trip.get_gift_id_at_position(second_gift_position)
            
            f_trip.gift_id_list[first_gift_position] = s_gift_id
            s_trip.gift_id_list[second_gift_position] = f_gift_id
            
            f_gift_weight = Trip.gift_list[f_gift_id][3]
            s_gift_weight = Trip.gift_list[s_gift_id][3]
            
            f_trip.trip_weight = f_trip.trip_weight - f_gift_weight + s_gift_weight
            s_trip.trip_weight = s_trip.trip_weight - s_gift_weight + f_gift_weight
        else:
            pass

    def reverse_gift_swaps_in_trips(self):
        for i in range(len(self.swaped_trips)-1,-1,-1):
            self.trip_list[self.swaped_trips[i]].reverse_swap(self.swaped_gifts[i][0], self.swaped_gifts[i][1])
        

    def transfer_many_gifts_between_nearest_trips(self, n_transfers):
        
        # The following transfer types are possible:
        # -1 no transfer occured,
        # 0 normal transfer,
        # 1 transfer with trip deletion,
        # 2 transfer with trip creation.
        
        self.transfer_type = [0 for i in range(n_transfers)]
        self.transfer_trip_ids = [[0,0] for i in range(n_transfers)]
        self.transfer_gift_positions = [[0,0] for i in range(n_transfers)]
        self.transfered_gift_id = [0 for i in range(n_transfers)]
        
        for nT in range(n_transfers):
            N = len(self.trip_list)
            first_trip_id = rnd.randint(0, N-1)
            second_trip_id = 0
            
            coin_toss = rnd.randint(0, 1)
            if first_trip_id == 0:
                if coin_toss == 0:
                    second_trip_id = 1
                else:
                    second_trip_id = (N-1)
            elif first_trip_id == (N-1):
                if coin_toss == 0:
                    second_trip_id = 1
                else:
                    second_trip_id = (N-2)
            else:
                if coin_toss == 0:
                    second_trip_id = first_trip_id +1
                else:
                    second_trip_id = first_trip_id -1
            
            random_gift_position_1 = 0
            random_gift_position_2 = 0
            
            self.transfer_trip_ids[nT][0] = first_trip_id
            self.transfer_trip_ids[nT][1] = second_trip_id 
            
            number_of_gifts_in_first_trip = self.trip_list[first_trip_id].get_number_of_gifts_in_trip()
            if (number_of_gifts_in_first_trip == 1) and (second_trip_id >= N):
                self.transfer_type[nT] = -1
                return 0
            if first_trip_id == second_trip_id:
                self.transfer_type[nT] = -1
                return 0
            
            gift_id = 0
            if number_of_gifts_in_first_trip == 1:
                gift_id = self.trip_list[first_trip_id].gift_id_list[0]
                self.pop_trip(first_trip_id)
                
                N = len(self.trip_list)
                second_trip_id = rnd.randint(0, N-1)
                self.transfer_trip_ids[nT][1] = second_trip_id
                
                self.transfered_gift_id[nT] = gift_id
                self.transfer_type[nT] = 1
            else:
                random_gift_position_1 = rnd.randint(0, number_of_gifts_in_first_trip-1)
                gift_id = self.trip_list[first_trip_id].pop_gift(random_gift_position_1)
                
                self.transfer_gift_positions[nT][0] = random_gift_position_1
                self.transfered_gift_id[nT] = gift_id
                self.transfer_type[nT] = 0
            
            if second_trip_id < N:
                numberOfGiftsInSecondTrip = self.trip_list[second_trip_id].get_number_of_gifts_in_trip()
                random_gift_position_2 = rnd.randint(0, numberOfGiftsInSecondTrip)
                
                inserted = self.trip_list[second_trip_id].insert_gift(random_gift_position_2, gift_id)
                if (inserted == False) and (number_of_gifts_in_first_trip != 1):
                    self.trip_list[first_trip_id].insert_gift(random_gift_position_1, gift_id)
                    self.transfer_type[nT] = -1
                    return 0
                
                if (inserted == False) and (number_of_gifts_in_first_trip == 1):
                    oldTrip = Trip([], 0.0)
                    oldTrip.push_gift(gift_id)
                    self.trip_list.insert(first_trip_id, oldTrip)
                    
                    self.transfer_type[nT] = -1
                    return 0
                
                self.transfer_gift_positions[nT][1] = random_gift_position_2
            else:
                newTrip = Trip([], 0.0)
                newTrip.push_gift(gift_id)
                self.push_trip(newTrip)
                
                
                self.transfer_trip_ids[nT][1] = -1
                self.transfer_gift_positions[nT][1] = -1
                self.transfer_type[nT] = 2
    


    def transfer_many_gifts_between_trips(self, n_transfers):
        
        # The following transfer types are possible:
        # -1 no transfer occured,
        # 0 normal transfer,
        # 1 transfer with trip deletion,
        # 2 transfer with trip creation.
        
        self.transfer_type = [0 for i in range(n_transfers)]
        self.transfer_trip_ids = [[0,0] for i in range(n_transfers)]
        self.transfer_gift_positions = [[0,0] for i in range(n_transfers)]
        self.transfered_gift_id = [0 for i in range(n_transfers)]
        
        for nT in range(n_transfers):
            N = len(self.trip_list)
            first_trip_id = rnd.randint(0, N-1)
            second_trip_id = rnd.randint(0, math.floor(N + SECOND_TRIP_RANDINT_OFFSET ) )
            random_gift_position_1 = 0
            random_gift_position_2 = 0
            
            self.transfer_trip_ids[nT][0] = first_trip_id
            self.transfer_trip_ids[nT][1] = second_trip_id 
            
            number_of_gifts_in_first_trip = self.trip_list[first_trip_id].get_number_of_gifts_in_trip()
            if (number_of_gifts_in_first_trip == 1) and (second_trip_id >= N):
                self.transfer_type[nT] = -1
                return 0
            if first_trip_id == second_trip_id:
                self.transfer_type[nT] = -1
                return 0
            
            gift_id = 0
            if number_of_gifts_in_first_trip == 1:
                gift_id = self.trip_list[first_trip_id].gift_id_list[0]
                self.pop_trip(first_trip_id)
                
                N = len(self.trip_list)
                second_trip_id = rnd.randint(0, N-1)
                self.transfer_trip_ids[nT][1] = second_trip_id
                
                self.transfered_gift_id[nT] = gift_id
                self.transfer_type[nT] = 1
            else:
                random_gift_position_1 = rnd.randint(0, number_of_gifts_in_first_trip-1)
                gift_id = self.trip_list[first_trip_id].pop_gift(random_gift_position_1)
                
                self.transfer_gift_positions[nT][0] = random_gift_position_1
                self.transfered_gift_id[nT] = gift_id
                self.transfer_type[nT] = 0
            
            if second_trip_id < N:
                
                numberOfGiftsInSecondTrip = self.trip_list[second_trip_id].get_number_of_gifts_in_trip()
                random_gift_position_2 = rnd.randint(0, numberOfGiftsInSecondTrip)
                inserted = self.trip_list[second_trip_id].insert_gift(random_gift_position_2, gift_id)
                
                if (inserted == False) and (number_of_gifts_in_first_trip != 1):
                    self.trip_list[first_trip_id].insert_gift(random_gift_position_1, gift_id)
                    self.transfer_type[nT] = -1
                    return 0
                
                if (inserted == False) and (number_of_gifts_in_first_trip == 1):
                    oldTrip = Trip([], 0.0)
                    oldTrip.push_gift(gift_id)
                    self.trip_list.insert(first_trip_id, oldTrip)
                    
                    self.transfer_type[nT] = -1
                    return 0
                
                self.transfer_gift_positions[nT][1] = random_gift_position_2
            else:
                newTrip = Trip([], 0.0)
                newTrip.push_gift(gift_id)
                self.push_trip(newTrip)
                
                self.transfer_trip_ids[nT][1] = -1
                self.transfer_gift_positions[nT][1] = -1
                self.transfer_type[nT] = 2


    def transfer_many_gifts_back(self):
        
        for nT in range(len(self.transfer_type)-1,-1,-1):
            t = self.transfer_type[nT]
            
            
            if t == 0:
                first_trip_id = self.transfer_trip_ids[nT][0]
                second_trip_id = self.transfer_trip_ids[nT][1]
                
                
                gift_id = self.trip_list[second_trip_id].pop_gift(self.transfer_gift_positions[nT][1])
                #print("popped")
                self.trip_list[first_trip_id].insert_gift(self.transfer_gift_positions[nT][0], gift_id)
                #print("inserted")
                
            elif t == 1:
                first_trip_id = self.transfer_trip_ids[nT][0]
                second_trip_id = self.transfer_trip_ids[nT][1]
                
                gift_id = self.trip_list[second_trip_id].pop_gift(self.transfer_gift_positions[nT][1])
                trip = Trip([], 0.0)
                trip.push_gift(gift_id)
                self.trip_list.insert(first_trip_id, trip)
                
            elif t == 2: 
                first_trip_id = self.transfer_trip_ids[nT][0]
                
                gift_id = self.trip_list[-1].get_gift_id_at_position(0)
                self.trip_list.pop( len(self.trip_list)-1 )
                
                self.trip_list[first_trip_id].insert_gift(self.transfer_gift_positions[nT][0], gift_id)
            else:
                pass
                
    def make_nearest_random_state(self, n_transfers, n_swaps):
        self.transfer_many_gifts_between_nearest_trips(n_transfers)
        self.swap_gifts_in_random_trips(n_swaps)
    
        
    def make_random_state(self, n_transfers ,n_swaps):
        self.transfer_many_gifts_between_trips(n_transfers)
        #self.swap_gifts_in_random_trips(n_swaps)

    def reverse_nearest_random_state(self):
        #self.reverse_gift_swaps_in_trips()
        self.transfer_many_gifts_back()
        
    def reverse_random_state(self):
        #self.reverse_gift_swaps_in_trips()
        self.transfer_many_gifts_back()


def read_data(fileName):
    
    csv_reader = csv.reader(open(fileName), delimiter=',')
    data_list = list(csv_reader)
    
    return data_list[1:]


def hav(theta):
    return (1.0 - math.cos(theta))/2.0


def haversine_d(lon1, lat1, lon2, lat2):
    # Earth radious. Not Relevant for the optimization.
    return 2.0*EARTH_R*math.asin( math.sqrt( hav(lat2 - lat1) + math.cos(lat1)*math.cos(lat2)*hav(lon2-lon1) ) )



def make_gift_list(data):
    
    gift_list = [0 for i in range(len(data)+1)]
    gift_list[0] = [-1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0]
    for i in range(len(data)):
        
        th = math.pi*float(data[i][1])/180.0
        ph = math.pi*float(data[i][2])/180.0
        
        c_gift_id    = int(data[i][0])
        c_latitude  = th
        c_longitude = ph
        c_weight    = float(data[i][3])

        x = math.sin(math.pi/2.0 - th)*math.cos(ph)
        y = math.sin(math.pi/2.0 - th)*math.sin(ph)
        z = math.cos(math.pi/2.0 - th)
        
        X = x*math.sqrt(2.0/(1.0-z))
        Y = y*math.sqrt(2.0/(1.0-z))
        
        d = math.sqrt(X*X+Y*Y)
        
        dis = haversine_d(0.0, math.pi/2.0, ph, th)
        
        gift_list[i+1] = [c_gift_id, c_latitude, c_longitude, c_weight, X, Y, d, 0, dis]
    
    return gift_list


def dot(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]

def norm(v1):
    return math.sqrt(v1[0]*v1[0]+v1[1]*v1[1])


# There are two ways in which we handle the trips.
# Either through the Trip and Journey classes which are used
# for all functions that involve random swaping of gifts
# or as a simple list of lists.
# The functions below handle the list of list approach 
# which does not use classes.

def get_curved_trips(ph_sorted_gifts, massOffset = 0.0):
    
    gifts_added = 0
    trip_list = []
    while(True):

        trip = []
        cw = 0.0
        for i in range(len(ph_sorted_gifts)):
            if ph_sorted_gifts[i][7] == 1:
                continue
            
            if (cw + ph_sorted_gifts[i][3]) > MAX_SLEIGH_WEIGHT - massOffset:
                break
            
            cw = cw + ph_sorted_gifts[i][3]
            trip.append(ph_sorted_gifts[i])
            ph_sorted_gifts[i][7] = 1
            gifts_added = gifts_added + 1
            
            if gifts_added >= len(ph_sorted_gifts):
                break
        
        trip = sorted(trip, key=operator.itemgetter(8))
        trip_list.append(trip)
        
        if gifts_added >= len(ph_sorted_gifts):
            break
        
    return trip_list


def convert_trip_list_to_journey(phtrip_list):
    
    jo = Journey([])
    for i in range(len(phtrip_list)):
        t = Trip([], 0.0)
        for j in range(len(phtrip_list[i])):
            t.push_gift(phtrip_list[i][j][0])
        
        jo.push_trip(t)
    return jo                          
  
  
            
def metropolis_alg(initial_state, n_iter, \
                   n_transfers, n_swaps, \
                   period = 100000, make_iteration_and_wrw_arrays = False):
    
    iteration_array = []
    wrw_array = []
    
    period_print = True
    start = time.time()
    initial_wrw = initial_state.get_journey_wrw()
    minimal_journey = copy.deepcopy(initial_state)
    
    for i in range(n_iter):

        current_wrw = initial_state.get_journey_wrw()
        if current_wrw < initial_wrw:
            initial_wrw = current_wrw
            if period_print == True:
                print("Minimal wrw: " + str(6371.0*initial_wrw))
                #initial_state.print_journey_to_file("minimal_journey_exact_MH.dat", "we are at iteration: " + str(i))
                minimal_journey = copy.deepcopy(initial_state)
                period_print = False
        if (i % period == 0):
            
            if make_iteration_and_wrw_arrays == True:
                iteration_array.append(i)
                wrw_array.append(6371.0*current_wrw)
            
            print("\n" + "We are at iteration: " + str(i))
            print("Number of trips in initial state: " + str(initial_state.get_number_of_trips()))
            print("Number of gifts in initial state: " + str(initial_state.get_number_of_gifts_in_journey()))
            print("Random  wrw: " + str(6371.0*current_wrw))
            initial_state.print_journey_to_file("minimal_journey_random_probing_MH.dat", "we are at iteration: " + str(i))
            period_print = True
            end = time.time()
            print("time for " + str(period) + " iterations: " + str(end - start))
            start = time.time()
            
        initial_state.make_random_state(n_transfers, n_swaps)
        wrw_n = initial_state.get_journey_wrw()
        
        T = 0.2
        A = math.exp( current_wrw/(T*EARTH_R) - wrw_n/(T*EARTH_R))
        
        if rnd.random() < A:
            continue
        else:
            initial_state.reverse_random_state()
    
    

    
    return minimal_journey, iteration_array, wrw_array


def shuffle_gifts(gift_list):
    
    random_gift_list = [gift_list[i] for i in range(len(gift_list))]
    rnd.shuffle(random_gift_list)
    return random_gift_list  


def make_random_journey(gifts, max_gifts_in_trip):
    
    random_gift_list = shuffle_gifts(gifts[1:])
    random_gift_list.insert(0, 0)
    n_gifts = 1
    
    random_journey = Journey([])
    
    while(True):
        n_gifts_in_trip = rnd.randint(1, max_gifts_in_trip)
        trip = Trip([], 0.0)
        for i in range(n_gifts_in_trip):
            if n_gifts > NUMBER_OF_GIFTS:
                break
            if trip.push_gift( random_gift_list[n_gifts][0] ):
                n_gifts = n_gifts + 1
            else:
                random_journey.push_trip(trip)
                break
        random_journey.push_trip(trip)
        if n_gifts > NUMBER_OF_GIFTS:
            break
    
    return random_journey


def make_sample_journay(sample_submission_data):
    N = int(sample_submission_data[-1][1])+1
    trip_list = [Trip([], 0.0) for i in range(N)]
    
    for i in range(len(sample_submission_data)):
        g_id = int(sample_submission_data[i][0])
        t_id = int(sample_submission_data[i][1])
        
        trip_list[t_id].push_gift(g_id)
    
    return Journey(trip_list)


def make_random_journey_cluster(gifts_in_clusters, max_gifts_in_trip):
    
    random_gift_list = shuffle_gifts(gifts_in_clusters)
    number_of_gifts_in_cluster = len(random_gift_list)
    n_gifts = 1
    
    random_journey = Journey([])
    
    while(True):
        n_gifts_in_trip = rnd.randint(1, max_gifts_in_trip)
        trip = Trip([], 0.0)
        for i in range(n_gifts_in_trip):
            if n_gifts >= number_of_gifts_in_cluster:
                break
            if trip.push_gift( random_gift_list[n_gifts][0] ):
                n_gifts = n_gifts + 1
            else:
                random_journey.push_trip(trip)
                break
        random_journey.push_trip(trip)
        
        if n_gifts >= number_of_gifts_in_cluster:
            break
    
    return random_journey



if __name__ == "__main__":
    gifts_file_name = "gifts.csv"
    data = read_data(gifts_file_name)
    gifts = make_gift_list(data)
    Trip.gift_list = gifts
    
    # Checking the sample submission
    sample_submission_data = read_data("sample_submission.csv")
    js = make_sample_journay(sample_submission_data)
    
    print("Number of trips: " + str(js.get_number_of_trips()))
    print("Number of gifts: " + str(js.get_number_of_gifts_in_journey()))
    print("Sample trips wrw: " + str(6371.0*js.get_journey_wrw()))

    number_of_iterations = 1000000
    period = 10000
    
    gifts_cluster_file_name = "gifts50.csv"
    cluster_data = read_data(gifts_cluster_file_name)
    gifts_in_clusters = make_gift_list(cluster_data)
    
    jo = make_random_journey_cluster(gifts_in_clusters, 1)
    jo, x, y = metropolis_alg(jo, number_of_iterations, 1, 1, period, True)
    
    print("Minimal wrw: " + str(6371.0*jo.get_journey_wrw()))
    