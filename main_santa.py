import math
import csv
import operator
import random
import sys
import time

NUMBER_OF_GIFTS = 100000
MAX_SLEIGH_WEIGHT = 1000.0
SLEIGH_WEIGHT = 10.0
M_PI2 = math.pi/2.0
SQRT_12 = math.sqrt(1.0/12.0)
SEED = random.randint(0, 10000000000)
EARTH_R = 1.0 # this is not a joke :-)
SECOND_TRIP_RANDINT_OFFSET = 1


#SEED = 481420852
print("Current seed: " + str(SEED))
rnd = random.Random(SEED)


class Trip:
    giftList = []
    
    def __init__(self, giftIdList, tripWeight):
        self.giftIdList = giftIdList
        self.tripWeight = tripWeight
        self.updateWRW = True
        self.tripWRW = 0.0

    def printGifts(self):
        for i in range( len(self.giftIdList) ):
            sys.stdout.write(str(self.giftIdList[i]) + " ")
        sys.stdout.write("\n")

    def getGiftIdAtPosition(self, pos):
        if (pos >= 0) and (pos < len(self.giftIdList)): 
            return self.giftIdList[pos]

    def pushGift(self, giftId):
        self.updateWRW = True
        if self.tripWeight + Trip.giftList[giftId][3] <= MAX_SLEIGH_WEIGHT:
            self.giftIdList.append(giftId)
            self.tripWeight = self.tripWeight + Trip.giftList[giftId][3]
            return True
        else:
            return False

    def swapGifts(self):
        self.updateWRW = True
        N = len(self.giftIdList)
        g1 = rnd.randint(0,N-1)
        g2 = rnd.randint(0, N-1)

        tempGift = self.giftIdList[g1]
        self.giftIdList[g1] = self.giftIdList[g2]
        self.giftIdList[g2] = tempGift
        
        return (g1,g2)
        
    def reverseSwap(self, g1, g2):
        self.updateWRW = True
        tempGift = self.giftIdList[g1]
        self.giftIdList[g1] = self.giftIdList[g2]
        self.giftIdList[g2] = tempGift
        

    def insertGift(self, i, giftId):
        self.updateWRW = True
        if self.tripWeight + Trip.giftList[giftId][3] <= MAX_SLEIGH_WEIGHT:
            self.giftIdList.insert(i, giftId)
            self.tripWeight = self.tripWeight + Trip.giftList[giftId][3]
            return True
        else:
            return False
        
    def popGift(self, i):
        self.updateWRW = True
        giftId = self.giftIdList[i]
        self.tripWeight = self.tripWeight - Trip.giftList[giftId][3]
        return self.giftIdList.pop(i)

    def getTripWrw(self):
        
        if self.updateWRW == False:
            return self.tripWRW
        else:
        
            wrw = 0.0
            pOBW = self.tripWeight + SLEIGH_WEIGHT # present on board wieght + SLEIGH_WEIGHT
            
            iLat = Trip.giftList[ self.giftIdList[0] ][1]
            iLon = Trip.giftList[ self.giftIdList[0] ][2]
            wrw = wrw + (pOBW)*haversineD(0.0, M_PI2, iLon, iLat)
            pOBW = pOBW - Trip.giftList[ self.giftIdList[0] ][3]
            
            for i in range(1, len(self.giftIdList)):
                im1Lat = Trip.giftList[ self.giftIdList[i-1] ][1]
                im1Lon = Trip.giftList[ self.giftIdList[i-1] ][2]
                
                iLat = Trip.giftList[ self.giftIdList[i] ][1]
                iLon = Trip.giftList[ self.giftIdList[i] ][2]
                wrw = wrw + (pOBW)*haversineD(im1Lon, im1Lat, iLon, iLat)
                pOBW = pOBW - Trip.giftList[ self.giftIdList[i] ][3]
            
            iLat = Trip.giftList[ self.giftIdList[-1] ][1]
            iLon = Trip.giftList[ self.giftIdList[-1] ][2]
            wrw = wrw + pOBW*haversineD(0.0, M_PI2, iLon, iLat)
        
        self.tripWRW = wrw
        self.updateWRW = False
        
        return wrw
    
    def getNumberOfGiftsInTrip(self):
        return len(self.giftIdList)
    
    def sortTrip(self):
        self.updateWRW = True
        self.giftIdList.sort(key=lambda x: Trip.giftList[x][3], reverse=True)
        
    def latitudeSortTrip(self):
        self.updateWRW = True
        self.giftIdList.sort(key=lambda x: Trip.giftList[x][1], reverse=True)



