import datetime
import pandas as pd
import time

DEBUG = True
DATE_SHIFT = 341  # we have old base so need to add some days to existing values to check downtime features

DOWNTIME = 24  # downtime limit for red status
DOWNTIME_PU = 45  # downtime limit for red status only for PU stations

FAST_MODE = True

#  There not a real position, rather our assume
UKRAINE_BOARDERS = [[48.25, 22.14], [52.35, 33.15], [44.35, 33.65], [49.25, 40.25]]  # WNSE 52.35-44.35 40.25-22.14
STATION_POSITIONS = {38810: [49.22, 24.65], 49310: [48.45, 37.08], 40030: [46.49, 30.75], 50770: [48.77, 39.28],
                     44100: [49.98, 36.08], 45000: [48.48, 35.12], 35000: [50.53, 26.26], 45770: [47.96, 33.41],
                     32740: [51.22, 33.19], 47600: [46.87, 35.36], 37040: [49.86, 23.98], 33580: [49.24, 28.51],
                     45510: [48.44, 36.03], 49100: [48.41, 37.78], 41520: [46.96, 31.98], 44280: [48.89, 36.32],
                     40510: [46.48, 30.65], 34620: [50.96, 28.59], 46000: [47.88, 35.23], 37000: [49.84, 23.99],
                     36120: [49.6, 25.91], 40790: [47.89, 29.34], 48100: [47.99, 37.31], 46700: [47.91, 33.45],
                     45460: [48.63, 35.89], 49140: [48.63, 37.55], 46300: [47.48, 36.26], 58890: [48.05, 40.19],
                     41960: [47.19, 31.72], 48200: [48.29, 37.18], 42000: [49.2, 31.9], 43830: [50.2, 38.12],
                     40110: [46.83, 30.76], 49120: [48.51, 37.73], 48210: [48.23, 37.31], 43230: [50.33, 36.19],
                     46720: [47.88, 33.38], 45350: [48.33, 35.51], 49600: [48.63, 38.38], 45640: [48.48, 34.24],
                     43880: [50.94, 37.81], 46360: [47.81, 35.28], 34640: [50.98, 28.61], 32880: [52.18, 34.02],
                     20650: [51.21, 35.31], 43190: [49.71, 37.64], 45220: [48.81, 35.27], 33300: [48.77, 26.61],
                     43981: [50.01, 38.19], 45760: [47.92, 33.4], 41190: [48.24, 31.41], 52210: [45.23, 38.15],
                     37630: [49.36, 23.54], 32870: [52.04, 33.95], 48560: [47.21, 37.56], 45700: [48.35, 33.5],
                     42120: [48.73, 30.2], 34000: [50.2, 27.07], 43920: [50.49, 37.85], 48620: [47.6, 37.49],
                     44000: [50.03, 36.18], 46710: [47.96, 33.53], 45060: [48.5, 35.06], 42500: [49.07, 33.43],
                     33310: [48.83, 26.6], 38010: [48.43, 22.21], 47690: [47.49, 34.65], 42420: [49.43, 32.05],
                     49180: [48.73, 37.54], 32600: [51.19, 32.84], 34970: [51.29, 28.59], 49000: [48.97, 37.83],
                     34630: [50.96, 28.63]}

STATION_PIXELS = {38810: [609, 263], 49310: [513, 1567], 40030: [268, 903], 50770: [553, 1798], 44100: [704, 1463],
                  45000: [516, 1362], 35000: [772, 432], 45770: [451, 1182], 32740: [859, 1159], 47600: [315, 1387],
                  37040: [689, 193], 33580: [611, 668], 45510: [511, 1457], 49100: [507, 1641], 41520: [326, 1032],
                  44280: [567, 1488], 40510: [266, 893], 34620: [826, 677], 46000: [441, 1373], 37000: [686, 194],
                  36120: [656, 396], 40790: [442, 755], 48100: [455, 1592], 46700: [445, 1187], 45460: [535, 1443],
                  49140: [535, 1617], 46300: [391, 1481], 58890: [462, 1894], 41960: [355, 1005], 48200: [492, 1578],
                  42000: [606, 1024], 43830: [731, 1677], 40110: [310, 904], 49120: [520, 1636], 48210: [485, 1592],
                  43230: [747, 1474], 46720: [441, 1179], 45350: [497, 1403], 49600: [535, 1704], 45640: [516, 1269],
                  43880: [824, 1644], 46360: [433, 1379], 34640: [829, 679], 32880: [979, 1246], 20650: [857, 1382],
                  43190: [670, 1626], 45220: [558, 1378], 33300: [553, 469], 43981: [707, 1684], 45760: [446, 1181],
                  41190: [486, 973], 52210: [110, 1680], 37630: [626, 147], 32870: [961, 1239], 48560: [357, 1618],
                  45700: [500, 1192], 42120: [547, 846], 34000: [731, 517], 43920: [768, 1648], 48620: [406, 1610],
                  44000: [710, 1473], 46710: [451, 1195], 45060: [519, 1355], 42500: [590, 1184], 33310: [560, 468],
                  38010: [510, 7], 47690: [393, 1312], 42420: [635, 1040], 49180: [547, 1616], 32600: [855, 1123],
                  34970: [867, 677], 49000: [577, 1646], 34630: [826, 681]}

