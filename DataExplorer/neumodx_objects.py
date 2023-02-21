import pandas as pd
import numpy as np


class nmdx_file_parser:
    """
    A class used to read raw data file(s) and convert to flat format.
    Methods
    -------
    scrapeFile(file=None, env=None)
        Scrapes data from one raw data file.
    """

    def __init__(self):
        self.file_data = {}

    def readChannelData(file, sheet, channel):

        channelData_all = pd.read_excel(io=file, sheet_name=sheet)
        if len(channelData_all) > 0:
            ChannelRawStart = channelData_all[channelData_all['Sample ID']
                                              == 'Raw'].index.values[0] + 1
            ChannelRawEnd = channelData_all[channelData_all['Sample ID']
                                            == 'Normalized'].index.values[0] - 2
            ChannelRaw = channelData_all.loc[ChannelRawStart:ChannelRawEnd]
            ChannelRaw['Processing Step'] = 'Raw'

            ChannelNormStart = channelData_all[channelData_all['Sample ID']
                                               == 'Normalized'].index.values[0] + 1
            ChannelNormEnd = channelData_all[channelData_all['Sample ID']
                                             == 'SecondDerivative'].index.values[0] - 2
            ChannelNorm = channelData_all.loc[ChannelNormStart:ChannelNormEnd]
            ChannelNorm['Processing Step'] = 'Normalized'

            Channel2ndStart = channelData_all[channelData_all['Sample ID']
                                              == 'SecondDerivative'].index.values[0] + 1

            if 'Modulated' in channelData_all['Sample ID'].unique():
                Channel2ndEnd = channelData_all[channelData_all['Sample ID']
                                                == 'Modulated'].index.values[0] - 2
                ChannelModulatedStart = channelData_all[channelData_all['Sample ID']
                                                        == 'Modulated'].index.values[0] + 1
                ChannelModulated = channelData_all.loc[ChannelModulatedStart:ChannelModulatedStart+len(
                    ChannelRaw)]
                ChannelModulated['Processing Step'] = 'Modulated'
                Channel2nd = channelData_all.loc[Channel2ndStart:Channel2ndEnd]
                Channel2nd['Processing Step'] = '2nd'

                if len(ChannelRaw) == len(ChannelNorm) and len(ChannelRaw) == len(Channel2nd) and len(ChannelRaw) == len(ChannelModulated):

                    ChannelFinal = pd.concat(
                        [ChannelRaw, ChannelNorm, Channel2nd, ChannelModulated], axis=0)
                    ChannelFinal['Channel'] = channel
                    ChannelFinal.set_index(
                        ['Test Guid', 'Replicate Number'], inplace=True)
                else:
                    print("Error in parsing Datablocks")
            else:
                Channel2nd = channelData_all.loc[Channel2ndStart:Channel2ndStart+len(
                    ChannelRaw)]
                Channel2nd['Processing Step'] = '2nd'
                ChannelFinal = pd.concat(
                    [ChannelRaw, ChannelNorm, Channel2nd], axis=0)
                ChannelFinal['Channel'] = channel
                ChannelFinal.set_index(
                    ['Test Guid', 'Replicate Number'], inplace=True)

        else:
            ChannelFinal = pd.DataFrame()

        return ChannelFinal

    def readRawData(file):
        channelDict = {'Green_470_510': 'Green',
                       'Yellow_530_555': 'Yellow',
                       'Orange_585_610': 'Orange',
                       'Red_625_660': 'Red',
                       'Far_Red_680_715': 'Far_Red'}

        Summary_Tab = pd.read_excel(io=file, sheet_name='Summary', header=2)
        COC_Tab = pd.read_excel(io=file, sheet_name='Chain of Custody')
        Summary_COC_Data = Summary_Tab.set_index(['Test Guid', 'Replicate Number']).join(COC_Tab.set_index(
            ['Test Guid', 'Replicate Number']).loc[:, [x for x in COC_Tab.columns if x not in Summary_Tab.columns]])

        channelDataDict = {}
        for channel in channelDict:
            channelDataDict[channel] = nmdx_file_parser.readChannelData(
                file, channel, channelDict[channel])
        channelDataFinal = pd.concat(
            [channelDataDict[df] for df in channelDataDict if len(channelDataDict[df]) > 0], axis=0)

        channelDataFinal.set_index(
            ['Target Result Guid', 'Processing Step', 'Channel'], append=True, inplace=True)
        for i in range(1, 256):
            if "Readings " + str(i) not in channelDataFinal.columns:
                channelDataFinal["Readings "+str(i)] = np.nan
        channelDataFinal_readings = channelDataFinal.loc[:, [
            'Readings '+str(i) for i in range(1, 256)]]
        channelDataFinal_summary = channelDataFinal.swaplevel(
            3, 0).swaplevel(3, 1).swaplevel(3, 2)
        channelDataFinal_summary = channelDataFinal_summary.loc['Raw'].drop(
            ['Readings '+str(i) for i in range(1, 256)], axis=1)

        return Summary_COC_Data, channelDataFinal_summary, channelDataFinal_readings

    def scrapeFile(self, file, filename):

        summary_coc, channel_summary, channel_readings = nmdx_file_parser.readRawData(
            file)
        for col in channel_summary.columns:
            if 'Barcode' in col:
                channel_summary[col] = channel_summary[col].astype(str)
                channel_summary[col] = channel_summary[col].str.replace(
                    "_x001D_", " ")
                channel_summary[col] = channel_summary[col].replace(
                    "nan", np.nan)
        channel_summary = channel_summary.astype(
            object).where(pd.notna(channel_summary), None)

        for col in summary_coc.columns:
            if 'Barcode' in col:
                summary_coc[col] = summary_coc[col].astype(str)
                summary_coc[col] = summary_coc[col].str.replace("_x001D_", " ")
                summary_coc[col] = summary_coc[col].replace("nan", np.nan)
            if 'ADP Position' in col:
                summary_coc[col] = summary_coc[col].astype(str)
            if 'Serial' in col:
                summary_coc[col] = summary_coc[col].astype(str)
        summary_coc = summary_coc.astype(
            object).where(pd.notna(summary_coc), None)
        for col in summary_coc.loc[:, [col for col in summary_coc if 'Date' in col]].columns:
            summary_coc[col] = pd.to_datetime(summary_coc[col], utc=False).apply(
                lambda x: x.replace(tzinfo=pytz.utc))

        channel_readings = channel_readings.astype(
            object).where(pd.notna(channel_readings), None)

        channel_summary['File Source'] = filename
        channel_readings['File Source'] = filename
        summary_coc['File Source'] = filename
        summary_coc.rename({'Flags': 'Summary Flags'}, axis=1, inplace=True)

        flat_data = summary_coc.join(channel_summary.loc[:, [x for x in channel_summary.columns if x not in summary_coc.columns]]).join(
            channel_readings.loc[:, [x for x in channel_readings.columns if x not in channel_summary.columns]])

        flat_data.replace('None', np.nan, inplace=True)
        flat_data.replace('nan', np.nan, inplace=True)

        # Add Target Result / Localized Result columns if not in flat_data columns
        if 'Localized Result' not in flat_data.columns:
            flat_data['Localized Result'] = np.nan

        if 'Target Result' not in flat_data.columns:
            flat_data['Target Result'] = np.nan

        return flat_data.reset_index()