class Journey:
    
    def __init__(self, tripList):
        self.tripList = tripList
    
    def printJourney(self):
        for i in range( len(self.tripList) ):
            #print("Trip number " +str(i) + ":")
            self.tripList[i].printGifts()
        
    def printJourneyToFile(self, fileName, comment = "No comment provided"):
        
        f = open(fileName, "w")
        f.write(comment + "\n")
        f.write("SEED: " + str(SEED) + "\n")
        
        f.write("wrw score: " + str(6371.0*self.getJourneyWrw()) + "\n")
        f.write("TripId,GiftId\n")
        
        for i in range( len(self.tripList) ):
            nGiftsInTrip = self.tripList[i].getNumberOfGiftsInTrip()
            for j in range(nGiftsInTrip):
                giftId = self.tripList[i].getGiftIdAtPosition(j)
                f.write(str(i) + "," + str(giftId) + "\n")
        f.close()
                
        
    
    def pushTrip(self, trip):
        self.tripList.append(trip)
    
    def popTrip(self, i):
        return self.tripList.pop(i)
    
    def insertTrip(self, i, trip):
        self.tripList.insert(i,trip)
    
    def getJourneyWrw(self):
        wrw = 0.0
        for i in range(len(self.tripList)):
            wrw = wrw + self.tripList[i].getTripWrw()
        return wrw
    
    def getNumberOfGifts(self):
        N = 0
        for i in range(len(self.tripList)):
            N = N + self.tripList[i].getNumberOfGiftsInTrip()
        return N
    
    def sortTrips(self):
        for i in range(len(self.tripList)):
            self.tripList[i].sortTrip()
            
    def getNumberOfTrips(self):
        return len(self.tripList)

    
    def swapGiftsInRandomTrips(self, N):
        # for every trip N the positions of two gifts are swaped
        # the gifts are swaped in the same trip
        self.swapedTrips = [0 for i in range(N)]
        self.swapedGifts = [(0,0) for i in range(N)]
        for i in range(N):
            cNTrips = len(self.tripList)  
            swapTrip = rnd.randint( 0, cNTrips-1 )
            g1, g2 = self.tripList[swapTrip].swapGifts()
            
            self.swapedTrips[i] = swapTrip
            self.swapedGifts[i] = (g1,g2)

    def swapGiftsBetweenTwoNearestTrips(self):
        self.swapInformation = [0, 0, 0, 0, 0]
        
        N = self.getNumberOfTrips()
        firstTripId = rnd.randint( 0, N-1 )
        secondTripId= 0
        coinToss = rnd.randint(0, 1)
        
        if firstTripId == 0:
            if firstTripId == 0:
                if coinToss == 0:
                    secondTripId = 1
                else:
                    secondTripId = (N-1)
            elif firstTripId == (N-1):
                if coinToss == 0:
                    secondTripId = 1
                else:
                    secondTripId = (N-2)
            else:
                if coinToss == 0:
                    secondTripId = firstTripId + 1
                else:
                    secondTripId = firstTripId - 1
        
        self.swapInformation[1] = firstTripId
        self.swapInformation[2] = secondTripId
        
        fTrip = self.tripList[firstTripId]
        sTrip = self.tripList[secondTripId]
        
        firstGiftPosition = rnd.randint( 0, fTrip.getNumberOfGiftsInTrip() - 1 )
        secondGiftPosition = rnd.randint( 0, sTrip.getNumberOfGiftsInTrip() - 1 )
        
        self.swapInformation[3] = firstGiftPosition
        self.swapInformation[4] = secondGiftPosition
        
        fGiftId = fTrip.getGiftIdAtPosition(firstGiftPosition)
        sGiftId = sTrip.getGiftIdAtPosition(secondGiftPosition)
        
        fGiftWeight = Trip.giftList[fGiftId][3]
        sGiftWeight = Trip.giftList[sGiftId][3]
        
        if (fTrip.tripWeight - fGiftWeight + sGiftWeight < MAX_SLEIGH_WEIGHT) and \
            (sTrip.tripWeight - sGiftWeight + fGiftWeight < MAX_SLEIGH_WEIGHT):
            
            fTrip.giftIdList[firstGiftPosition] = sGiftId
            sTrip.giftIdList[secondGiftPosition] = fGiftId
            
            fTrip.tripWeight = fTrip.tripWeight - fGiftWeight + sGiftWeight
            sTrip.tripWeight = sTrip.tripWeight - sGiftWeight + fGiftWeight
            
            self.swapInformation[0] = 1
        else:
            self.swapInformation[0] = -1
        


    def reverseSwapGiftsBetweenTwoNearestTrips(self):
        
        if self.swapInformation[0] == 1:
        
            firstTripId = self.swapInformation[1]
            secondTripId = self.swapInformation[2]
            
            firstGiftPosition = self.swapInformation[3]
            secondGiftPosition = self.swapInformation[4]
            
            fTrip = self.tripList[firstTripId]
            sTrip = self.tripList[secondTripId]
            
            fGiftId = fTrip.getGiftIdAtPosition(firstGiftPosition)
            sGiftId = sTrip.getGiftIdAtPosition(secondGiftPosition)
            
            fTrip.giftIdList[firstGiftPosition] = sGiftId
            sTrip.giftIdList[secondGiftPosition] = fGiftId
            
            fGiftWeight = Trip.giftList[fGiftId][3]
            sGiftWeight = Trip.giftList[sGiftId][3]
            
            fTrip.tripWeight = fTrip.tripWeight - fGiftWeight + sGiftWeight
            sTrip.tripWeight = sTrip.tripWeight - sGiftWeight + fGiftWeight
            
            
        else:
            pass
        

    


    def reverseGiftSwapsInTrips(self):
        for i in range(len(self.swapedTrips)-1,-1,-1):
            self.tripList[self.swapedTrips[i]].reverseSwap(self.swapedGifts[i][0], self.swapedGifts[i][1])
        

    def transferManyGiftsBetweenNearestTrips(self, nTransfers):
        self.transferType = [0 for i in range(nTransfers)]
        # -1 no transfer occured
        # 0 normal transfer
        # 1 transfer with trip deletion
        # 2 transfer with trip creation
        self.transferTripIds = [[0,0] for i in range(nTransfers)]
        self.transferGiftPositions = [[0,0] for i in range(nTransfers)]
        self.transferedGiftId = [0 for i in range(nTransfers)]
        
        for nT in range(nTransfers):
            N = len(self.tripList)
            #print("N: " + str(N))
            firstTripId = rnd.randint(0, N-1)
            #secondTripId = rnd.randint(0, math.floor(N + SECOND_TRIP_RANDINT_OFFSET ) )
            secondTripId = 0
            
            coinToss = rnd.randint(0, 1)
            if firstTripId == 0:
                if coinToss == 0:
                    secondTripId = 1
                else:
                    secondTripId = (N-1)
            elif firstTripId == (N-1):
                if coinToss == 0:
                    secondTripId = 1
                else:
                    secondTripId = (N-2)
            else:
                if coinToss == 0:
                    secondTripId = firstTripId +1
                else:
                    secondTripId = firstTripId -1
            
            randomGiftPosition1 = 0
            randomGiftPosition2 = 0
            #secondTripId = rnd.randint(0, math.floor(N + (4.0*N/99.0 + 95000.0/99.0 ) ) )
             
            
            #print("---Transfering---")
            
            self.transferTripIds[nT][0] = firstTripId
            self.transferTripIds[nT][1] = secondTripId 
    
            #print("First trip Id: " + str(self.transferTripIds[0]))
            #print("Second trip Id: " + str(self.transferTripIds[1]))
            
            numberOfGiftsInFirstTrip = self.tripList[firstTripId].getNumberOfGiftsInTrip()
            if (numberOfGiftsInFirstTrip == 1) and (secondTripId >= N):
                self.transferType[nT] = -1
                #print("No transfer")
                return 0
            if firstTripId == secondTripId:
                self.transferType[nT] = -1
                #print("No transfer")
                return 0
            
            giftId = 0
            if numberOfGiftsInFirstTrip == 1:
                giftId = self.tripList[firstTripId].giftIdList[0]
                self.popTrip(firstTripId)
                
                N = len(self.tripList)
                #print("N: " + str(N))
                secondTripId = rnd.randint(0, N-1)
                self.transferTripIds[nT][1] = secondTripId
                #print("Again sampling second trip Id: " + str(self.transferTripIds[1]))
                
                self.transferedGiftId[nT] = giftId
                self.transferType[nT] = 1
            else:
                randomGiftPosition1 = rnd.randint(0, numberOfGiftsInFirstTrip-1)
                giftId = self.tripList[firstTripId].popGift(randomGiftPosition1)
                
                
                self.transferGiftPositions[nT][0] = randomGiftPosition1
                self.transferedGiftId[nT] = giftId
                self.transferType[nT] = 0
            
            
            
            if secondTripId < N:
                numberOfGiftsInSecondTrip = self.tripList[secondTripId].getNumberOfGiftsInTrip()
                randomGiftPosition2 = rnd.randint(0, numberOfGiftsInSecondTrip)
                
                
                
                inserted = self.tripList[secondTripId].insertGift(randomGiftPosition2, giftId)
                if (inserted == False) and (numberOfGiftsInFirstTrip != 1):
                    self.tripList[firstTripId].insertGift(randomGiftPosition1, giftId)
                    self.transferType[nT] = -1
                    return 0
                
                if (inserted == False) and (numberOfGiftsInFirstTrip == 1):
                    oldTrip = Trip([], 0.0)
                    oldTrip.pushGift(giftId)
                    self.tripList.insert(firstTripId, oldTrip)
                    
                    self.transferType[nT] = -1
                    return 0
                
                self.transferGiftPositions[nT][1] = randomGiftPosition2
            else:
                newTrip = Trip([], 0.0)
                newTrip.pushGift(giftId)
                self.pushTrip(newTrip)
                
                
                self.transferTripIds[nT][1] = -1
                self.transferGiftPositions[nT][1] = -1
                self.transferType[nT] = 2
    


    def transferManyGiftsBetweenTrips(self, nTransfers):
        self.transferType = [0 for i in range(nTransfers)]
        # -1 no transfer occured
        # 0 normal transfer
        # 1 transfer with trip deletion
        # 2 transfer with trip creation
        self.transferTripIds = [[0,0] for i in range(nTransfers)]
        self.transferGiftPositions = [[0,0] for i in range(nTransfers)]
        self.transferedGiftId = [0 for i in range(nTransfers)]
        
        for nT in range(nTransfers):
            N = len(self.tripList)
            #print("N: " + str(N))
            firstTripId = rnd.randint(0, N-1)
            secondTripId = rnd.randint(0, math.floor(N + SECOND_TRIP_RANDINT_OFFSET ) )
            randomGiftPosition1 = 0
            randomGiftPosition2 = 0
            #secondTripId = rnd.randint(0, math.floor(N + (4.0*N/99.0 + 95000.0/99.0 ) ) )
             
            
            #print("---Transfering---")
            
            self.transferTripIds[nT][0] = firstTripId
            self.transferTripIds[nT][1] = secondTripId 
    
            #print("First trip Id: " + str(self.transferTripIds[0]))
            #print("Second trip Id: " + str(self.transferTripIds[1]))
            
            numberOfGiftsInFirstTrip = self.tripList[firstTripId].getNumberOfGiftsInTrip()
            if (numberOfGiftsInFirstTrip == 1) and (secondTripId >= N):
                self.transferType[nT] = -1
                #print("No transfer")
                return 0
            if firstTripId == secondTripId:
                self.transferType[nT] = -1
                #print("No transfer")
                return 0
            
            giftId = 0
            if numberOfGiftsInFirstTrip == 1:
                giftId = self.tripList[firstTripId].giftIdList[0]
                self.popTrip(firstTripId)
                
                N = len(self.tripList)
                #print("N: " + str(N))
                secondTripId = rnd.randint(0, N-1)
                self.transferTripIds[nT][1] = secondTripId
                #print("Again sampling second trip Id: " + str(self.transferTripIds[1]))
                
                self.transferedGiftId[nT] = giftId
                self.transferType[nT] = 1
            else:
                randomGiftPosition1 = rnd.randint(0, numberOfGiftsInFirstTrip-1)
                giftId = self.tripList[firstTripId].popGift(randomGiftPosition1)
                
                self.transferGiftPositions[nT][0] = randomGiftPosition1
                self.transferedGiftId[nT] = giftId
                self.transferType[nT] = 0
            
            
            
            if secondTripId < N:
                numberOfGiftsInSecondTrip = self.tripList[secondTripId].getNumberOfGiftsInTrip()
                randomGiftPosition2 = rnd.randint(0, numberOfGiftsInSecondTrip)
                inserted = self.tripList[secondTripId].insertGift(randomGiftPosition2, giftId)
                if (inserted == False) and (numberOfGiftsInFirstTrip != 1):
                    self.tripList[firstTripId].insertGift(randomGiftPosition1, giftId)
                    self.transferType[nT] = -1
                    return 0
                
                if (inserted == False) and (numberOfGiftsInFirstTrip == 1):
                    oldTrip = Trip([], 0.0)
                    oldTrip.pushGift(giftId)
                    self.tripList.insert(firstTripId, oldTrip)
                    
                    self.transferType[nT] = -1
                    return 0
                
                self.transferGiftPositions[nT][1] = randomGiftPosition2
            else:
                newTrip = Trip([], 0.0)
                newTrip.pushGift(giftId)
                self.pushTrip(newTrip)
                
                
                self.transferTripIds[nT][1] = -1
                self.transferGiftPositions[nT][1] = -1
                self.transferType[nT] = 2

        #print("Transfer type: " + str(self.transferType))
        
        #print("Gift position in first trip: " + str(self.transferGiftPositions[0]))
        #print("Gift position in second trip: " + str(self.transferGiftPositions[1]))
    
    def transferManyGiftsBack(self):
        
        for nT in range(len(self.transferType)-1,-1,-1):
            t = self.transferType[nT]
            
            
            if t == 0:
                firstTripId = self.transferTripIds[nT][0]
                secondTripId = self.transferTripIds[nT][1]
                
                
                giftId = self.tripList[secondTripId].popGift(self.transferGiftPositions[nT][1])
                #print("popped")
                self.tripList[firstTripId].insertGift(self.transferGiftPositions[nT][0], giftId)
                #print("inserted")
                
            elif t == 1:
                firstTripId = self.transferTripIds[nT][0]
                secondTripId = self.transferTripIds[nT][1]
                
                giftId = self.tripList[secondTripId].popGift(self.transferGiftPositions[nT][1])
                trip = Trip([], 0.0)
                trip.pushGift(giftId)
                self.tripList.insert(firstTripId, trip)
                
            elif t == 2: 
                firstTripId = self.transferTripIds[nT][0]
                
                giftId = self.tripList[-1].getGiftIdAtPosition(0)
                self.tripList.pop( len(self.tripList)-1 )
                
                self.tripList[firstTripId].insertGift(self.transferGiftPositions[nT][0], giftId)
            else:
                pass
                
    def makeNearestRandomState(self, nTransfers, nSwaps):
        self.transferManyGiftsBetweenNearestTrips(nTransfers)
        self.swapGiftsInRandomTrips(nSwaps)
    
        
    def makeRandomState(self, nTransfers ,nSwaps):
        self.transferManyGiftsBetweenTrips(nTransfers)
        #self.swapGiftsInRandomTrips(nSwaps)

    def reverseNearestRandomState(self):
        #self.reverseGiftSwapsInTrips()
        self.transferManyGiftsBack()
        
    def reverseRandomState(self):
        #self.reverseGiftSwapsInTrips()
        self.transferManyGiftsBack()