#  At now we assume that all operations above are appropriate for downtime calculations,
#  but we understand that is not True
DOWNTIME_COMPLIANT_OPERATION = ['ОДПВ', 'ОТОТ', 'ПГР2', 'ВЫГ2', 'ПРДР', 'СВПП', 'СДЧ', 'ДОСЛ', 'ПВПП', 'ВУ36', 'ОКОТ',
                                'ВУ23', 'ЗАНЯ', 'ОСВО', 'ПСНГ', 'ПГР0', 'ПРМ', 'СВТП', 'ВУ26', 'ПГР9', 'ПОГР', 'ВЫГ1',
                                'ВЫГР', 'ВКЛП', 'ОТСФ', 'ПСНП', 'ОСМТ', 'ИСКП', 'ПГР1', 'ПВТП', 'СПВС', 'СДГС', 'ПАДР']

COLUMNS = ['Номер вагона', 'Код станции операции', 'Название станции операции', 'Номер поезда', 'Индекс поезда',
           'Операция', 'Дата операции', 'Код груза', 'Название груза', 'Вес груза', 'Код станции назначения',
           'Название станции назначения', 'Код отправителя', 'Код получателя', 'Код станции отправления',
           'Станция начала рейса', 'Дата приема груза к перевозке']

#  I found it on the Internet, add some improvment for logging,
#  and decided that it could be very useful
class Profiler(object):
    # def __init__(self, iventType:str):
    #     self.iventType = iventType

    # def logevent(self, logmsg:str):
    #     assert isinstance(logmsg, object)
    #     self.logmsg = logmsg
    #     self.f.write(str(time.time()) + ' ' + str(self.iventType) + str(self.logmsg))

    def __enter__(self):
        self._startTime = time.time()
        # self.f = open('log.txt', 'a')
        # self.f.write(str(time.time()) + ' ' + str(self.iventType) + 'start')

    def __exit__(self, type, value, traceback):
        timemessage = "Elapsed time: {:.3f} sec".format(time.time() - self._startTime)
        print(timemessage)
        # self.f.write(str(time.time()) + ' ' + timemessage)
        # self.f.write(str(time.time()) + ' ' + str(self.iventType) + 'stop')
        # self.f.close()

########################################################################################################################
#                                              FUNC PROGRAMING RULE :)                                                 #
########################################################################################################################

def get_data_from_db(db_file='traindata.csv',
                     datetimeStart='',
                     carriageNumbers=None,
                     operationStations=None,
                     notEmpty=False,
                     isPickle=DEBUG):
    '''
    Read data from CSV and then filter it by different condition
    :param datetimeStart: string in datetime format from which start reading data eg '2017-06-18 17:05:00'
    :param carriageNumbers: list of carriages eg [52942752, 52965134], by default full list
    :param operationStations: list of operation stations carriages [49290, 49310]
    :param notEmpty: if True - only carriages with cargo will return
    :param isPickle: if True load data from picle file (for speed purpose)
    :return: dataframe sorted by operation date and carriage number
    '''
    with Profiler() as p:
        if isPickle:
            dataframe = pd.read_pickle('traindata.pkl')
        else:
            dataframe = pd.read_csv(db_file,
                                    converters={'Дата операции': pd.to_datetime,
                                                'Дата приема груза к перевозке': pd.to_datetime})

        dataframe.sort_values(by=['Дата операции', 'Номер вагона'], inplace=True)
        dataframe = dataframe.loc[dataframe['Дата операции'] >= datetimeStart].dropna(how='all')
        if carriageNumbers is not None:
            dataframe = dataframe.loc[dataframe['Номер вагона'].isin(carriageNumbers)].dropna(how='all')
        if operationStations is not None:
            dataframe = dataframe.loc[dataframe['Код станции операции'].isin(operationStations)].dropna(how='all')
        if notEmpty:
            dataframe = dataframe.loc[dataframe['Вес груза'] > 0].dropna(how='all')
        if DEBUG and False: print(dataframe.head(10))
        if DEBUG and False: p.logevent(logmsg = ('loaded from db:' + str(dataframe.shape)))
    return dataframe
