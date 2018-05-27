import datetime
import pandas as pd

DEBUG = True
DATE_SHIFT = 341 #  we have old base so need to add some days to existing values to check downtime features

DOWNTIME = 24 #  downtime limit for red status
DOWNTIME_PU = 45 #  downtime limit for red status only for PU stations

#  There not a real position, rather our assume
STATION_POSITIONS = {45510:(100, 200)} #TODO dict of station positions

#  At now we assume that all operations above are appropriate for downtime calculations,
#  but we understand that is not True
DOWNTIME_COMPLIANT_OPERATION = ['ОДПВ', 'ОТОТ', 'ПГР2', 'ВЫГ2', 'ПРДР', 'СВПП', 'СДЧ', 'ДОСЛ', 'ПВПП', 'ВУ36', 'ОКОТ',
                                'ВУ23', 'ЗАНЯ', 'ОСВО', 'ПСНГ', 'ПГР0', 'ПРМ', 'СВТП', 'ВУ26', 'ПГР9', 'ПОГР', 'ВЫГ1',
                                'ВЫГР', 'ВКЛП', 'ОТСФ', 'ПСНП', 'ОСМТ', 'ИСКП', 'ПГР1', 'ПВТП', 'СПВС', 'СДГС', 'ПАДР']

COLUMNS = ['Номер вагона', 'Код станции операции', 'Название станции операции', 'Номер поезда', 'Индекс поезда',
           'Операция', 'Дата операции', 'Код груза', 'Название груза', 'Вес груза', 'Код станции назначения',
           'Название станции назначения', 'Код отправителя', 'Код получателя', 'Код станции отправления',
           'Станция начала рейса', 'Дата приема груза к перевозке']

class Carriage():
    carriageList = []
    def __init__(self, entry):
        self.number = int(entry.iloc[0])
        self.operationStation = int(entry.iloc[1])
        self.train = entry.iloc[3]
        self.trainIndex = entry.iloc[4]
        self.operation = entry.iloc[5]
        self.lastOperationDate = entry.iloc[6]
        self.cargoCode = int(entry.iloc[7])
        self.cargoWeight = int(entry.iloc[9])
        self.destinationStation = entry.iloc[10]
        self.senderCode = entry.iloc[12]
        self.recipientCode = entry.iloc[13]
        self.sendStation = entry.iloc[14]
        self.cargoSendDate = entry.iloc[16]
        self.isVisible = False
        self.coordinates = [0, 0]
        self.color = 'black'

    def to_dict(self):
        return {
            'number': self.number,
            'operationStation': self.operationStation,
        }

    def change_color(self):
        if is_downtime(self): self.color = 'red'

    def is_downtime(self):
        if DEBUG and True: print('is_downtime start')
        if (time.now-self.lastOperationDate>DOWNTIME) and self.operation == 'ПРИБ':
            print("Простой")


class Station():
    stationList = []
    def __init__(self, entry):
        self.number = int(entry.iloc[1])
        self.name = entry.iloc[2]
        self.isVisible = True
        self.coordinates = [0, 0]


def create_carriage_objects(dataframe):
    for index, entry in dataframe.iterrows():
        if entry.iloc[0] not in Carriage.carriageList:
            Carriage.carriageList.append(entry.iloc[0])
            carriageDict.update({entry.iloc[0]: Carriage(entry)})

    if DEBUG and True: print('unic carriages = '+str(len(Carriage.carriageList)))


def create_station_objects(dataframe):
    for index, entry in dataframe.iterrows():
        if entry.iloc[1] not in Station.stationList:
            Station.stationList.append(entry.iloc[1])
            stationDict.update({entry.iloc[1]: Station(entry)})
    if DEBUG and True: print('unic stations = '+str(len(Station.stationList)))


def save_object_to_file(objectDict):
    print(pd.DataFrame.from_dict(objectDict).iloc[0])
    # pd.DataFrame.from_dict(objectDict).iloc[0].to_csv('carriageREST.csv', header=False, index=False, mode='a')




########################################################################################################################
#                                              FUNC PROGRAMING RULE :)                                                 #
########################################################################################################################

def get_data_from_db(datetimeStart='', carriageNumbers=None, operationStations=None, notEmpty=False, isPickle=False):
    '''
    Read data from CSV and then filter it by different condition
    :param datetimeStart: string in datetime format from which start reading data eg '2017-06-18 17:05:00'
    :param carriageNumbers: list of carriages eg [52942752, 52965134], by default full list
    :param operationStations: list of operation stations carriages [49290, 49310]
    :param notEmpty: if True - only carriages with cargo will return
    :param isPickle: if True load data from picle file (for speed purpose)
    :return: dataframe sorted by operation date and carriage number
    '''
    if isPickle:
        dataframe = pd.read_pickle('traindata.pkl')
    else:
        dataframe = pd.read_csv('traindata.csv',
                                converters={'Дата операции': pd.to_datetime,
                                            'Дата приема груза к перевозке': pd.to_datetime})

    dataframe.sort_values(by=['Дата операции','Номер вагона'], inplace=True)
    dataframe = dataframe.loc[dataframe['Дата операции'] >= datetimeStart].dropna(how='all')
    if carriageNumbers is not None:
        dataframe = dataframe.loc[dataframe['Номер вагона'].isin(carriageNumbers)].dropna(how='all')
    if operationStations is not None:
        dataframe = dataframe.loc[dataframe['Код станции операции'].isin(operationStations)].dropna(how='all')
    if notEmpty:
        dataframe = dataframe.loc[dataframe['Вес груза'] > 0].dropna(how='all')
    if DEBUG and False: print(dataframe.head(10))
    if DEBUG and True: print('loaded from db:'+str(dataframe.shape))
    return dataframe

