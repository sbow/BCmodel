# Offline Bitcoin
# Consumes output of ParseCsv.py (creates a cPickle file with bitcoin transactions from Cavirtex & Bitstamp, and USD / CAD exchange rates
# 2013 / 01 / 02

__author__ = 'shaun'

import cPickle, datetime, WorldModel, StrategyModel1

fileBitstampPkl = 'bitcoinDataBitstamp.pkl'
fileCavirtexPkl = 'bitcoinDataCavirtex.pkl'
fileDukascopyUSDCADPkl = 'dukascopyUSDCAD20112014.pkl'

data = [] # data, format: data[0][:] = Cavirtex, data[1][:] = Bitstamp, data[2][:] = USD/CAD exchange

timestart = datetime.datetime.now()

with open(fileCavirtexPkl, 'r') as pklFile:
    dataCavirtex = cPickle.load(pklFile)

with open(fileBitstampPkl, 'r') as pklFile:
    dataBitstamp = cPickle.load(pklFile)

with open(fileDukascopyUSDCADPkl, 'r') as pklFile:
    dataUSDCAD = cPickle.load(pklFile)

# these print's below display start & end line items of the given datasets (commented out by default, used for debugging)
# print dataCavirtex[0]
# print dataCavirtex[-1]
# print dataBitstamp[0]
# print dataBitstamp[-1]
# print dataUSDCAD[0]
# print dataUSDCAD[-1]


# SETUP parameters
worldInitialDatetime = dataUSDCAD[-100000]['datetime']
print "Initial Time: ", str(worldInitialDatetime)

strategyString = 'Strategy1'
worldNloops = 3
worldInitialCavirtexFunding = float(10000)
targetProfit = 0.06

# RUN
modelTradeModel = StrategyModel1.StrategyModel1(dataUSDCAD,dataBitstamp,dataCavirtex,targetProfit)
modelWorld = WorldModel.WorldModel(worldInitialDatetime, worldNloops, worldInitialCavirtexFunding, modelTradeModel, dataBitstamp, dataCavirtex, dataUSDCAD, strategyString)


print modelWorld.runWorld()
modelWorld.postProc()

# REVIEW
print modelWorld.printCycle()
print modelWorld.storeCycle()

timeend = datetime.datetime.now()
print str(timeend - timestart)