def readData(fileName):
    
    CSVReader = csv.reader(open(fileName), delimiter=',')
    dataList = list(CSVReader)
    
    return dataList[1:]


def hav(theta):
    return (1.0 - math.cos(theta))/2.0


def haversineD(lon1, lat1, lon2, lat2):
    # Earth radious. Not Relevant for the optimization.
    return 2.0*EARTH_R*math.asin( math.sqrt( hav(lat2 - lat1) + math.cos(lat1)*math.cos(lat2)*hav(lon2-lon1) ) )



def makeGiftList(data):
    
    
    giftList = [0 for i in range(len(data)+1)]
    giftList[0] = [-1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0]
    for i in range(len(data)):
        
        th = math.pi*float(data[i][1])/180.0
        ph = math.pi*float(data[i][2])/180.0
        
        cGiftID    = int(data[i][0])
        cLatitude  = th
        cLongitude = ph
        cWeight    = float(data[i][3])

        x = math.sin(math.pi/2.0 - th)*math.cos(ph)
        y = math.sin(math.pi/2.0 - th)*math.sin(ph)
        z = math.cos(math.pi/2.0 - th)
        
        X = x*math.sqrt(2.0/(1.0-z))
        Y = y*math.sqrt(2.0/(1.0-z))
        
        d = math.sqrt(X*X+Y*Y)
        
        dis = haversineD(0.0, math.pi/2.0, ph, th)
        
        giftList[i+1] = [cGiftID, cLatitude, cLongitude, cWeight, X, Y, d, 0, dis]
    
    return giftList


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