def only_last_operations(dataframe):
    '''
    Remove from given dataframe all non-first entry for each carriage
    :param dataframe: sorted by carriage_number and time dataframe
    :return: dateframe consisting of the most recent operations
    '''
    uniqueCarriages = []
    deletedRows = 0
    for index, row in dataframe.iterrows():
        if row['Номер вагона'] in uniqueCarriages:
            deletedRows += 1
            dataframe.drop(index, inplace=True)
        else:
            uniqueCarriages.append(row['Номер вагона'])
    if DEBUG and False: print('rows deleted: '+str(deletedRows))
    if DEBUG and False: print(dataframe.head(10))
    if DEBUG and False: print(dataframe.shape)
    return dataframe

def carriage_in_operation(dataframe, operation):
    '''
    Find items from a given dataset that are corresponds to given operation
    :param dataframe: dataframe from csv file
    :param operation: operation type from NSI.OPVAGON
    :return: All carriages data that are in the specific operation status
    '''
    dataframe = dataframe.loc[dataframe['Операция'] == operation].dropna(how='all')
    if DEBUG and False: print(dataframe.head())
    if DEBUG and True: print('in operation '+operation+' : '+str(dataframe.shape))
    return dataframe

def carriage_in_downtime(dataframe,
                         carriageNumbers=None,
                         operationStations=None,
                         notEmpty=False,
                         downtimeLimit=DOWNTIME):
    '''
    Find carriages that exceeded permissible downtime
    :param dataframe: dataframe from csv file
    :param carriageNumbers: list of carriages eg [52942752, 52965134], if None - full list will be used
    :param operationStations: list of operation stations carriages [49290, 49310], if None - full list will be used
    :param notEmpty: if True - only carriages with cargo will return
    :param downtimeLimit: permissible downtime in hours, by default use global constant DOWNTIME(=24h)
    :return: dataframe with carriages that exceeded permissible downtime
    '''
    nowtime = datetime.datetime.now()
    downtimeDelta = nowtime - datetime.timedelta(days=DATE_SHIFT, hours=downtimeLimit)
    dataframe = only_last_operations(dataframe)  #  we don't need to check operations that already ended
    dataframe = dataframe.loc[dataframe['Дата операции'] <= downtimeDelta].dropna(how='all')
    if carriageNumbers is not None:
        dataframe = dataframe.loc[dataframe['Номер вагона'].isin(carriageNumbers)].dropna(how='all')
    if operationStations is not None:
        dataframe = dataframe.loc[dataframe['Код станции операции'].isin(operationStations)].dropna(how='all')
    if notEmpty:
        dataframe = dataframe.loc[dataframe['Вес груза'] > 0].dropna(how='all')

    if DEBUG and False: print(dataframe.head(10))
    if DEBUG and True: print('in downtime:'+str(dataframe.shape))
    return dataframe

data_from_db = get_data_from_db(isPickle = DEBUG)
# last_operations = only_last_operations(data_from_db)
# carriage_in_operation(carriage_in_downtime(data_from_db), 'ОКОТ')
# carriage_in_operation(last_operations, 'ВУ23')
# carriage_in_operation(last_operations, 'ВУ26')
# carriage_in_operation(last_operations, 'ВУ36')
# carriage_in_operation(last_operations, 'БРОС')

def get_trains(dataframe):
    '''
    Create dict with train as a keys, and list of carriage as a value
    :param dataframe: dataframe from csv file
    :return: carriage-to-trains mapping dict
    '''
    dataframe = only_last_operations(dataframe)  #  To ensure uniqueness of carriages
    trains = {}
    for index, row in dataframe.iterrows():
        if row['Индекс поезда'] not in trains.keys():
            trains[row['Индекс поезда']] = [row['Номер вагона']]
        else:
            trains[row['Индекс поезда']].append(row['Номер вагона'])
    if DEBUG and False: print('trains collected ' + str(len(trains)))
    if DEBUG and False: print('trains ' + str(trains))
    return trains