class api_base:

    main_dir = "https://localhost:7107/api/"

    def __init__(self):
        self.properties = {}
        self.data = pd.DataFrame()
        self.responseColumnName = None

    def create_object(self):

        # Make sure all Columns are available before Proceeding
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        return cleanobject

    # Begin Methods related to posting
    def get_unique_objects(self):
        self.objects = []

        # Make sure all Columns are available before Proceeding
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan

        unique_data = self.data.drop_duplicates(
            subset=[x for x in self.properties])
        for item in unique_data.index.unique():
            self.precusor_object = unique_data.loc[item, self.properties]
            object = unique_data.loc[item, self.properties].to_dict()
            object = {k: None if pd.isnull(
                v) else v for k, v in object.items()}
            self.objects.append(object)

    def post_objects(self):
        self.responses = pd.DataFrame(self.objects).set_index(
            [x for x in self.properties])

        for object in self.objects:

            self.cleanobject = dict(
                (self.properties[key], value) for (key, value) in object.items())

            result = self.write_post(self.cleanobject)
            key = [x for x in object.values()]
            self.responses.loc[tuple(key), self.responseColumnName] = result.headers[[
                x for x in result.headers if 'Id' in x][0]]

    def write_post(self, object):
        self.response = requests.post(self.url, json=object, verify=False)
        return self.response

    def postData(self):
        self.get_unique_objects()
        self.post_objects()
        return self.data.set_index([x for x in self.properties]).join(self.responses).reset_index()


class NeuMoDxConsumable(api_base):

    def write_post(self, object):
        if pd.isnull(object['Barcode']) == True:
            self.response = requests.post(self.url, json='', verify=False)
        else:
            self.response = requests.post(
                self.url, json=object['Barcode'], verify=False)
        return self.response