def getStraightTrips(dSortedGifts, gifts):
    
    
    listOfTrips = []
    
    for i in range(len(dSortedGifts)):
    #for i in range(1,2):
        if (i % 10000 == 0):
            print("i: " + str(i))
        hTable = []
        
        if gifts[ dSortedGifts[i][0] ][7] == 1:
            continue
        v0 = [ dSortedGifts[i][4], dSortedGifts[i][5] ]
        gifts[ dSortedGifts[i][0] ][7] = 1
        
        for j in range(1,len(gifts)):
            if (dSortedGifts[i][0] == gifts[j][0]):
                continue
            if gifts[j][7] == 1:
                continue
            
            vj = [gifts[j][4], gifts[j][5]]
            
            vD = [ vj[0] - v0[0], vj[1] - v0[1] ]
            #print(vD)
            #print(v0)
            #print(dot(v0, vD))
            #print(norm(v0))
            #print("norm(vD): " + str(norm(vD)))
            #print("asd: " + str(dot(v0, vD)/(norm(v0)*norm(vD))))
            cosTheta = dot(v0, vD)/(norm(v0)*norm(vD))
            if cosTheta > 1.0:
                cosTheta = 1.0
            if cosTheta < -1.0:
                cosTheta = -1.0
            th = math.acos( cosTheta )
            h = math.sin(th)*norm(vD)
            
            if th > math.pi/2.0:
                continue
            
            
            hTable.append( [h, gifts[j][0], th] )
        
        hTable = sorted(hTable, key=operator.itemgetter(0))
        
        #print("Printing hTable")
        #for t in range(80):
        #    print("t: " + str(t) + " row: "  + str(hTable[t]))
        
        cw = 0.0
        trip = []
        trip.append(gifts[ dSortedGifts[i][0] ])
        cw = cw + gifts[ dSortedGifts[i][0] ][3]
        for k in range(len(hTable)):
            if ((cw + gifts[ hTable[k][1] ][3]) > MAX_SLEIGH_WEIGHT ):
                continue
            if gifts[ hTable[k][1] ][7] == 1:
                continue
            if hTable[k][2] > math.pi/2.0:
                continue
            
            cw = cw + gifts[ hTable[k][1] ][3]
            trip.append(gifts[ hTable[k][1] ])
            gifts[ hTable[k][1] ][7] = 1 
        
        #print("Trip length: " + str(len(trip)))
        trip = sorted(trip, key = operator.itemgetter(8))
        listOfTrips.append(trip)
        
    return listOfTrips