def get_train_FEdata(trains, dataframe):
    '''
    Prepare data about trains for FrontEnd
    :param trains: dict of trains where train numbers are keys, and list of carriages is values {train:[carriages]}
    :param dataframe: dataframe from csv file
    :return: trainsData in dict {train:{'position':(x,y), 'carriages':{carriage:downtime}, 'downtime':int, 'color':#HEX}}
    '''
    dataframe = only_last_operations(dataframe)  # To ensure uniqueness of carriages
    trainsData = {}
    carriagesDowntime = get_downtime_for_carriages(dataframe)
    for train in trains:
        trainDataframe = dataframe.loc[dataframe['Индекс поезда'] == train].dropna(how='all')
        #  get position from station position dictionary
        trainPosition = STATION_POSITIONS[trainDataframe[0]['Код станции операции']]
        isEmptyTrain = True if trainDataframe[0]['Вес груза'] == 0 else False
        carriages = {}
        trainDowntime = 0
        for carriage in trains[train]:
            carriages[carriage] = carriagesDowntime[carriage]
            trainDowntime += carriagesDowntime[carriage]
            trainDowntime = round(trainDowntime/len(carriages))
        if trainDowntime >= DOWNTIME:
            color = 'ff0000'
        elif isEmptyTrain:
            color = '000000'
        else:
            color = '00ff00'
        #  gather collected data in one dict
        trainData = {'position': trainPosition, 'carriages': carriages, 'downtime': trainDowntime, 'color': color}
        trainsData[train] = trainData
    if DEBUG and True: print('trainsData collected ' + str(len(trainsData)))
    if DEBUG and True: print('trains ' + str(trains))
    return trainsData

def get_downtime_for_carriages(dataframe):
    '''
    Calculate downtime for carriages, сonsidering operations that not cause
    downtime (eg 'ОТОТ'). Such operations stored in DOWNTIME_COMPLIANT_OPERATION
    :param dataframe: dataframe from csv file
    :return: all carriages with downtime value rounddown to hour (if in appropriate operation, else = 0)
             eg {52733490:5, 52943271:15, 55094742:30, 53392544:0}
    '''
    dataframe = only_last_operations(dataframe)  # To ensure uniqueness of carriages
    nowtime = datetime.datetime.now()
    carriagesDowntime = {}
    for index, row in dataframe.iterrows():
        if row['Операция'] in DOWNTIME_COMPLIANT_OPERATION: #  calculate downtime only for some operation
            # print
            carriagesDowntime[row['Номер вагона']] = nowtime - row['Дата операции']\
                                                     +datetime.timedelta(days=DATE_SHIFT) #  shift due to test data
        else:
            carriagesDowntime[row['Номер вагона']] = 0
    for key, value in carriagesDowntime.items():
        if value > 0 : print('Downtime>0 carriege'+str(key))
    if DEBUG and False:
        for key in list(carriagesDowntime.keys())[0:10]:
            print(carriagesDowntime[key])
    return carriagesDowntime

# get_train_FEdata(get_trains(data_from_db), data_from_db)
# get_downtime_for_carriages(last_operations)


########################################################################################################################
#                                         Various auxiliary functions                                                  #
########################################################################################################################
def csv_to_picle(filename):
    dataframe = get_data_from_db()
    dataframe.to_pickle(filename+'.pkl')
    if DEBUG and True: print('Data converted to: '+filename+'.pkl')
# csv_to_picle('traindata')

def gather_stations_dict(dataframe):
    stations = {}
    for index, row in dataframe.iterrows():
        if row['Код станции операции'] not in stations.keys():
            stations[row['Код станции операции']] = row['Название станции операции']
    return stations

def gather_operations_list(dataframe):
    operations = []
    for index, row in dataframe.iterrows():
        if row['Операция'] not in operations:
            operations.append(row['Операция'])
    return operations

def create_stations_coord(stations):
    pass #TODO for global constant

def get_station_data_from_csv():
    osm2esr = pd.read_csv('osm2esr.csv', sep=';')
    # pureESR = pd.read_csv('esr.csv', sep=';')
    stations = gather_stations_dict(data_from_db)
    stationLoc = {}
    for key in stations.keys():
        lat = osm2esr.loc[osm2esr['esr'].isin(range(key * 10, key * 10 + 9))][['lat']]
        latf = lat.astype(dtype=int, copy=False)
        print(latf)
        print(type(latf))
        lon = osm2esr.loc[osm2esr['esr'].isin(range(key * 10, key * 10 + 9))][['lon']]
    #     # if lat : print('bla')
    #     # print(locations['lat'])
    #     print('for key: '+str(key)+' lat is '+str(lat)+' lon is '+str(lon)+'\n')
    #     stationLoc[key] = osm2esr.loc[osm2esr['esr'].isin(range(key*10,key*10+9))][['lat','lon']]
    # print(stationLoc)


    # osm2esr = osm2esr.loc[osm2esr['esr'].isin(stations.keys())].dropna(how='all')
    # print(stationLoc)
    # a = osm2esr.loc[osm2esr['esr'].isin(range(388100,388109))][['lat','lon']]


get_station_data_from_csv()


def set_carriage_color(carriage=Carriage):
    get_carriage_state(carriage)

def get_carriage_state(carriage:int):
    return state









