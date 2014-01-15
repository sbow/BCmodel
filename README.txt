BCmodel
2014/01/15
Shaun Bowman

OfflineBitcoin.py
- File to run "python OfflineBitcoin.py"
- Does setup (initial date, target profit for strategy, strategy class selection, initial CA bank balance

StrategyModel1.py
- Strategy class
- Looks for a target delta % in BTC price between Bitstamp & Cavirtex, then signals desire to buy

WorldModel.py
- Models all trade steps
- Builds records of trade steps & provides methods to print these records to the screen or a CSV

ParseCsv.py
- Builds python format (cPickle) datastructures from CSV's containing historical trade & currency data
- Not run by OfflineBitcoin.py, to update datasets download new CSV's, change the setup variables in this file and
  run "python ParseCsv.py"



Tested using:
Python 2.7
Mac OSX