def getCurvedTrips(phSortedGifts, massOffset = 0.0):
    
    giftsAdded = 0
    tripList = []
    while(True):
        #print("giftsAdded: " + str(giftsAdded))
        trip = []
        cw = 0.0
        for i in range(len(phSortedGifts)):
            if phSortedGifts[i][7] == 1:
                continue
            
            if (cw + phSortedGifts[i][3]) > MAX_SLEIGH_WEIGHT - massOffset:
                break
            
            cw = cw + phSortedGifts[i][3]
            trip.append(phSortedGifts[i])
            phSortedGifts[i][7] = 1
            giftsAdded = giftsAdded + 1
            
            if giftsAdded >= len(phSortedGifts):
                break
        
        #print("trip len: " + str(len(trip)))
        #print(trip[0])
        trip = sorted(trip, key=operator.itemgetter(8))
        tripList.append(trip)
        
        if giftsAdded >= len(phSortedGifts):
            break
        
    return tripList


def converttripListToJourney(phTripList):
    
    jo = Journey([])
    for i in range(len(phTripList)):
        t = Trip([], 0.0)
        for j in range(len(phTripList[i])):
            t.pushGift(phTripList[i][j][0])
        
        jo.pushTrip(t)
    return jo                          
  
  
            
def metropolisAlgManyTransfersAndSwaps(initialState, nIter, nTransfers, nSwaps, period = 100000):
    
    
    minimalJ = Journey([])
    wrw = 1000000000000000.0
    periodPrint = True
    start = time.time()
    for i in range(nIter):

        currentWrw = initialState.getJourneyWrw()
        if currentWrw < wrw:
            wrw = currentWrw
            if periodPrint == True:
                print("Minimal wrw: " + str(6371.0*wrw))
                initialState.printJourneyToFile("minimalJourney_exact_MH.dat", "we are at iteration: " + str(i))
                periodPrint = False
        if (i % period == 0):
            print("\n" + "We are at iteration: " + str(i))
            print("Number of trips in initial state: " + str(initialState.getNumberOfTrips()))
            print("Number of gifts in initial state: " + str(initialState.getNumberOfGifts()))
            print("Random  wrw: " + str(6371.0*currentWrw))
            initialState.printJourneyToFile("minimalJourney_random_probing_MH.dat", "we are at iteration: " + str(i))
            periodPrint = True
            end = time.time()
            print("time for " + str(period) + " iterations: " + str(end - start))
            start = time.time()
            
        initialState.makeRandomState(nTransfers, nSwaps)
        wrwN = initialState.getJourneyWrw()
        
        A = math.exp( currentWrw/EARTH_R - wrwN/EARTH_R)
        
        if rnd.random() < A:
            continue
        else:
            initialState.reverseRandomState()
            
    return wrw


