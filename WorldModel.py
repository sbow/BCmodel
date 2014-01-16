# WorldModel.py
# 2014/01/04
# Shaun Bowman
# Models the "world", meaning the world outside of the trade decision strategy

# Given:    Initial datetime, Number of trade loops, Initial Cavirtex funding, Trade model object
# Outputs:  Final USD Bank Balance, USD Bank Balance timeseries

# Setup: Delays, USD/CAD Exchange timeseries data object, Bitstamp transaction timeseries data object, Cavirtex transaction timeseries object.
delayOrderExecution         = 30        #(s), delay between Cavirtex BTC order to buy is made & Cavirtex has purchased them
delayBuyPossesion           = 240       #(s), delay between Cavirtex purchasing & your account having bitcoin in posesion
delayBitcoinTransfer        = 240       #(s), delay between BTC posession on Cavirtex & decision to transfer to Bitstamp
delaySaleDecision           = 240       #(s), delay between BTC posession on Bitstamp & decision to sell on Bitstamp (Note: sale itself is assumed to be instant... incorrect)
delayWithdrawlDecision      = 600       #(s), delay between USD pocession on Bitstamp & decision to withdrawl to US Bank
delayBitstampWithdrawl      = 60*60*24  #(s), delay between USD decision to transfer from Bitstamp to US Bank and funds available in US Bank
delayExchangeDecision       = 600       #(s), delay between USD posession in US Bank and decision to exchange funds to CDN Bank
delayUSDCADExchange         = 60*60*24*4#(s), delay between US Bank posession and CDN Bank possesion (ie: Exchange delay)
delayBankCavirtexDecision   = 60*60*4   #(s), delay between CDN Bank posession and action/decision to transfer to Cavirtex
delayBankCavirtexDeposit    = 60*60*4   #(s), delay between action to transfer from CDN Bank to Cavirtex & funts available in Cavirtex
feeBitstampWithdrawl        = 0         #($USD), withdrawl fee from Bitstamp (constant)
feeBitstampWithdrawlPct     = float(0.01) #(1/100%), fee charged to withdrawl money from bitstamp / coinbase. TransferedFunds = BitstampFunds*(1-ThisConstant)
feeCavirtexDeposit          = 5         #($CAD), deposit fee to Cavirtex from CA bank
feeExchangePercentage       = float(0.02)      #(1/100%), fee ontop of actual exchange rate charged by USBank for doing an exchange & transfer to CABank
feeCavirtexPurchasePct         = float(0.015) #(1/100%), fee charged ontop of Cavirtex BTC purchase price, paid at time of purchase

__author__ = 'shaun'

import datetime, collections, csv