get_data_from_db()

def only_last_operations(dataframe=None):
    '''
    Remove from given dataframe all non-first entry for each carriage
    I really think that there is a more effective way, but so far remains as it is
    :param dataframe: sorted by carriage_number and time dataframe
    :return: dateframe consisting of the most recent operations
    '''
    with Profiler() as p:
        if FAST_MODE:  #  using pickle file with dataframe, there much faster for most requests
            dataframe = pd.read_pickle('only_last_operations.pkl')
            return dataframe
        uniqueCarriages = []
        deletedRows = 0
        for index, row in dataframe.iterrows():
            if row['Номер вагона'] in uniqueCarriages:
                deletedRows += 1
                dataframe.drop(index, inplace=True)
            else:
                uniqueCarriages.append(row['Номер вагона'])
        if DEBUG and False: print('rows deleted: ' + str(deletedRows))
        if DEBUG and False: print(dataframe.head(10))
        if DEBUG and False: print(dataframe.shape)
        if DEBUG and False: dataframe.to_pickle('only_last_operations.pkl')
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
    if DEBUG and True: print('in operation ' + operation + ' : ' + str(dataframe.shape))
    return dataframe


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
    dataframe = only_last_operations(dataframe)  # we don't need to check operations that already ended
    dataframe = dataframe.loc[dataframe['Дата операции'] <= downtimeDelta].dropna(how='all')
    if carriageNumbers is not None:
        dataframe = dataframe.loc[dataframe['Номер вагона'].isin(carriageNumbers)].dropna(how='all')
    if operationStations is not None:
        dataframe = dataframe.loc[dataframe['Код станции операции'].isin([operationStations])].dropna(how='all')
    if notEmpty:
        dataframe = dataframe.loc[dataframe['Вес груза'] > 0].dropna(how='all')

    if DEBUG and False: print(dataframe.head(10))
    if DEBUG and False: print('in downtime:' + str(dataframe.shape))
    return dataframe


# data_from_db = get_data_from_db()
# last_operations = only_last_operations(data_from_db)
# carriage_in_operation(carriage_in_downtime(data_from_db), 'ОКОТ')
# carriage_in_operation(last_operations, 'ВУ23')
# carriage_in_operation(last_operations, 'ВУ26')
# carriage_in_operation(last_operations, 'ВУ36')
# carriage_in_operation(last_operations, 'БРОС')

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
        if row['Операция'] in DOWNTIME_COMPLIANT_OPERATION:  # calculate downtime only for some operation
            carriagesDowntime[row['Номер вагона']] = nowtime - row['Дата операции'] \
                                                     - datetime.timedelta(days=DATE_SHIFT)  # shift due to test data
        #  TODO add rounddown operation
        else:
            carriagesDowntime[row['Номер вагона']] = pd.to_timedelta(0)
    if DEBUG and False:
        for key in list(carriagesDowntime.keys())[0:10]:
            print(carriagesDowntime[key])
    return carriagesDowntime


def get_stations(dataframe):
    '''
    Create dict with stations as a keys, and list of trains as a value
    :param dataframe: dataframe from csv file
    :return: trains-to-stations mapping dict {station:[trains]}
    '''
    stations = {}
    for index, row in dataframe.iterrows():
        if row['Код станции операции'] not in stations.keys():
            stations[row['Код станции операции']] = [row['Номер поезда']]
        else:
            stations[row['Код станции операции']].append(row['Номер поезда'])
    if DEBUG and False: print('stations collected ' + str(len(stations)))
    if DEBUG and False: print('stations ' + str(stations))
    return stations