def randomSearch(initialState, nIter, nTransfers, nSwaps, period = 100000):
    
    wrw = 1000000000000000.0
    currentWrw = initialState.getJourneyWrw()
    periodPrint = True
    weSwapwsGiftsBetweenTwoNearestTrips = True
    
    start = time.time()
    for i in range(nIter):
        
        if currentWrw < wrw:
            wrw = currentWrw
            if periodPrint == True:
                print("Current minimal wrw: " + str(6371.0*wrw))
                initialState.printJourneyToFile("x_random_search_minimal.dat", "we are at iteration: " + str(i))
                periodPrint = False
        if (i % period == 0):
            print("\n" + "We are at iteration: " + str(i))
            print("Number of trips in initial state: " + str(initialState.getNumberOfTrips()))
            print("Number of gifts in initial state: " + str(initialState.getNumberOfGifts()))
            initialState.printJourneyToFile("x_random_search.dat", "we are at iteration: " + str(i))
            periodPrint = True
            end = time.time()
            print("time: " + str(end - start))
            start = time.time()
        
        if i % 2 == 0:
            initialState.makeNearestRandomState(nTransfers, nSwaps)
            weSwapwsGiftsBetweenTwoNearestTrips = False
        else:
            initialState.swapGiftsBetweenTwoNearestTrips()
            weSwapwsGiftsBetweenTwoNearestTrips = True
        
        wrwN = initialState.getJourneyWrw()
        
        if wrwN < currentWrw:
            currentWrw = wrwN
            continue
        else:
            if weSwapwsGiftsBetweenTwoNearestTrips == True:
                pass
                initialState.reverseSwapGiftsBetweenTwoNearestTrips()
            else:
                initialState.reverseNearestRandomState()