# World Model Class
class WorldModel(object):
    initialDatetime  = []
    numberTradeLoops = []
    initialCavirtexFunding = []
    trademodelObject = []
    exchangeUSDCADObject = []
    bitstampTransactionObject = []
    cavirtexTransactionObject = []
    timeMinEndOfDataObjects = []
    strategyString = []
    cycleInfo = []
    overallInfo = {}
    modelState = []

    __balanceCavirtexCAD = float(0)
    __balanceCavirtexBTC = float(0)
    __balanceBitstampUSD = float(0)
    __balanceBitstampBTC = float(0)
    __balanceUsbankUSD = float(0)
    __balanceCabankCAD = float(0)

    __timeCurrent = []

    __returnBuyDecision = []
    __timeBuyDecision = []
    __bSuccessBuyDecision = []

    indexes = collections.namedtuple('Indexes', ['bitstamp','cavirtex','exchange'])
    returnBuyDecision = collections.namedtuple('ReturnResult', ['decisionTime', 'bSuccess', 'currentIndicies'])

    def __init__(self, initialDatetime, numberTradeLoops, initialCavirtexFunding, trademodelObject, bitstampTransactionObject, cavirtexTransactionObject, exchangeUSDCADObject, strategyString):
        self.initialDatetime = initialDatetime
        self.numberTradeLoops = numberTradeLoops
        self.initialCavirtexFunding = initialCavirtexFunding
        self.__balanceCavirtexCAD = int(self.initialCavirtexFunding)
        self.trademodelObject = trademodelObject
        self.bitstampTransactionObject = bitstampTransactionObject
        self.cavirtexTransactionObject = cavirtexTransactionObject
        self.exchangeUSDCADObject = exchangeUSDCADObject
        self.timeMinEndOfDataObjects = min([self.bitstampTransactionObject[-1]['datetime'], self.cavirtexTransactionObject[-1]['datetime'], self.exchangeUSDCADObject[-1]['datetime']])
        self.strategyString = strategyString

    # runWorld: public WorldModel, this is the main function. When called the world model executes, also executes strategy
    def runWorld(self):
        self.__runWorld()
        return "World Running!"

    # __runWorld: private WorldModel, the numbers "# X)..." reference the powerpoint presentation I made
    def __runWorld(self):
        self.__timeCurrent = self.initialDatetime
        self.__retainedIndicies = [0]
        for cycle in range(0, self.numberTradeLoops):

            print "Cycle: ", cycle

            self.cycleInfo.append({'a: CycleNumber':cycle})
            self.cycleInfo[cycle]['b: BuyStratStartDateTime'] = self.__timeCurrent

            # 1) Buy Decision:
            self.modelState = 'Buy Decision'
            if (self.__timeCurrent == self.initialDatetime):
                self.returnBuyDecision = self.trademodelObject.runStrategy(self.initialDatetime)
            else:
                self.returnBuyDecision = self.trademodelObject.runStrategyWithStart(self.__timeCurrent, self.__retainedIndicies)

            self.cycleInfo[cycle]['c: BuyDatetime'] = self.returnBuyDecision.decisionTime
            self.__returnBuyDecision = self.returnBuyDecision
            self.__timeBuyDecision = self.__returnBuyDecision.decisionTime
            self.__bSuccessBuyDecision = self.__returnBuyDecision.bSuccess
            currentIndicies = self.__returnBuyDecision.currentIndicies

            if not self.__bSuccessBuyDecision:  # model failed to find time to execute trade
                break

            # 1.action) Delay Cavirtex Order Execution
            self.__timeCurrent = self.__timeBuyDecision + datetime.timedelta(0, delayOrderExecution)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 2) Cavirtex Buy Execution - modeled as infinitely stiff market, ie: can buy at last transaction price
            self.modelState = 'Cavirtex Buy Execution'
            currentIndicies = self.__findIndiciesForTimeWithStart(self.__timeCurrent, currentIndicies) # find new time after order delay
            self.__balanceCavirtexBTC = self.__balanceCavirtexCAD / (float(self.cavirtexTransactionObject[currentIndicies.cavirtex]['price'])*(1.0+feeCavirtexPurchasePct)) # purchase, uses all available money. Including purchase % fee

            self.cycleInfo[cycle]['d: BuyBalanceCAD'] = self.__balanceCavirtexCAD
            self.cycleInfo[cycle]['e: BuyBalanceBTC'] = self.__balanceCavirtexBTC
            self.cycleInfo[cycle]['f: ExchangeAtBuyTime'] = float(self.exchangeUSDCADObject[currentIndicies.exchange]['high'])
            self.cycleInfo[cycle]['g: BuyBitstampPriceUSD'] = float(self.bitstampTransactionObject[currentIndicies.bitstamp]['price'])
            self.cycleInfo[cycle]['h: BuyCavirtexPriceCAD'] = float(self.cavirtexTransactionObject[currentIndicies.cavirtex]['price'])
            self.__balanceCavirtexCAD = float(0) # update CA bank balance

            # 2.action) Delay buy possesion:
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayBuyPossesion)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 3) Cavirtex Posession
            self.modelState = 'Cavirtex Possession'

            # 3.action) Delay Bitcoin Transfer
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayBitcoinTransfer)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 4) Bitstamp Possession - transfer funds from cavirtex to bitstamp
            self.modelState = 'Bitstamp Possession'
            self.__balanceBitstampBTC = self.__balanceCavirtexBTC # transfer bitcoin to Bitstamp
            self.__balanceCavirtexBTC = 0 # assumes transfer is total

            # 4.action) Delay Sale
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delaySaleDecision)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 5) Bitstamp Sale - Assumes total sale
            self.modelState = 'Bitstamp Sale'
            currentIndicies = self.__findIndiciesForTimeWithStart(self.__timeCurrent, currentIndicies) # find indicies at current time
            currentBTCBitstampPriceUSD = float(self.bitstampTransactionObject[currentIndicies.bitstamp]['price']) # get current bitstamp price
            self.__balanceBitstampUSD = self.__balanceBitstampBTC * currentBTCBitstampPriceUSD # sale model
            
            self.cycleInfo[cycle]['i: SellDatetime'] = self.__timeCurrent
            self.cycleInfo[cycle]['j: SellCavirtexPriceCAD'] = float(self.cavirtexTransactionObject[currentIndicies.cavirtex]['price'])
            self.cycleInfo[cycle]['k: SellBitstampPriceUSD'] = currentBTCBitstampPriceUSD
            self.cycleInfo[cycle]['l: SellBalanceUSD'] = self.__balanceBitstampUSD

            # 5.action) Delay withdrawl decision
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayWithdrawlDecision)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 6) Bitstamp Withdrawl - transfer from bitstamp to USBank; with fee:
            self.modelState = 'Bitstamp Withdrawl'
            self.__balanceUsbankUSD = (self.__balanceBitstampUSD - feeBitstampWithdrawl)*(1.0-feeBitstampWithdrawl)
            self.__balanceBitstampUSD = 0
            # print "6) time at Bitstamp withdrawl to US Bank decision: ", str(self.__timeCurrent)

            # 6.action) Bitstamp withdrawl delay
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayBitstampWithdrawl)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 7) US Bank funds available
            self.modelState = 'US Bank Funds Available'
            # print "6.action) Time at US Funds Available: ", str(self.__timeCurrent)

            # 7.action) Delay exchange decision
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayExchangeDecision)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 8) US Bank transfer Order
            self.modelState = 'US Bank Tranfer Order'
            currentIndicies = self.__findIndiciesForTimeWithStart(self.__timeCurrent, currentIndicies) # find indicies at time of exchange USD to CAD
            currentExchangeRate = float(self.exchangeUSDCADObject[currentIndicies.exchange]['high']) # get current exchange rate
            self.__balanceCabankCAD = self.__balanceUsbankUSD * (currentExchangeRate - feeExchangePercentage) # do exchange
            self.__balanceUsbankUSD = 0 # update US Bank balance
            self.cycleInfo[cycle]['m: TransferOrderDatetime'] = self.__timeCurrent
            self.cycleInfo[cycle]['n: TransferOrderBalanceCAD'] = self.__balanceCabankCAD
            self.cycleInfo[cycle]['o: ExchangeAtTransferOrder'] = currentExchangeRate
            self.cycleInfo[cycle]['p: ExchangeFee'] = feeExchangePercentage

            # 8.action) USDCAD Exchange delay
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayUSDCADExchange)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 9) CA Bank funded
            self.modelState = 'CA Bank Funded'
            self.cycleInfo[cycle]['q: CaBankReFundedDatetime'] = self.__timeCurrent

            # 9.action) Delay bank carirtex transfer decision
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayBankCavirtexDecision)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 10) CA Bank Cavirtex Transfer
            self.modelState = 'CA Bank Cavirtex Transfer'
            self.__balanceCavirtexCAD = self.__balanceCabankCAD - feeCavirtexDeposit # transfer all available money, less transfer fee
            self.__balanceCabankCAD = 0

            # 10.action) Delay bank Cavirtex deposit
            self.__timeCurrent = self.__timeCurrent + datetime.timedelta(0, delayBankCavirtexDeposit)
            if self.__timeCurrent >= self.timeMinEndOfDataObjects: # exceeded a dataset
                break

            # 11) Cavitex funded
            self.modelState = 'Cavirtex Funded'
            self.cycleInfo[cycle]['r: CavitexFundedDatetime'] = self.__timeCurrent

            self.__retainedIndicies = currentIndicies # for start of next loop  / trade

        print "Final Cavirtex Ballance CAD: ", str(self.__balanceCavirtexCAD) # debug
        print "Final datetime: ", str(self.__timeCurrent) # debug

    # __findIndiciesForTimeWithStart: given a target date & time, search through the 3 objects & return the INDEX of
    # the transaction / exchange just prior
    # startIndicies are the indicies from which to start searching (the objects are large, this speeds it up a bit)
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

    # postProc: run some calcs on data
    def postProc(self):
        startDate = self.cycleInfo[0]['b: BuyStratStartDateTime']
        endDate = self.cycleInfo[-1]['r: CavitexFundedDatetime']
        nDaysDuration   = float((endDate - startDate).total_seconds()/float( 24*60*60 )) # convert to seconds in order to get decimal form of days
        nDollarsProfit  = self.cycleInfo[-1]['n: TransferOrderBalanceCAD'] - self.cycleInfo[0]['d: BuyBalanceCAD'] # profit is positive, loss negative
        nDollarsPerDay  = nDollarsProfit / nDaysDuration
        nTotalFeesPct   = feeExchangePercentage + feeBitstampWithdrawlPct + feeCavirtexPurchasePct
        nTotalFeesFixed   = feeBitstampWithdrawl + feeCavirtexDeposit # does not account for exchange rate, note: mixes CAD & USD

        nNormDollarsPerDay = nDollarsPerDay / float(self.initialCavirtexFunding) # dollars per day, normalized by initial funding (not the same as % per day)
        self.overallInfo = {'a: iniCavirtex$CAD':self.initialCavirtexFunding, 'b: finalCaBank$CAD':self.cycleInfo[-1]['n: TransferOrderBalanceCAD'], 'c: nDaysDuration':str(nDaysDuration), 'd: nDollarsProfit':nDollarsProfit, 'e: nDollarsPerDay':str(nDollarsPerDay), 'f: nNormDollarsPerDay':str(nNormDollarsPerDay), 'g: targetProf':int(100*self.trademodelObject.getTargetProfit()), 'h: totalPctFees':str(nTotalFeesPct) }
        strPrintStr = ""
        for key in sorted(self.overallInfo):
            strPrintStr = strPrintStr + '|' + key.rjust(18) + ' - ' + str(self.overallInfo[key]).ljust(20)
        strPrintStr = strPrintStr + '|' + "\n"
        print strPrintStr
        return

    # printCycle: print data to standard output, each row is a trade loop, steps run left to right in time
    def printCycle(self):
        PrintString = ""
        for cycle in self.cycleInfo:
            for key in sorted(cycle):
                PrintString = PrintString + '|' + key.rjust(18) + ' - ' + str(cycle[key]).ljust(20)
            PrintString = PrintString + '|' + "\n"
        print PrintString
        return

    # storeCycle: output data to csv, each row is a trade loop, steps run left to right in time
    def storeCycle(self):
        storeFileDatetime = self.initialDatetime.strftime('%Y_%m_%d__%H-%M-%S')
        storeFilename = storeFileDatetime + ' ' + self.strategyString + ' ' + str(self.numberTradeLoops) +'Loops' + ' ' + str(int(100*self.trademodelObject.getTargetProfit())) + 'PctTgt' + ' ' + str(int(self.initialCavirtexFunding)) + 'IniCAD' + ' ' + str(int(self.__balanceCavirtexCAD)) + 'FnlCAD' + '.csv'
        with open(storeFilename, 'wb') as csvfile:
            dataWriter = csv.DictWriter(csvfile, sorted(self.cycleInfo[0].keys()))
            dataWriter.writeheader()
            for cycle in self.cycleInfo:
                dataWriter.writerow(cycle)
        return storeFilename
