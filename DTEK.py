import datetime
import pandas as pd

DEBUG = True
DATE_SHIFT = 341 #we have old base so need to add some days to existing values to check downtime features

DOWNTIME = 24 #downtime limit for red status
DOWNTIME_PU = 45 #downtime limit for red status only for PU stations

carriageDict={}
stationDict={}


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


def get_data_from_db(datetimeStart='', carriageNumbers=None, operationStations=None, notEmpty=False):
    '''
    Read data from CSV and then filter it by different condition
    :param datetimeStart: string in datetime format from which start reading data eg '2017-06-18 17:05:00'
    :param carriageNumbers: list of carriages eg [52942752, 52965134], by default full list
    :param operationStations: list of operation stations carriages [49290, 49310]
    :param notEmpty: if True - only carriages with cargo will return
    :return: dataframe sorted by operation date and carriage number
    '''
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
    if DEBUG and False: print(dataframe.shape)
    return dataframe

def only_last_operations(dataframe):
    '''
    Remove from dataframe all non-first entry for each carriage
    :param dataframe: sorted by carriage_number and time dataframe
    :return: only last operations dataframe
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
    dataframe = dataframe.loc[dataframe['Операция'] == operation].dropna(how='all')
    if DEBUG and True: print(dataframe.head())
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
    :param carriageNumbers: list of carriages eg [52942752, 52965134], by default full list
    :param operationStations: list of operation stations carriages [49290, 49310], by default full list
    :param notEmpty: if True - only carriages with cargo will return
    :param downtimeLimit: permissible downtime in hours, by default use constant(24h)
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

# data_from_db = get_data_from_db()
# last_operations = only_last_operations(data_from_db)
# carriage_in_operation(carriage_in_downtime(data_from_db), 'ОКОТ')
# carriage_in_operation(last_operations, 'ВУ23')
# carriage_in_operation(last_operations, 'ВУ26')
# carriage_in_operation(last_operations, 'ВУ36')
# carriage_in_operation(last_operations, 'БРОС')

def get_train(dataframe):
    




def save_object_to_file(objectDict):
    print(pd.DataFrame.from_dict(objectDict).iloc[0])
    # pd.DataFrame.from_dict(objectDict).iloc[0].to_csv('carriageREST.csv', header=False, index=False, mode='a')


def csv_to_picle(filename):
    dataframe = pd.read_csv(filename+'.csv')
    dataframe.to_pickle(filename+'.pkl')
    if DEBUG and True: print('file converted to: '+filename+'.pkl')
# csv_to_picle()


def draw_map():
    draw_ukraine_map()
    draw_stations_list(stations_list)
    draw_carriages_list(carriages_list)
    pass #TODO

def draw_stations_list(stations_list=None):
    for station in stations_list:
        draw_station(station)

def draw_station(station:int):
    stationDict[station].coord

def draw_carriages_list(carriages_list=None):
    for carriages in carriages_list:
        draw_carriage(carriage)

def draw_carriage(carriage:int):
    carriage_coord = stationDict[carriageDict[carriage].operationStation].coord

def set_carriage_color(carriage=Carriage):
    get_carriage_state(carriage)

def get_carriage_state(carriage:int):
    return state