def shuffleGifts(giftList):
    
    randomGiftList = [giftList[i] for i in range(len(giftList))]
    rnd.shuffle(randomGiftList)
    return randomGiftList  


def makeRandomJourney(gifts, maxGiftsInTrip):
    
    randomGiftList = shuffleGifts(gifts[1:])
    randomGiftList.insert(0, 0)
    nGifts = 1
    
    randomJourney = Journey([])
    
    while(True):
        nGiftsInTrip = rnd.randint(1, maxGiftsInTrip)
        trip = Trip([], 0.0)
        for i in range(nGiftsInTrip):
            if nGifts > NUMBER_OF_GIFTS:
                break
            if trip.pushGift( randomGiftList[nGifts][0] ):
                nGifts = nGifts + 1
            else:
                randomJourney.pushTrip(trip)
                break
        randomJourney.pushTrip(trip)
        if nGifts > NUMBER_OF_GIFTS:
            break
    
    return randomJourney


def makeSampleJournay(sampleSubmissionData):
    N = int(sampleSubmissionData[-1][1])+1
    tripList = [Trip([], 0.0) for i in range(N)]
    
    for i in range(len(sampleSubmissionData)):
        gId = int(sampleSubmissionData[i][0])
        tId = int(sampleSubmissionData[i][1])
        
        tripList[tId].pushGift(gId)
    
    return Journey(tripList)


