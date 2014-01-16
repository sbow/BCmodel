# StrategyModel1.py
# 2014/01/04
# Shaun Bowman
# Simple model that waits for a target % profit to appear and then executes

# Given:    Start datetime
# Outputs:  Execution datetime

#['CycleNumber','BuyDatetime','BuyBalanceCAD','BuyExchange','BuyCavirtexPriceCAD','BuyBalanceBTC','BuyBitstampPriceUSD','BuyModeledProfit','BuyTargetProfit','SellDatetime','SellCavirtexPriceCAD','SellBitstampPriceUSD','SellBalanceUSD','TransferOrderDatetime','TransferOrderBalanceCAD','TransferOrderExchange','ExchangeFee'])

# Setup:
setTargetProfit = 0.05 # n*100 = target profit
setModelTimestep   = 120   # s, rate at which model runs
setModelFees    = 0 # USD/BTC, total fees, expressed per unit BTC (simplification)

__author__ = 'shaun'

import datetime, collections

class StrategyModel1(object):
    initialDatetime = []
    timeoutDatetime = []
    exchangeUSDCADObject = []
    bitstampTransactionObject = []
    cavirtexTransactionObject = []
    targetProfit = float(setTargetProfit)
    modelTimestep = float(setModelTimestep)
    modelFees = float(setModelFees)

    __datetimeCurrent = []

    indexes = collections.namedtuple('Indexes', ['bitstamp','cavirtex','exchange'])
    returnBuyDecision = collections.namedtuple('ReturnResult', ['decisionTime', 'bSuccess', 'currentIndicies'])

    def __init__(self, exchangeUSDCADObject, bitstampTransactionObject, cavirtexTransactionObject, targetProfit):
        self.exchangeUSDCADObject = exchangeUSDCADObject
        self.bitstampTransactionObject = bitstampTransactionObject
        self.cavirtexTransactionObject = cavirtexTransactionObject
        self.targetProfit = float(targetProfit)

    def getTargetProfit(self):
        return self.targetProfit

    def runStrategy(self, initialDatetime):
        # print "Running Strategy" #debug
        self.initialDatetime = initialDatetime
        self.__datetimeCurrent = self.initialDatetime
        initialIndicies = self.__findIndiciesForTime(self.initialDatetime)
        # print self.exchangeUSDCADObject[initialIndicies.exchange] #debug
        # print self.bitstampTransactionObject[initialIndicies.bitstamp] #debug
        # print self.cavirtexTransactionObject[initialIndicies.cavirtex] #debug

        if all( i > -1 for i in initialIndicies): # success, found initial time in all datasets
            self.__datetimeCurrent = self.initialDatetime
            currentIndicies = initialIndicies

            nItems = [len(self.bitstampTransactionObject), len(self.cavirtexTransactionObject), len(self.exchangeUSDCADObject)]
            nItemsLeft = [nItems[i] - currentIndicies[i] for i,n in enumerate(nItems)] # note: assumes order is bitstamp,cavirtex,exchange

            nItemsLeftMin = min(nItemsLeft)
            bSuccess = False

            while nItemsLeftMin > 10 and not(bSuccess): # note: this should be nItemsLeftMin > 0 but it fails for some reason... (inf loop)
                currentUSDCADExchange   = float(self.exchangeUSDCADObject[currentIndicies.exchange]['high'])
                currentCavirtexSale     = float(self.cavirtexTransactionObject[currentIndicies.cavirtex]['price'])
                currentBitstampSale     = float(self.bitstampTransactionObject[currentIndicies.bitstamp]['price'])

                currentModeledProfit    = currentBitstampSale/(currentCavirtexSale/currentUSDCADExchange + self.modelFees) - 1

                metTarget = currentModeledProfit > self.targetProfit

                if not metTarget: # haven't met the target, go to next time & get new indicies
                    self.__datetimeCurrent = self.__datetimeCurrent + datetime.timedelta(0,self.modelTimestep)
                    currentIndicies = self.__findIndiciesForTimeWithStart(self.__datetimeCurrent,currentIndicies)
                    nItems = [len(self.bitstampTransactionObject), len(self.cavirtexTransactionObject), len(self.exchangeUSDCADObject)]
                    nItemsLeft = [nItems[i] - currentIndicies[i] for i,n in enumerate(nItems)] # note: assumes order is bitstamp,cavirtex,exchange
                    nItemsLeftMin = min(nItemsLeft)
                    currentTIme = self.__datetimeCurrent
                    # print "fail time:", str(self.__datetimeCurrent) # debug
                    # print "nItemsLeftMin: ", nItemsLeftMin # debug
                    # print "currentUSDCADExchange: ", currentUSDCADExchange # debug
                    # print "currentCavirtexSale: ", currentCavirtexSale # debug
                    # print "currentBitstampSale: ", currentBitstampSale # debug
                    # print "currentModeledProfit: ", currentModeledProfit # debug
                    # print "currentModeledProfit: ", currentModeledProfit # debug

                else:
                    bSuccess = True
                    # print "Success time: ", str(self.__datetimeCurrent) # debug
                    # print "currentUSDCADExchange: ", currentUSDCADExchange # debug
                    # print "currentCavirtexSale: ", currentCavirtexSale # debug
                    # print "currentBitstampSale: ", currentBitstampSale # debug
                    # print "currentModeledProfit: ", currentModeledProfit # debug
                    # print "targetProfit: ", self.targetProfit # debug

        return self.returnBuyDecision(decisionTime=self.__datetimeCurrent, bSuccess=bSuccess, currentIndicies=currentIndicies)

    def runStrategyWithStart(self, initialDatetime,startIndicies):
        # print "Running Strategy with start" #debug
        self.initialDatetime = initialDatetime
        self.__datetimeCurrent = self.initialDatetime
        initialIndicies = self.__findIndiciesForTimeWithStart(self.initialDatetime, startIndicies)
        # print self.exchangeUSDCADObject[initialIndicies.exchange] #debug
        # print self.bitstampTransactionObject[initialIndicies.bitstamp] #debug
        # print self.cavirtexTransactionObject[initialIndicies.cavirtex] #debug

        if all( i > -1 for i in initialIndicies): # success, found initial time in all datasets
            self.__datetimeCurrent = self.initialDatetime
            currentIndicies = initialIndicies

            nItems = [len(self.bitstampTransactionObject), len(self.cavirtexTransactionObject), len(self.exchangeUSDCADObject)]
            nItemsLeft = [nItems[i] - currentIndicies[i] for i,n in enumerate(nItems)] # note: assumes order is bitstamp,cavirtex,exchange

            nItemsLeftMin = min(nItemsLeft)
            bSuccess = False

            while nItemsLeftMin > 10 and not(bSuccess): # note: this should be nItemsLeftMin > 0 but it fails for some reason... (inf loop)
                currentUSDCADExchange   = float(self.exchangeUSDCADObject[currentIndicies.exchange]['high'])
                currentCavirtexSale     = float(self.cavirtexTransactionObject[currentIndicies.cavirtex]['price'])
                currentBitstampSale     = float(self.bitstampTransactionObject[currentIndicies.bitstamp]['price'])

                currentModeledProfit    = currentBitstampSale/(currentCavirtexSale/currentUSDCADExchange + self.modelFees) - 1

                metTarget = currentModeledProfit > self.targetProfit

                if not metTarget: # haven't met the target, go to next time & get new indicies
                    self.__datetimeCurrent = self.__datetimeCurrent + datetime.timedelta(0,self.modelTimestep)
                    currentIndicies = self.__findIndiciesForTimeWithStart(self.__datetimeCurrent,currentIndicies)
                    nItems = [len(self.bitstampTransactionObject), len(self.cavirtexTransactionObject), len(self.exchangeUSDCADObject)]
                    nItemsLeft = [nItems[i] - currentIndicies[i] for i,n in enumerate(nItems)] # note: assumes order is bitstamp,cavirtex,exchange
                    nItemsLeftMin = min(nItemsLeft)
                    currentTIme = self.__datetimeCurrent
                    # print "fail time:", str(self.__datetimeCurrent) # debug
                    # print "nItemsLeftMin: ", nItemsLeftMin # debug
                    # print "currentUSDCADExchange: ", currentUSDCADExchange # debug
                    # print "currentCavirtexSale: ", currentCavirtexSale # debug
                    # print "currentBitstampSale: ", currentBitstampSale # debug
                    # print "currentModeledProfit: ", currentModeledProfit # debug
                    # print "currentModeledProfit: ", currentModeledProfit # debug

                else:
                    bSuccess = True
                    # print "Success time: ", str(self.__datetimeCurrent) # debug
                    # print "currentUSDCADExchange: ", currentUSDCADExchange # debug
                    # print "currentCavirtexSale: ", currentCavirtexSale # debug
                    # print "currentBitstampSale: ", currentBitstampSale # debug
                    # print "currentModeledProfit: ", currentModeledProfit # debug
                    # print "targetProfit: ", self.targetProfit # debug

        return self.returnBuyDecision(decisionTime=self.__datetimeCurrent, bSuccess=bSuccess, currentIndicies=currentIndicies)


    def __findIndiciesForTime(self,timeTarget):
        indexCavirtex = -1
        indexBitstamp = -1
        indexUSDCAD = -1

        for index, entry in enumerate(self.cavirtexTransactionObject):
            if entry['datetime'] >= timeTarget:
                indexCavirtex = index - 1 #note: fails on edge cases
            if indexCavirtex > -1:
                break

        for index, entry in enumerate(self.bitstampTransactionObject):
            if entry['datetime'] >= timeTarget:
                indexBitstamp = index - 1 #note: fails on edge cases
            if indexBitstamp > -1:
                break

        for index, entry in enumerate(self.exchangeUSDCADObject):
            if entry['datetime'] >= timeTarget:
                indexUSDCAD = index - 1 #note: fails on edge cases
            if indexUSDCAD > -1:
                break

        return self.indexes(bitstamp=indexBitstamp, cavirtex=indexCavirtex, exchange=indexUSDCAD)

    def __findIndiciesForTimeWithStart(self,timeTarget,startIndicies):
        indexCavirtex = -1
        indexBitstamp = -1
        indexUSDCAD = -1

        for index, entry in enumerate(self.cavirtexTransactionObject[startIndicies.cavirtex:]):
            if entry['datetime'] >= timeTarget:
                indexCavirtex = index + startIndicies.cavirtex - 1 #note: fails on edge cases
                break

        for index, entry in enumerate(self.bitstampTransactionObject[startIndicies.bitstamp:]):
            if entry['datetime'] >= timeTarget:
                indexBitstamp = index + startIndicies.bitstamp - 1 #note: fails on edge cases
                break

        for index, entry in enumerate(self.exchangeUSDCADObject[startIndicies.exchange:]):
            if entry['datetime'] >= timeTarget:
                indexUSDCAD = index + startIndicies.exchange - 1 #note: fails on edge cases
                break

        return self.indexes(bitstamp=indexBitstamp, cavirtex=indexCavirtex, exchange=indexUSDCAD)