def get_trains(dataframe):
    '''
    Create dict with train as a keys, and list of carriage as a value
    :param dataframe: dataframe from csv file
    :return: carriages-to-trains mapping dict {train:[carriege]}
    '''
    dataframe = only_last_operations(dataframe)  # To ensure uniqueness of carriages
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
    :return: trainsData in dict {train:{'position':[x, y],
                                        'info':[carriageCount, avgDowntime, color],
                                        'carriages':{carriage:[isEmpty, downtime, stationFrom, stationTo]}}}
    '''
    dataframe = only_last_operations(dataframe)  # To ensure uniqueness of carriages
    carriagesDowntime = get_downtime_for_carriages(dataframe)
    trainsData = {}
    for train in trains:
        trainDataframe = dataframe.loc[dataframe['Индекс поезда'] == train].dropna(how='all')
        #  get position from station position dictionary
        if trainDataframe['Код станции операции'].iloc[0] not in STATION_PIXELS.keys():
            trainPosition = [900, 1800]  # Hardcoded until we find the positions of missing stations
        else:
            trainPosition = STATION_PIXELS[trainDataframe['Код станции операции'].iloc[0]]
        carriages = {}
        trainDowntime = pd.to_timedelta(0)
        for carriage in trains[train]:
            isEmpty = trainDataframe.loc[trainDataframe['Номер вагона'] == carriage]['Вес груза'] == 0
            stationFrom = trainDataframe.loc[trainDataframe['Номер вагона'] == carriage]['Код станции отправления']
            stationTo = trainDataframe.loc[trainDataframe['Номер вагона'] == carriage]['Код станции назначения']
            carriages[carriage] = [isEmpty, carriagesDowntime[carriage], stationFrom, stationTo]
            trainDowntime += carriagesDowntime[carriage]
            trainDowntime = trainDowntime // len(carriages)
        if trainDowntime >= pd.to_timedelta(DOWNTIME, unit='h'):
            color = 'red'
        else:
            color = 'green'
        #  gather collected data in one dict
        trainData = {'position': trainPosition,
                     'info': [len(trains[train]), trainDowntime, color],
                     'carriages': carriages}
        trainsData[train] = trainData
    if DEBUG and False: print('trainsData collected ' + str(len(trainsData)))
    if DEBUG and False: print('trains ' + str(trains))
    return trainsData


# print(get_train_FEdata(get_trains(data_from_db), data_from_db))


def get_station_FEdata(stations, dataframe):
    '''
    :param stations: list of stations
    :param dataframe:
    :return: stationData: dict {station:{'position': [x, y],
                                         'carriagesWithDowntime': int,
                                         'trains': {train: {'position': [x, y],
                                                            'info': [carriageCount, avgDowntime, color],
                                                            'carriages': {carriage: [isEmpty, downtime,
                                                                                     stationFrom, stationTo]}}}}}
    '''
    dataframe = only_last_operations(dataframe)  # To ensure uniqueness of carriages
    stationsData = {}
    counter = 0
    for station in stations:
        with Profiler() as p:
            stationsData[station] = {}
            if dataframe['Код станции операции'].iloc[0] not in STATION_PIXELS.keys():
                stationPosition = [900, 1800]
                counter+=1
            else:
                stationPosition = STATION_PIXELS[station]
            carriagesWithDowntime = carriage_in_downtime(dataframe, operationStations=station).size
            print('On {0} station is {1} carriage in downtime'.format(str(station), str(carriagesWithDowntime)))
            trainsData = get_train_FEdata(get_trains(dataframe), dataframe)
            stationsData[station] = {'position': stationPosition,
                                 'carriagesWithDowntime': carriagesWithDowntime,
                                 'trains': trainsData}
    if DEBUG and False: print('Stations without coord {}'.format(counter))
    if DEBUG and True: csv_to_picle(stationsData, 'stationsData')
    return stationsData


# print(get_station_FEdata(STATION_PIXELS.keys(), data_from_db))


########################################################################################################################
#                                         Various auxiliary functions                                                  #
########################################################################################################################
def csv_to_picle(data, filename):
    data.to_pickle(filename + '.pkl')
    if DEBUG and True: print('Data converted to: ' + filename + '.pkl')


def enrich_station_data():
    osm2esr = pd.read_csv('osm2esr.csv', sep=';')
    stations = gather_stations_dict(data_from_db)
    stationLoc = {}
    for key in stations.keys():
        position = osm2esr.loc[osm2esr['esr'].isin(range(key * 10, key * 10 + 9))][['lat', 'lon']]
        if position.empty: continue
        if not min(pd.DataFrame(UKRAINE_BOARDERS)[0]) <= position['lat'].iloc[0] <= max(
                pd.DataFrame(UKRAINE_BOARDERS)[0]):
            continue
        if not min(pd.DataFrame(UKRAINE_BOARDERS)[1]) <= position['lon'].iloc[0] <= max(
                pd.DataFrame(UKRAINE_BOARDERS)[1]):
            continue
        stationLoc[key] = list(position.iloc[0].round(2))
    return stationLoc


def translate_position_to_pixel(stationLoc):
    pixelCoordinates = {}
    ukraineSize = [52.35 - 44.35, 40.25 - 22.14]
    mapSize = [1000, 1900]
    for key in stationLoc.keys():
        pixelCoordinates[key] = [round((stationLoc[key][0] - 44.35) / ukraineSize[0] * mapSize[0]),
                                 round((stationLoc[key][1] - 22.14) / ukraineSize[1] * mapSize[1])]
    return pixelCoordinates


def save_object_to_file(objectDict):
    print(pd.DataFrame.from_dict(objectDict).iloc[0])