def makeRandomJourneyCluster(giftsInClusters, maxGiftsInTrip):
    
    
    randomGiftList = shuffleGifts(giftsInClusters)
    NUMBER_OF_GIFTS_IN_CLUSTERS = len(randomGiftList)
    nGifts = 1
    
    randomJourney = Journey([])
    
    while(True):
        nGiftsInTrip = rnd.randint(1, maxGiftsInTrip)
        trip = Trip([], 0.0)
        for i in range(nGiftsInTrip):
            if nGifts >= NUMBER_OF_GIFTS_IN_CLUSTERS:
                break
            if trip.pushGift( randomGiftList[nGifts][0] ):
                nGifts = nGifts + 1
            else:
                randomJourney.pushTrip(trip)
                break
        randomJourney.pushTrip(trip)
        
        if nGifts >= NUMBER_OF_GIFTS_IN_CLUSTERS:
            break
    
    return randomJourney






giftsFileName = "gifts.csv"
data = readData(giftsFileName)
gifts = makeGiftList(data)
Trip.giftList = gifts

# Checking the sample submission
sampleSubmissionData = readData("sample_submission.csv")
js = makeSampleJournay(sampleSubmissionData)

print("Number of trips: " + str(js.getNumberOfTrips()))
print("Number of gifts: " + str(js.getNumberOfGifts()))
print("Sample trips wrw: " + str(6371.0*js.getJourneyWrw()))

# Metropolis approach (simple short examples)
numberOfIterations = 100000000

giftsClusterFileName = "gifts100.csv"
clusterData = readData(giftsClusterFileName)
giftsInClusters = makeGiftList(clusterData)


jo = makeRandomJourneyCluster(giftsInClusters, 1)
metropolisAlgManyTransfersAndSwaps(jo, numberOfIterations, 1, 1, 100000)

# Metropolis approach (all data)

#jo = makeRandomJourney(gifts, 3)
#print("Random state (journey) wrw: " + str(6371.0*jo.getJourneyWrw()))


#metropolisAlgManyTransfersAndSwaps(jo, numberOfIterations, 1, 1)


# Random search approach

#print("\nMaking curved trips...")
#lonSortedGifts = sorted(gifts[1:], key=operator.itemgetter(2), reverse=True)
#bareTripList = getCurvedTrips(lonSortedGifts, 50.0)

#print("Converting to journey...")
#jo = converttripListToJourney(bareTripList)
#print("Initial curved trips wrw: " + str(6371.0*jo.getJourneyWrw()))
#randomSearch(jo, 10000000, 1, 0, 100000)