class Cartridge(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "Cartridge"
    properties = {'Pcr Cartridge Barcode': 'Barcode'}
    responseColumnName = 'CartridgeId'

    def __init__(self, data):
        self.data = data.copy()


class ExtractionPlate(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "ExtractionPlate"
    properties = {'Capture Plate Barcode': 'Barcode'}
    responseColumnName = 'ExtractionPlateId'

    def __init__(self, data):
        self.data = data.copy()


class BufferTrough(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "BufferTrough"
    properties = {'Buffer Barcode': 'Barcode'}
    responseColumnName = 'BufferTroughId'

    def __init__(self, data):
        self.data = data.copy()


class TestStrip(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "TestStrip"
    properties = {'Test Strip NeuMoDx Barcode': 'Barcode'}
    responseColumnName = 'TestStripId'

    def __init__(self, data):
        self.data = data.copy()


class LDTTestStripMM(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "LDTTestStripMM"
    properties = {'Test Strip LDT Master Mix Barcode': 'Barcode'}
    responseColumnName = 'LDTTestStripMMId'

    def __init__(self, data):
        self.data = data.copy()


class LDTTeststripPPM(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "LDTTeststripPPM"
    properties = {'Test Strip LDT Primer Probe Barcode': 'Barcode'}
    responseColumnName = 'LDTTestStripPPMId'

    def __init__(self, data):
        self.data = data.copy()


class ReleaseReagent(NeuMoDxConsumable):

    url = NeuMoDxConsumable.main_dir + "ReleaseReagent"
    properties = {'Release Reagent Barcode': 'Barcode'}
    responseColumnName = 'ReleaseReagentId'

    def __init__(self, data):
        self.data = data.copy()


class WashReagent(NeuMoDxConsumable):
    url = NeuMoDxConsumable.main_dir + "WashReagent"
    properties = {'Wash Reagent Barcode': 'Barcode'}
    responseColumnName = 'WashReagentId'

    def __init__(self, data):
        self.data = data.copy()


class Assay(api_base):

    url = api_base.main_dir + "Assays"
    properties = {'Assay Name': 'assayName',
                  'Assay Version': 'assayVersion',
                  'RP Version': 'rpVersion',
                  'Result Code': 'resultCode',
                  'Sample Specimen Type': 'sampleSpecimenType',
                  'Test Specimen Type': 'testSpecimenType',
                  'Run Type': 'runType',
                  'Dilution Factor': 'dilutionFactor',
                  'Primer/Probe': 'PrimerProbe'}
    responseColumnName = 'AssayId'

    def __init__(self, data):
        self.data = data.copy()
        self.data['RP Version'] = [
            x for x, y in self.data['RP,Assay Version'].str.split(',')]
        self.data['Dilution Factor'] = self.data['Dilution Factor'].astype(
            np.float32)


class XPCRModule(api_base):
    url = api_base.main_dir + "XPCRModules"
    properties = {'XPCR Module Serial': 'xpcrModuleSerial'}
    responseColumnName = 'XPCRModuleId'

    def __init__(self, data):
        self.data = data.copy()


class HeaterModule(api_base):
    url = api_base.main_dir + "HeaterModules"
    properties = {'Heater Module Serial': 'heaterModuleSerial'}
    responseColumnName = 'HeaterModuleId'

    def __init__(self, data):
        self.data = data.copy()


class NeuMoDxSystem(api_base):
    url = api_base.main_dir + "NeuMoDxSystems"
    properties = {'N500 Serial Number': 'n500SerialNumber',
                  'Software Version': 'neuMoDxSoftwareVersion',
                  'Hamilton Serial Number': 'hamiltonSerialNumber',
                  'Hamilton Firmware Version': 'hamiltonFirmwareVersion',
                  'Hamilton Method Version': 'hamiltonMethodVersion',
                  'Hamilton Software Version': 'hamiltonSoftwareVersion'}
    responseColumnName = 'NeuMoDxSystemId'

    def __init__(self, data):
        self.data = data.copy()


class XPCRModuleLane(api_base):
    properties = {'Pcr Cartridge Lane': 'moduleLane'}

    def __init__(self, data):
        self.data = data.copy()


class XPCRModuleConfiguration(api_base):
    properties = {'XPCRFirmwareApplicationVersion': 'xpcrFirmwareApplicationVersion',
                  'XPCRFirmwareBootloaderVersion': 'xpcrFirmwareBootloaderVersion',
                  'ABFirmwareApplicationVersion': 'abFirmwareApplicationVersion',
                  'ABFirmwareBootloaderVersion': 'abFirmwareBootloaderVersion',
                  'XPCRConfigurationStartDate': 'xpcrConfigurationStartDate',
                  'XPCRConfigurationEndDate': 'xpcrConfigurationEndDate',
                  'XPCR Module Index': 'xpcrModuleIndex'}
    responseColumnName = 'XPCRModuleConfigurationId'

    def __init__(self, data):
        self.data = data.copy()
        if 'XPCR Actuator Version' not in self.data.columns:
            self.data['XPCR Actuator Version'] = np.nan
        for col in self.properties:
            if col not in self.data.columns:
                self.data[col] = np.nan
        self.data[['XPCRFirmwareApplicationVersion', 'XPCRFirmwareBootloaderVersion', 'ABFirmwareApplicationVersion',
                   'ABFirmwareBootloaderVersion', 'XPCRConfigurationStartDate', 'XPCRConfigurationEndDate']] = np.nan
        self.data['XPCR Firmware Version'].fillna(
            'App: Null, Bolo: Null', inplace=True)
        self.data['XPCR Actuator Version'].fillna(
            'App: Null, Bolo: Null', inplace=True)
        self.data[['XPCRFirmwareApplicationVersion', 'XPCRFirmwareBootloaderVersion']] = [[x.replace(
            'App: ', ''), y.replace(' Bolo: ', '')] for x, y in self.data['XPCR Firmware Version'].str.split(',')]
        self.data[['ABFirmwareApplicationVersion', 'ABFirmwareBootloaderVersion']] = [[x.replace(
            'App: ', ''), y.replace(' Bolo: ', '')] for x, y in self.data['XPCR Actuator Version'].str.split(',')]
        for col in ['XPCRFirmwareApplicationVersion', 'XPCRFirmwareBootloaderVersion', 'ABFirmwareApplicationVersion', 'ABFirmwareBootloaderVersion']:
            self.data[col] = self.data[col].replace({'Null': 'X.X.X'})

        self.data['XPCR Module Index'] = self.data['XPCR Module Index'].astype(
            'Int64')

    def create_object(self):
        cleanobject = super().create_object()
        cleanobject['XPCRModule'] = XPCRModule(self.data).create_object()
        cleanobject['NeuMoDxSystem'] = NeuMoDxSystem(self.data).create_object()
        return cleanobject


class HeaterModuleConfiguration(api_base):
    url = api_base.main_dir + "HeaterModuleConfigurations"
    properties = {'HeaterFirmwareApplicationVersion': 'heaterFirmwareApplicationVersion',
                  'HeaterFirmwareBootloaderVersion': 'heaterFirmwareBootloaderVersion',
                  'HeaterConfigurationStartDate': 'heaterConfigurationStartDate',
                  'HeaterConfigurationEndDate': 'heaterConfigurationEndDate',
                  'Heater Module Index': 'heaterModuleIndex'}

    responseColumnName = 'HeaterModuleConfigurationId'

    def __init__(self, data):
        self.data = data.copy()
        self.data[['HeaterFirmwareApplicationVersion', 'HeaterFirmwareBootloaderVersion',
                   'HeaterConfigurationStartDate', 'HeaterConfigurationEndDate']] = np.nan
        self.data[['HeaterFirmwareApplicationVersion', 'HeaterFirmwareBootloaderVersion']] = [[x.replace(
            'App: ', ''), y.replace(' Bolo: ', '')] for x, y in self.data['Heater Firmware Version'].str.split(',')]
        self.data['Heater Module Index'] = self.data['Heater Module Index'].astype(
            'Int64')
        for col in ['HeaterFirmwareApplicationVersion', 'HeaterFirmwareBootloaderVersion']:
            self.data[col] = self.data[col].replace({'Null': 'X.X.X'})

    def create_object(self):
        cleanobject = super().create_object()
        cleanobject['HeaterModule'] = HeaterModule(self.data).create_object()
        cleanobject['NeuMoDxSystem'] = NeuMoDxSystem(self.data).create_object()
        return cleanobject


class AssayChannel(api_base):
    url = api_base.main_dir + "AssayChannels"
    properties = {'Channel': 'channel',
                  'Target Name': 'targetName'}
    # 'AssayId':'assayId',}
    responseColumnName = 'AssayChannelId'

    def __init__(self, data):
        self.data = data.copy()


class AssayChannelStep(api_base):
    url = api_base.main_dir + "AssayChannelSteps"
    properties = {'Processing Step': 'processingStep'}
    # 'AssayChannelId':'assayChannelId'}
    responseColumnName = 'AssayChannelStepId'

    def __init__(self, data):
        self.data = data.copy()


class Sample(api_base):
    url = api_base.main_dir + "Samples"
    properties = {'Test Guid': 'testGuid',
                  'Replicate Number': 'replicateNumber',
                  'Sample Type': 'sampleType',
                  'Sample ID': 'barcode',
                  'Start Date/Time': 'startDateTime',
                  'End Date/Time': 'endDateTime',
                  'Patient ID': 'patientID',
                  'Overall Result': 'overallResult'}

    responseColumnName = 'SampleId'

    def __init__(self, data):
        self.data = data.copy()
        self.data['Start Date/Time'] = self.data['Start Date/Time'].apply(
            lambda x: x.isoformat(timespec='milliseconds'))
        self.data['End Date/Time'] = self.data['End Date/Time'].apply(
            lambda x: x.isoformat(timespec='milliseconds'))
        self.data['Replicate Number'] = self.data['Replicate Number'].astype(
            'Int64')


class ChannelSummarySet(api_base):
    url = api_base.main_dir + "ChannelSummarySets"
    properties = {'Localized Result': 'localizedResult',
                  'Ct': 'ct',
                  'EPR': 'epr',
                  'End Point Fluorescence': 'endPointFluorescence',
                  'Max Peak Height': 'maxPeakHeight',
                  'Baseline Slope': 'baselineSlope',
                  'Baseline Y Intercept': 'baselineYIntercept',
                  'Baseline First Cycle': 'baselineFirstCycle',
                  'Baseline Last Cycle': 'baselineLastCycle',
                  'Calibration Coefficient': 'calibrationCoefficient',
                  'Log Conc.': 'logConc',
                  'Conc.': 'conc',
                  'Blank Reading': 'blankReading',
                  'Dark Reading': 'darkReading'}
    responseColumnName = 'ChannelSummarySetId'

    def create_objects(self):
        objects = []
        # Make sure all Columns are available before Proceeding
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.data.drop_duplicates(
            subset=[x for x in self.properties], inplace=True)
        self.data.reset_index(inplace=True)
        for item in self.data.index.unique():
            object = self.data.loc[item, self.properties].to_dict()
            object = {k: None if pd.isnull(
                v) else v for k, v in object.items()}
            object = dict((self.properties[key], value)
                          for (key, value) in object.items())
            object['AssayChannel'] = AssayChannel(
                self.data.loc[[item]]).create_object()
            object['AssayChannel']['Assay'] = Assay(
                self.data.loc[[item]]).create_object()
            objects.append(object)

        return objects

    def __init__(self, data):
        self.data = data.copy()
        self.data['Baseline First Cycle'] = self.data['Baseline First Cycle'].astype(
            'Int64')
        self.data['Baseline Last Cycle'] = self.data['Baseline Last Cycle'].astype(
            'Int64')


class CrossTalkSetting(api_base):
    url = api_base.main_dir + "CrossTalkSettings"
    properties = {'Green Crosstalk Into Yellow': 'greenIntoYellow',
                  'Yellow Crosstalk Into Orange': 'yellowIntoOrange',
                  'Orange Crosstalk Into Red': 'orangeIntoRed',
                  'Red Crosstalk Into Far Red': 'redIntoFarRed'}
    responseColumnName = 'CrossTalkSettingId'

    def __init__(self, data):
        self.data = data.copy()

    def create_object(self):

        self.data[[x for x in self.properties if x not in self.data.columns]] = 1.0
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        return cleanobject


class TipRack(api_base):
    url = api_base.main_dir + "TipRacks"
    properties = {'LoadDateTime': 'loadDateTime',
                  'LastLoadDateTime': 'lastLoadDateTime',
                  'CarrierPosition': 'carrierPosition',
                  'StackPosition': 'stackPosition',
                  'CarrierGroupId': 'carrierGroupId'}


class SampleLargeTipRack(TipRack):

    responseColumnName = 'SampleLargeTipRackId'
    TipRack.properties['Sample Large Tip Rack Barcode'] = 'barcode'

    def __init__(self, data):
        self.data = data.copy()


class BufferLargeTipRack(TipRack):

    responseColumnName = 'BufferLargeTipRackId'
    TipRack.properties['Buffer Large Tip Rack Barcode'] = 'barcode'

    def __init__(self, data):
        self.data = data.copy()


class LhpBLargeTipRack(TipRack):

    responseColumnName = 'LhpBLargeTipRackId'
    TipRack.properties['LHPB Large Tip Rack Barcode'] = 'barcode'

    def __init__(self, data):
        self.data = data.copy()


class SmallTipRack(TipRack):

    responseColumnName = 'SmallTipRackId'
    TipRack.properties['Small Tip Rack Barcode'] = 'barcode'

    def __init__(self, data):
        self.data = data.copy()


class TestStripMap(api_base):
    url = api_base.main_dir + "TestStripMaps"


class TestStripMapIVD(TestStripMap):

    responseColumnName = 'TestStripMapIVDId'
    properties = {'Test Strip NeuMoDx Carrier': 'carrier',
                  'Test Strip NeuMoDx Carrier Position': 'carrierPosition',
                  'Test Strip NeuMoDx Well': 'well'}

    def __init__(self, data):
        self.data = data.copy()
        self.data['Test Strip NeuMoDx Carrier'] = self.data['Test Strip NeuMoDx Carrier'].str.replace(
            'TestStrips', '').fillna(np.nan).astype('Int64')
        self.data['Test Strip NeuMoDx Carrier'] = np.where(
            self.data['Test Strip NeuMoDx Carrier'].isnull(), np.nan, self.data['Test Strip NeuMoDx Carrier'])


class TestStripMapMM(TestStripMap):
    responseColumnName = 'TestStripMapMMId'
    properties = {'Test Strip LDT Master Mix Carrier': 'carrier',
                  'Test Strip LDT Master Mix Carrier Position': 'carrierPosition',
                  'Test Strip LDT Master Mix Well': 'well'}

    def __init__(self, data):
        self.data = data.copy()
        self.data['Test Strip LDT Master Mix Carrier'] = self.data['Test Strip LDT Master Mix Carrier'].str.replace(
            'TestStrips', '').fillna(np.nan).astype('Int64')
        self.data['Test Strip LDT Master Mix Carrier'] = np.where(
            self.data['Test Strip LDT Master Mix Carrier'].isnull(), np.nan, self.data['Test Strip LDT Master Mix Carrier'])


class TestStripMapPPM(TestStripMap):
    responseColumnName = 'TestStripMapPPMId'
    properties = {'Test Strip LDT Primer Carrier': 'carrier',
                  'Test Strip LDT Primer Carrier Position': 'carrierPosition',
                  'Test Strip LDT Primer Well': 'well'}

    def __init__(self, data):
        self.data = data.copy()
        self.data['Test Strip LDT Primer Carrier'] = self.data['Test Strip LDT Primer Carrier'].str.replace(
            'TestStrips', '').fillna(np.nan).astype('Int64')
        self.data['Test Strip LDT Primer Carrier'] = np.where(
            self.data['Test Strip LDT Primer Carrier'].isnull(), np.nan, self.data['Test Strip LDT Primer Carrier'])


class ChainOfCustodySet(api_base):

    properties = {'SampleId': 'sampleId',
                  'SampleDefinition': 'sampleDefinitionVM',
                  'LhpATrace': 'lhpATraceVM',
                  'LysisBindingTrace': 'lysisBindingTraceVM',
                  'LhpBTrace': 'lhpBTraceVM',
                  'ExtractionTrace': 'extractionTraceVM',
                  'LhpCTrace': 'lhpCTraceVM',
                  'PcrTrace': 'PcrTraceVM'}

    url = api_base.main_dir + "ChainOfCustodySets"
    responseColumnName = 'ChainOfCustodySetId'

    def __init__(self, data):

        self.data = data.copy()

    def get_unique_objects(self):
        self.objects = []

        # Make sure all Columns are available before Proceeding
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan

        unique_data = self.data.drop_duplicates(
            subset=[x for x in self.properties])
        for item in unique_data.index.unique():
            self.sampleSlice = unique_data.loc[item, :].to_frame().transpose()
            object = unique_data.loc[item, self.properties].to_dict()
            object = {k: None if pd.isnull(
                v) else v for k, v in object.items()}

            object['SampleDefinition'] = SampleDefinition(
                self.sampleSlice).create_object()
            object['LhpATrace'] = LhpATrace(self.sampleSlice).create_object()
            object['LysisBindingTrace'] = LysisBindingTrace(
                self.sampleSlice).create_object()
            object['LhpBTrace'] = LhpBTrace(self.sampleSlice).create_object()
            object['ExtractionTrace'] = ExtractionTrace(
                self.sampleSlice).create_object()
            object['LhpCTrace'] = LhpCTrace(self.sampleSlice).create_object()
            object['PcrTrace'] = PcrTrace(self.sampleSlice).create_object()

            self.objects.append(object)

    def create_object(self):

        cleanobject = {}
        cleanobject['SampleDefinition'] = SampleDefinition(
            self.data).create_object()
        cleanobject['LhpATrace'] = LhpATrace(self.data).create_object()
        cleanobject['LysisBindingTrace'] = LysisBindingTrace(
            self.data).create_object()
        cleanobject['LhpBTrace'] = LhpBTrace(self.data).create_object()
        cleanobject['ExtractionTrace'] = ExtractionTrace(
            self.data).create_object()
        cleanobject['LhpCTrace'] = LhpCTrace(self.data).create_object()
        cleanobject['PcrTrace'] = PcrTrace(self.data).create_object()

        return cleanobject

    def post_objects(self):
        self.responses = pd.DataFrame(self.objects).set_index(['SampleId'])

        for object in self.objects:

            self.cleanobject = dict(
                (self.properties[key], value) for (key, value) in object.items())

            result = self.write_post(self.cleanobject)
            self.responses.loc[self.cleanobject['sampleId'], self.responseColumnName] = result.headers[[
                x for x in result.headers if 'Id' in x][0]]

    def postData(self):
        self.get_unique_objects()
        self.post_objects()
        return self.data.set_index(['SampleId']).join(self.responses.loc[:, [x for x in self.responses.columns if x not in self.data.columns]]).reset_index()


class SampleDefinition(api_base):
    properties = {'Test Comment': 'testComment',
                  'Control Name': 'controlName',
                  'Comment': 'comment',
                  'Sample Origin': 'sampleOrigin',
                  'Status': 'status',
                  'Control Prefix': 'controlPrefix',
                  'Control Serial': 'controlSerial'}
    # 'OperatorId':'operatorId'}

    def __init__(self, data_item):

        self.data = data_item.copy()

    def create_object(self):
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        cleanobject['Operator'] = Operator(self.data).create_object()
        return cleanobject


class LhpATrace(api_base):
    properties = {
        'Buffer Large Tip Position': 'bufferLargeTipRackPosition',
        'Sample Large Tip Position': 'sampleLargeTipRackPosition',
        'Sample Tube Rack': 'sampleTubeRack',
        'Sample Tube Position': 'sampleTubePosition',
        'LHPA Start Date Time': 'lhpAStartDateTime',
        'LHPA ADP Position': 'lhpAADPPosition',
        'Specimen Tube Type': 'specimenTubeType'}
    #  'SampleLargeTipRackId':'sampleLargeTipRackId',
    #  'BufferLargeTipRackId':'bufferLargeTipRackId',
    #  }

    def __init__(self, data_item):

        self.data = data_item.copy()
        self.data['Buffer Large Tip Position'] = self.data['Buffer Large Tip Position'].astype(
            'Int64')
        self.data['Sample Large Tip Position'] = self.data['Sample Large Tip Position'].astype(
            'Int64')
        self.data['LHPA Start Date Time'] = self.data['LHPA Start Date Time'].apply(
            lambda x: x.isoformat(timespec='milliseconds'))
        self.data['LHPA ADP Position'] = self.data['LHPA ADP Position'].astype(
            str)
        self.data['Sample Tube Rack'] = self.data['Sample Tube Rack'].astype(
            'Int64')
        self.data['Sample Tube Position'] = self.data['Sample Tube Position'].astype(
            'Int64')
        self.data['Specimen Tube Type'] = self.data['Specimen Tube Type'].astype(
            str)

    def create_object(self):

        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        cleanobject['SampleLargeTipRack'] = SampleLargeTipRack(
            self.data).create_object()
        cleanobject['BufferLargeTipRack'] = BufferLargeTipRack(
            self.data).create_object()

        return cleanobject


class LysisBindingTrace(api_base):
    properties = {'Capture Plate Well': 'capturePlateWell'}

    def __init__(self, data_item):

        self.data = data_item.copy()
        self.data['Capture Plate Well'] = self.data['Capture Plate Well'].astype(
            'Int64')


class LhpBTrace(api_base):
    properties = {
        'LHPB Large Tip Position': 'lhpBLargeTipRackPosition',
        'LHPB Start Date Time': 'lhpBStartDateTime',
        'LHPB ADP Position': 'lhpBADPPosition'}
    # 'LhpBLargeTipRackId':'lhpBLargeTipRackId',

    def __init__(self, data_item):
        self.data = data_item.copy()
        self.data['LHPB Large Tip Position'] = self.data['LHPB Large Tip Position'].astype(
            'Int64')
        self.data['LHPB Start Date Time'] = np.where(self.data['LHPB Start Date Time'].isnull(
        ), np.nan, self.data['LHPB Start Date Time'].apply(lambda x: x.isoformat(timespec='milliseconds')))
        self.data['LHPB ADP Position'] = self.data['LHPB ADP Position'].astype(
            str)

    def create_object(self):
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        cleanobject['LhpBLargeTipRack'] = LhpBLargeTipRack(
            self.data).create_object()
        return cleanobject


class ExtractionTrace(api_base):
    properties = {'Start Heater Ambient Temperature C': 'startHeaterAmbientTemperatureC',
                  'End Heater Ambient Temperature C': 'endHeaterAmbientTemperatureC',
                  'Bulk Reagent Drawer': 'BulkReagentDrawer'}

    def __init__(self, data_item):
        self.data = data_item.copy()
        self.data['Start Heater Ambient Temperature C'] = self.data['Start Heater Ambient Temperature C'].astype(
            float)
        self.data['End Heater Ambient Temperature C'] = self.data['End Heater Ambient Temperature C'].astype(
            float)
        self.data['Bulk Reagent Drawer'] = self.data['Bulk Reagent Drawer'].astype(
            str)


class LhpCTrace(api_base):
    properties = {
        'Small Tip Position': 'smallTipPosition',
        'LHPC Start Date Time': 'lhpCStartDateTime',
        'LHPC ADP Position': 'lhpCADPPosition'}

    #  'TestStripMapIVDId':'testStripMapIVDId',
    #  'TestStripMapMMId':'testStripMapMMId',
    #  'TestStripMapPPMId':'testStripMapPPMId',
    #  'SmallTipRackId':'smallTipRackId',}

    def __init__(self, data_item):
        self.data = data_item.copy()
        self.data['Small Tip Position'] = self.data['Small Tip Position'].astype(
            'Int64')
        self.data['LHPC Start Date Time'] = np.where(self.data['LHPC Start Date Time'].isnull(
        ), np.nan, self.data['LHPC Start Date Time'].apply(lambda x: x.isoformat(timespec='milliseconds')))
        self.data['LHPC ADP Position'] = self.data['LHPC ADP Position'].astype(
            str)

    def create_object(self):
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        cleanobject['SmallTipRack'] = SmallTipRack(self.data).create_object()
        cleanobject['TestStripMapIVD'] = TestStripMapIVD(
            self.data).create_object()
        cleanobject['TestStripMapMM'] = TestStripMapMM(
            self.data).create_object()
        cleanobject['TestStripMapPPM'] = TestStripMapPPM(
            self.data).create_object()

        return cleanobject


class PcrTrace(api_base):
    properties = {'Start Pcr Ambient Temperature C': 'startPcrAmbientTemperatureC',
                  'End Pcr Ambient Temperature C': 'endPcrAmbientTemperatureC',
                  'PCR Start Date Time': 'pcrStartDateTime'}

    def __init__(self, data_item):
        self.data = data_item.copy()
        self.data['Start Pcr Ambient Temperature C'] = self.data['Start Pcr Ambient Temperature C'].astype(
            float)
        self.data['End Pcr Ambient Temperature C'] = self.data['End Pcr Ambient Temperature C'].astype(
            float)
        self.data['PCR Start Date Time'] = np.where(self.data['PCR Start Date Time'].isnull(
        ), np.nan, self.data['PCR Start Date Time'].apply(lambda x: x.isoformat(timespec='milliseconds')))

    def create_object(self):
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan
        self.precusor_object = self.data[self.properties]
        object = self.precusor_object.to_dict(orient='records')[0]
        object = {k: None if pd.isnull(v) else v for k, v in object.items()}
        cleanobject = dict((self.properties[key], value)
                           for (key, value) in object.items())
        cleanobject['CrossTalkSetting'] = CrossTalkSetting(
            self.data.fillna(1)).create_object()
        return cleanobject


class Operator(api_base):

    properties = {'Test Operator': 'userName', 'Role': 'role'}
    url = api_base.main_dir + "Operators"
    responseColumnName = 'OperatorId'

    def __init__(self, data):
        self.data = data.copy()


class ReadingSet(api_base):
    # ,'AssayChannelStepId':'assayChannelStepId','SampleId':'sampleId'}
    properties = {'Readings': 'readings'}
    url = api_base.main_dir + "ReadingSets"
    responseColumnName = 'ReadingSetId'

    def __init__(self, data):
        self.data = data.copy()

    def create_objects(self):

        objects = []

        # Make sure all Columns are available before Proceeding
        self.data[[x for x in self.properties if x not in self.data.columns]] = np.nan

        self.data.reset_index(inplace=True)
        for item in self.data.index.unique():
            object = self.data.loc[item, self.properties].to_dict()
            object = {k: None if pd.isnull(
                v) else v for k, v in object.items()}
            object['Readings'] = Readings(
                self.data.loc[item]).create_readings_list()
            object['AssayChannelStep'] = AssayChannelStep(
                self.data.loc[[item]]).create_object()
            object['AssayChannelStep']['AssayChannel'] = AssayChannel(
                self.data.loc[[item]]).create_object()
            object['AssayChannelStep']['AssayChannel']['Assay'] = Assay(
                self.data.loc[[item]]).create_object()
            objects.append(object)

        return objects

    def post_objects(self):
        self.responses = pd.DataFrame(
            self.objects).set_index(['AssayChannelStepId'])

        for object in self.objects:

            self.cleanobject = dict(
                (self.properties[key], value) for (key, value) in object.items())

            result = self.write_post(self.cleanobject)
            self.responses.loc[self.cleanobject['assayChannelStepId'], self.responseColumnName] = result.headers[[
                x for x in result.headers if 'Id' in x][0]]

    def postData(self):
        self.get_unique_objects()
        self.post_objects()
        return self.data.set_index(['AssayChannelStepId']).join(self.responses.loc[:, [x for x in self.responses.columns if x not in self.data.columns]]).reset_index()


class Readings(api_base):

    def __init__(self, data_item):
        self.data = data_item.copy()
        self.data = self.data[["Readings " +
                               str(i) for i in range(1, 200)]].astype(float)

    def create_readings_list(self):
        readings_array = [[int(key.replace("Readings ", "")), value]
                          for (key, value) in self.data.to_dict().items()]
        readings_list = [{'cycle': item[0], 'value':item[1]}
                         for item in readings_array if pd.isnull(item[1]) == False]
        return readings_list


class Flag(api_base):

    def __init__(self, data_item):
        self.data = data_item.copy()

    def create_objects(self):
        objects = []
        # Make sure all Columns are available before Proceeding
        self.data.drop_duplicates(subset=['Flags', 'Channel'], inplace=True)
        self.data.reset_index(inplace=True)
        for item in self.data.index.unique():
            assaychannel = AssayChannel(self.data.loc[[item]]).create_object()
            assaychannel['Assay'] = Assay(
                self.data.loc[[item]]).create_object()
            if self.data.loc[item, 'Flags'] == None:
                flags_list = []
            else:
                flags_list = self.data.loc[item, 'Flags'].split('), ')
            for flag in flags_list:
                obj = {}
                error_code, flag_string = flag.split(" (")
                error_code = int(error_code)
                severity, description = flag_string.replace(
                    ")", "").split(", ")
                flag_object = {"errorCode": error_code,
                               "severity": severity, "flagdescription": description}
                obj['assaychannel'] = assaychannel
                obj['flag'] = flag_object
                objects.append(obj)
        return objects


class SampleJson:
    base_url = 'https://localhost:7107/api/'

    def __init__(self):
        self.sample_json = {}
        self.response = ''

    def create_sample_json(self, sample_data):
        """
        Used to convert line data for a given sample to a sample json file
        Parameters
        ----------
        sample_data (pandas.DataFrame): A slice of a Pandas DataFrame that represents all data for a NeuMoDx Sample
                For best practice perform following actions to create sample_data:
                1. Convert a Raw Data File to a Flat file using a nmdx_file_parser
                2. Set index to Test Guid and replicate Number.
                3. Select of one unique Test Guid / replicate number combination.
        Returns
        -------
        dictionary form of sample_json model of the data provided.
        """
        sample = Sample(sample_data.reset_index()).create_object()
        sample['Cartridge'] = Cartridge(sample_data).create_object()
        sample['TestStrip'] = TestStrip(sample_data).create_object()
        sample['BufferTrough'] = BufferTrough(sample_data).create_object()
        sample['ReleaseReagent'] = ReleaseReagent(sample_data).create_object()
        sample['WashReagent'] = WashReagent(sample_data).create_object()
        sample['ExtractionPlate'] = ExtractionPlate(
            sample_data).create_object()
        sample['LDTTestStripMM'] = LDTTestStripMM(sample_data).create_object()
        sample['LDTTestStripPPM'] = LDTTestStripMM(sample_data).create_object()
        sample['NeuMoDxSystem'] = NeuMoDxSystem(sample_data).create_object()
        sample['XPCRModuleLane'] = XPCRModuleLane(sample_data).create_object()
        sample['XPCRModuleConfiguration'] = XPCRModuleConfiguration(
            sample_data).create_object()
        sample['HeaterModuleConfiguration'] = HeaterModuleConfiguration(
            sample_data).create_object()
        sample['Assay'] = Assay(sample_data).create_object()
        sample['ReadingSets'] = ReadingSet(sample_data).create_objects()
        sample['ChainOfCustodySet'] = ChainOfCustodySet(
            sample_data).create_object()
        sample['ChannelSummarySets'] = ChannelSummarySet(
            sample_data).create_objects()
        sample['ChannelFlags'] = Flag(sample_data).create_objects()

        self.sample_json = sample

    def post_sample_json(self):
        """
        Used to post json to web api.
        """
        url = self.base_url + "SampleJson"
        self.response = requests.post(url, json=self.sample_json, verify=False)
