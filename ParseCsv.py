# 2013 / 01 / 02
# ParseCsv.py
# Parses the csv from this site: http://www.bitcoincharts.com/about/markets-api/
# Contains bitcoin transaction data from various exchanges
# Creates list of dictionaries with historical data from Cavirtex & Bitstamp
# (not implimented) Creates list of historical exchange rates (bid) from www.dukascopy.com/swiss/english/marketwatch/historical (amazing...)
# Saves datafile using cPickle (fileDataPickle)

__author__ = 'shaun bowman'

fileCavirtexCAD = 'virtexCAD.csv'
fileBitstampUSD = 'bitstampUSD.csv'

fileBitstampPkl = 'bitcoinDataBitstamp.pkl'
fileCavirtexPkl = 'bitcoinDataCavirtex.pkl'

fileDukascopyUSDCAD2013 = 'USDCAD_Candlestick_1_m_BID_01.01.2013-02.01.2014.csv'
fileDukascopyUSDCAD2012 = 'USDCAD_Candlestick_1_m_BID_01.01.2012-31.12.2012.csv'
fileDukascopyUSDCAD2011 = 'USDCAD_Candlestick_1_m_BID_01.01.2011-31.12.2011.csv'

fileDukascopy2011Pkl = 'dukascopyUSDCAD2011.pkl'
fileDukascopy2012Pkl = 'dukascopyUSDCAD2012.pkl'
fileDukascopy2013Pkl = 'dukascopyUSDCAD2013.pkl'
fileDukascopy20112014Pkl = 'dukascopyUSDCAD20112014.pkl'


import csv, datetime, copy, cPickle

timestart = datetime.datetime.now();



csvDukascopyFormat = {'rawDatetime' : 'undef','high' : 'undef'}
dataDukascopyUSDCAD = [csvDukascopyFormat]

with open(fileDukascopyUSDCAD2011, 'rb') as f:
    reader = csv.reader(f)
    next(reader, None) # skip the header
    for row in reader:
        x = 0
        for col in ['rawDatetime','high']:
            dataDukascopyUSDCAD[-1][col] = row[x]
            x = x + 1
        dataDukascopyUSDCAD[-1]['datetime'] = datetime.datetime.strptime(dataDukascopyUSDCAD[-1]['rawDatetime'], "%d.%m.%Y %H:%M:%S.000") # convert from dukascopy datetime format to datetime object
        dataDukascopyUSDCAD.append(copy.deepcopy(csvDukascopyFormat))
dataDukascopyUSDCAD.pop()

with open(fileDukascopyUSDCAD2012, 'rb') as f:
    reader = csv.reader(f)
    next(reader, None) # skip the header
    for row in reader:
        x = 0
        for col in ['rawDatetime','high']:
            dataDukascopyUSDCAD[-1][col] = row[x]
            x = x + 1
        dataDukascopyUSDCAD[-1]['datetime'] = datetime.datetime.strptime(dataDukascopyUSDCAD[-1]['rawDatetime'], "%d.%m.%Y %H:%M:%S.000") # convert from dukascopy datetime format to datetime object
        dataDukascopyUSDCAD.append(copy.deepcopy(csvDukascopyFormat))
dataDukascopyUSDCAD.pop()

with open(fileDukascopyUSDCAD2013, 'rb') as f:
    reader = csv.reader(f)
    next(reader, None) # skip the header
    for row in reader:
        x = 0
        for col in ['rawDatetime','high']:
            dataDukascopyUSDCAD[-1][col] = row[x]
            x = x + 1
        dataDukascopyUSDCAD[-1]['datetime'] = datetime.datetime.strptime(dataDukascopyUSDCAD[-1]['rawDatetime'], "%d.%m.%Y %H:%M:%S.000") # convert from dukascopy datetime format to datetime object
        dataDukascopyUSDCAD.append(copy.deepcopy(csvDukascopyFormat))
dataDukascopyUSDCAD.pop()

with open(fileDukascopy20112014Pkl, 'w') as f:
    cPickle.dump(dataDukascopyUSDCAD, f, 2)

print dataDukascopyUSDCAD[0]
print dataDukascopyUSDCAD[100]
print dataDukascopyUSDCAD[-1]



tid = 0 # unique transaction id

csvRowFormat = {'date' : 'undef', 'amount' : 'undef', 'price' : 'undef'}

dataCavirtexCAD = [csvRowFormat]

# FORMAT MUST BE: unixtimestamp,price,ncoins (this is the format from bitcoincharts csv's)
with open(fileCavirtexCAD, 'rb',) as f:
    reader = csv.reader(f)
    for row in reader:
        x = 0
        for col in ['date','price','ncoins']:
            # csvRowFormat[col] = row[x]
            dataCavirtexCAD[-1][col] = row[x]
            x = x + 1
        # dataCavirtexCAD[-1].update(csvRowFormat)

        dataCavirtexCAD[-1]['dollars'] = round(float(dataCavirtexCAD[-1]['price']) * float(dataCavirtexCAD[-1]['ncoins']), 4)
        dataCavirtexCAD[-1]['currency'] = 'CAD'
        dataCavirtexCAD[-1]['datetimeHuman'] = datetime.datetime.fromtimestamp(int(dataCavirtexCAD[-1]['date'])).strftime('%Y-%m-%d %H:%M:%S')
        dataCavirtexCAD[-1]['exchange'] = 'cavirtex'
        dataCavirtexCAD[-1]['datetime'] = datetime.datetime.fromtimestamp(int(dataCavirtexCAD[-1]['date']))
        dataCavirtexCAD[-1]['tid'] = tid

        dataCavirtexCAD.append(copy.deepcopy(csvRowFormat)) # note: need to do deepcopy of format otherwise its just a pointer replicated a million times
        tid = tid + 1
dataCavirtexCAD.pop() # gets rid of false record left over from last append

print dataCavirtexCAD[10]
print dataCavirtexCAD[100]



csvRowFormat = {'date' : 'undef', 'amount' : 'undef', 'price' : 'undef'}
dataBitstampUSD = [csvRowFormat]

with open(fileBitstampUSD, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        x = 0
        for col in ['date','price','ncoins']:
            dataBitstampUSD[-1][col] = row[x]
            # csvRowFormat[col] = row[x]
            x = x + 1
        # dataBitstampUSD[-1].update(csvRowFormat)

        dataBitstampUSD[-1]['dollars'] = round(float(dataBitstampUSD[-1]['price']) * float(dataBitstampUSD[-1]['ncoins']), 4)
        dataBitstampUSD[-1]['currency'] = 'USD'
        dataBitstampUSD[-1]['datetimeHuman'] = datetime.datetime.fromtimestamp(int(dataBitstampUSD[-1]['date'])).strftime('%Y-%m-%d %H:%M:%S')
        dataBitstampUSD[-1]['exchange'] = 'bitstamp'
        dataBitstampUSD[-1]['datetime'] = datetime.datetime.fromtimestamp(int(dataBitstampUSD[-1]['date']))
        dataBitstampUSD[-1]['tid'] = tid

        dataBitstampUSD.append(copy.deepcopy(csvRowFormat))
        tid = tid + 1
dataBitstampUSD.pop()

print dataBitstampUSD[100]
print dataBitstampUSD[-1]

# SAVE OFF DATA FILES
with open(fileCavirtexPkl, 'w') as pklFile:
    cPickle.dump(dataCavirtexCAD, pklFile, 2)

with open(fileBitstampPkl, 'w') as pklFile:
    cPickle.dump(dataBitstampUSD, pklFile, 2)

timeend = datetime.datetime.now()
print str(timeend - timestart) # time taken to run program