import pandas as pd
import numpy as np
import asyncio
import aiohttp
import os


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


class SampleJSONReader:
    """
    A class used to read sampleJSON style data from NeuMoDxResultsDB into a Pandas DataFrame
    Methods
    -------
    getCOC: Reads SampleCOC information from sampleJSON file.
    getChannelSummary: Reads SampleChannelSummaryData from sampleJSON file.
    getChannelReadings: Reads ChannelReadings from sampleJSON file.
    """

    column_mapper = {
        "id": "id",
        "testGuid": "Test Guid",
        "replicateNumber": "Replicate Number",
        "sampleType": "Sample Type",
        "barcode": "Sample ID",
        "startDateTime": "Start Date Time",
        "endDateTime": "End Date Time",
        "patientID": "Patient ID",
        "overallResult": "Overall Result",
        "cartridge": "Cartridge",
        "cartridgeId": "Cartridge Id",
        "bufferTrough": "Buffer Trough",
        "bufferTroughId": "Buffer Trough Id",
        "extractionPlate": "Extraction Plate",
        "extractionPlateId": "Extraction Plate Id",
        "testStrip": "Test Strip",
        "testStripId": "Test Strip Id",
        "ldtTestStripMM": "LDT Test Strip MM",
        "ldtTestStripMMId": "LDT Test Strip MM Id",
        "ldtTestStripPPM": "LDT Test Strip PPM",
        "ldtTestStripPPMId": "LDT Test Strip PPM Id",
        "releaseReagent": "Release Reagent",
        "releaseReagentId": "Release Reagent Id",
        "washReagent": "Wash Reagent",
        "washReagentId": "Wash Reagent Id",
        "neuMoDxSystem": "NeuMoDx System",
        "neuMoDxSystemId": "NeuMoDx System Id",
        "xpcrModuleConfiguration": "xpcrModuleConfiguration",
        "xpcrModuleConfigurationId": "XPCR Module Configuration Id",
        "heaterModuleConfiguration": "heaterModuleConfiguration",
        "heaterModuleConfigurationId": "Heater Module Configuration Id",
        "assay": "Assay",
        "assayId": "Assay Id",
        "chainOfCustodySet": "chainOfCustodySet",
        "rawDataFileSamples": "rawDataFileSamples",
        "channelSummarySets": "channelSummarySets",
        "readingSets": "readingSets",
        "sampleChannelFlags": "sampleChannelFlags",
        "sampleImportDate": "sampleImportDate",
        "cosmosID": "Cosmos Id",
    }

    def __init__(self, json_data):
        self.DataFrame = (
            pd.read_json(json_data).rename(
                self.column_mapper, axis=1).set_index("id")
        )
        self.DataFrame.drop(
            ["xpcrModule", "heaterModule", "xpcrModuleId", "heaterModuleId"],
            axis=1,
            inplace=True,
        )

    def getSampleSummary(self):
        print("im here")
        # self.DataFrame.loc[self.testid] =

    def getSampleCOC(self):
        print("getSamples")
        # self.DataFrame.loc[self.testid, 'Test Guid'] = self.data['testGuid']

    def unpackConsumable(self, consumable: str, drop_parent=True):
        """
        A function used to unpack consumable barcode, lot, serial & expiration from a consumables object loaded into dataframe.
        Parameters
        ----------
        consumable (str): Name of consumable column to unpack
        drop_parent (bool): Whether or not to drop parent column used to unpack data.
        """
        columns = [
            consumable + " Barcode",
            consumable + " Lot",
            consumable + " Serial",
            consumable + " Expiration",
        ]
        self.DataFrame.loc[:, columns] = [
            [x["barcode"], x["lot"], x["serial"], x["expiration"]]
            for x in self.DataFrame[consumable].values
        ]
        if drop_parent:
            self.DataFrame.drop(consumable, axis=1, inplace=True)

    def unpackConsumables(
        self,
        consumables=[
            "Buffer Trough",
            "Extraction Plate",
            "Cartridge",
            "Release Reagent",
            "Wash Reagent",
            "LDT Test Strip MM",
            "LDT Test Strip PPM",
            "Test Strip",
        ],
    ):
        """
        A function used to unpack all consumables included in dataframe
        """
        for consumable in consumables:
            if consumable in self.DataFrame.columns:
                SampleJSONReader.unpackConsumable(self, consumable)

    def unpackNeuMoDxSystem(self, drop_parent=True):
        """
        A function used to unpack NeuMoDx System Fields from a NeuMoDxSystem object loaded into dataframe.T
        Parameters:
        -----------
        drop_parent (bool): Whether or not to drop parent column used to unpack data.
        """

        columns = [
            "N500 Serial Number",
            "NeuMoDx Software Version",
            "Hamilton Serial Number",
            "Hamilton Firmware Version",
            "Hamilton Method Version",
            "Hamilton Software Version",
        ]

        self.DataFrame.loc[:, columns] = [
            [
                x["n500SerialNumber"],
                x["neuMoDxSoftwareVersion"],
                x["hamiltonSerialNumber"],
                x["hamiltonFirmwareVersion"],
                x["hamiltonMethodVersion"],
                x["hamiltonSoftwareVersion"],
            ]
            for x in self.DataFrame["NeuMoDx System"].values
        ]

        if drop_parent:
            self.DataFrame.drop("NeuMoDx System", axis=1, inplace=True)

    def unpackXPCRModuleLane(self, drop_parent=True):
        """
        A function used to unpack XPCR Module Lane Fields from a XPCR Module Lane object loaded into dataframe.
        Parameters:
        -----------
        drop_parent (bool): Whether or not to drop parent column used to unpack data.
        """
        xpcrmodulelanes = [x for x in self.DataFrame["xpcrModuleLane"].values]

        xpcrmodulelaneMap = {"XPCR Module Lane": "moduleLane"}

        xpcrmodulelaneData = {}
        for category in xpcrmodulelaneMap:
            xpcrmodulelaneData[category] = [
                x[xpcrmodulelaneMap[category]] for x in xpcrmodulelanes
            ]

        self.DataFrame.loc[:, [col for col in xpcrmodulelaneData]] = pd.DataFrame(
            index=self.DataFrame.index, data=xpcrmodulelaneData
        )

        if drop_parent:
            self.DataFrame.drop("xpcrModuleLane", axis=1, inplace=True)

    def unpackXPCRModuleConfiguration(self, drop_parent=True):
        """
        A function used to unpack XPCR Module Configuration Fields from a xpcrModuleConfiguration object loaded into dataframe.
        Parameters:
        -----------
        drop_parent (bool): Whether or not to drop parent column used to unpack data.
        """
        columns = [
            "XPCR Firmware Application Version",
            "XPCR Firmware Bootloader Version",
            "AB Firmware Application Version",
            "AB Firmware Bootloader Version",
            "XPCR ConfigurationEndDate",
            "XPCR ConfigurationStartDate",
            "XPCR Module Index",
            "XPCR Module Serial",
            "XPCR Module Id",
        ]

        self.DataFrame.loc[:, columns] = [
            [
                x["xpcrFirmwareApplicationVersion"],
                x["xpcrFirmwareBootloaderVersion"],
                x["abFirmwareApplicationVersion"],
                x["abFirmwareBootloaderVersion"],
                x["xpcrConfigurationEndDate"],
                x["xpcrConfigurationStartDate"],
                x["xpcrModuleIndex"],
                x["xpcrModule"]["xpcrModuleSerial"],
                x["xpcrModuleId"],
            ]
            for x in self.DataFrame["xpcrModuleConfiguration"].values
        ]

        if drop_parent:
            self.DataFrame.drop("xpcrModuleConfiguration",
                                axis=1, inplace=True)

    def unpackHeaterModuleConfiguration(self, drop_parent=True):
        """
        A function used to unpack Heater Module Configuration Fields from a heaterModuleConfiguration object loaded into dataframe.
        Parameters:
        -----------
        drop_parent (bool): Whether or not to drop parent column used to unpack data.
        """
        columns = [
            "Heater Module Index",
            "Heater Firmware Application Version",
            "Heater Firmware Bootloader Version",
            "Heater Configuration Start Date",
            "Heater Configuration End Date",
            "Heater Module Serial",
            "Heater Module Id",
        ]
        self.DataFrame.loc[:, columns] = [
            [
                x["heaterModuleIndex"],
                x["heaterFirmwareApplicationversion"],
                x["heaterFirmwareBootloaderVersion"],
                x["heaterConfigurationStartDate"],
                x["heaterConfigurationEndDate"],
                x["heaterModule"]["heaterModuleSerial"],
                x["heaterModuleId"],
            ]
            for x in self.DataFrame["heaterModuleConfiguration"].values
        ]
        if drop_parent:
            self.DataFrame.drop("heaterModuleConfiguration",
                                axis=1, inplace=True)

    def unpackChainOfCustodySet(self, drop_parent=True):
        chainofcustodysets = [
            x for x in self.DataFrame["chainOfCustodySet"].values]
        sampledefinitions = [x["sampleDefinition"] for x in chainofcustodysets]
        operators = [x["operator"] for x in sampledefinitions]
        lhpatraces = [x["lhpATrace"] for x in chainofcustodysets]
        bufferlargetipracks = [x["bufferLargeTipRack"] for x in lhpatraces]
        samplelargetipracks = [x["sampleLargeTipRack"] for x in lhpatraces]
        lysisbindingtraces = [x["lysisBindingTrace"]
                              for x in chainofcustodysets]
        lhpbtraces = [x["lhpBTrace"] for x in chainofcustodysets]
        lhpblargetipracks = [x["lhpBLargeTipRack"] for x in lhpbtraces]
        extractiontraces = [x["extractionTrace"] for x in chainofcustodysets]
        lhpctraces = [x["lhpCTrace"] for x in chainofcustodysets]
        smalltipracks = [x["smallTipRack"] for x in lhpctraces]
        teststripMapIVDs = [x["testStripMapIVD"] for x in lhpctraces]
        teststripMapLDTMMs = [x["testStripMapMM"] for x in lhpctraces]
        teststripMapLDTPPMs = [x["testStripMapPPM"] for x in lhpctraces]
        pcrtraces = [x["pcrTrace"] for x in chainofcustodysets]
        crosstalksettings = [x["crossTalkSetting"] for x in pcrtraces]

        chainofcustodysetMap = {
            "Sample Definition Id": "sampleDefinitionId",
            "LhpA Trace Id": "lhpATraceId",
            "Lysis Binding Trace Id": "lysisBindingTraceId",
            "LhpB Trace Id": "lhpBTraceId",
            "Extraction Trace Id": "extractionTraceId",
            "Pcr Trace Id": "pcrTraceId",
        }

        chainofcustodysetData = {}
        for category in chainofcustodysetMap:
            chainofcustodysetData[category] = [
                x[chainofcustodysetMap[category]] for x in chainofcustodysets
            ]

        self.DataFrame.loc[:, [col for col in chainofcustodysetMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=chainofcustodysetData
        )

        sampleDefinitionMap = {
            "Test Comment": "testComment",
            "Control Name": "controlName",
            "Comment": "comment",
            "Sample Origin": "sampleOrigin",
            "Status": "status",
            "Control Prefix": "controlPrefix",
            "Control Serial": "controlSerial",
        }

        sampleDefinitionData = {}
        for category in sampleDefinitionMap:
            sampleDefinitionData[category] = [
                x[sampleDefinitionMap[category]] for x in sampledefinitions
            ]
        self.DataFrame.loc[:, [col for col in sampleDefinitionMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=sampleDefinitionData
        )

        operatorMap = {
            "Operator Id": "id",
            "User Name": "userName",
            "Role": "role",
        }

        operatorData = {}
        for category in operatorMap:
            operatorData[category] = [x[operatorMap[category]]
                                      for x in operators]
        self.DataFrame.loc[:, [col for col in operatorMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=operatorData
        )

        lhpatraceMap = {
            "Buffer Large Tip Rack Id": "bufferLargeTipRackId",
            "Buffer Large Tip Rack Position": "bufferLargeTipRackPosition",
            "Sample Large Tip Rack Id": "sampleLargeTipRackId",
            "Sample Large Tip RackPosition": "sampleLargeTipRackPosition",
            "Sample Tube Rack": "sampleTubeRack",
            "Sample Tube Position": "sampleTubePosition",
            "LhpA Start Date Time": "lhpAStartDateTime",
            "LhpA ADP Position": "lhpAADPPosition",
            "specimen Tube Type": "specimenTubeType",
        }

        lhpatraceData = {}
        for category in lhpatraceMap:
            lhpatraceData[category] = [x[lhpatraceMap[category]]
                                       for x in lhpatraces]
        self.DataFrame.loc[:, [col for col in lhpatraceMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=lhpatraceData
        )

        lhpbtraceMap = {
            "LhpB Large Tip Rack Position": "lhpBLargeTipRackPosition",
            "LhpB Start Date Time": "lhpBStartDateTime",
            "LhpB ADP Position": "lhpBADPPosition",
        }

        lhpbtraceData = {}
        for category in lhpbtraceMap:
            lhpbtraceData[category] = [x[lhpbtraceMap[category]]
                                       for x in lhpbtraces]
        self.DataFrame.loc[:, [col for col in lhpbtraceMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=lhpbtraceData
        )

        extractiontraceMap = {
            "Start Heater Ambient Temperature C": "startHeaterAmbientTemperatureC",
            "End Heater Ambient Temperature C": "endHeaterAmbientTemperatureC",
            "Bulk Reagent Drawer": "bulkReagentDrawer",
        }

        extractiontraceData = {}
        for category in extractiontraceMap:
            extractiontraceData[category] = [
                x[extractiontraceMap[category]] for x in extractiontraces
            ]
        self.DataFrame.loc[:, [col for col in extractiontraceMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=extractiontraceData
        )

        lhpctraceMap = {
            "LhpC ADP Position": "lhpCADPPosition",
            "Small Tip Position": "smallTipPosition",
            "LhpC Start Date Time": "lhpCStartDateTime",
        }
        lhpctraceData = {}
        for category in lhpctraceMap:
            lhpctraceData[category] = [x[lhpctraceMap[category]]
                                       for x in lhpctraces]
        self.DataFrame.loc[:, [col for col in lhpctraceMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=lhpctraceData
        )

        pcrtraceMap = {
            "PCR Start Date Time": "pcrStartDateTime",
            "Start PCR Ambient Temperature C": "startPcrAmbientTemperatureC",
            "End PCR Ambient Temperature C": "endPcrAmbientTemperatureC",
        }

        pcrtraceData = {}
        for category in pcrtraceMap:
            pcrtraceData[category] = [x[pcrtraceMap[category]]
                                      for x in pcrtraces]
        self.DataFrame.loc[:, [col for col in pcrtraceMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=pcrtraceData
        )

        tiprackMap = {
            "Barcode": "barcode",
            "Load Date Time": "loadDateTime",
            "Last Load Date Time": "lastLoadDateTime",
            "Carrier Position": "carrierPosition",
            "Stack Position": "stackPosition",
            "Carrier Group Id": "carrierGroupId",
        }

        bufferlargetiprackData = {}
        samplelargetiprackData = {}
        lhpblargetiprackData = {}
        smalltiprackData = {}

        for category in tiprackMap:
            bufferlargetiprackData["Buffer Large Tip Rack " + category] = [
                x[tiprackMap[category]] for x in bufferlargetipracks
            ]
            samplelargetiprackData["Sample Large Tip Rack " + category] = [
                x[tiprackMap[category]] for x in samplelargetipracks
            ]
            lhpblargetiprackData["LhpB Large Tip Rack " + category] = [
                x[tiprackMap[category]] for x in lhpblargetipracks
            ]
            smalltiprackData["Small Tip Rack " + category] = [
                x[tiprackMap[category]] for x in smalltipracks
            ]

        self.DataFrame.loc[:, [col for col in bufferlargetiprackData]] = pd.DataFrame(
            index=self.DataFrame.index, data=bufferlargetiprackData
        )
        self.DataFrame.loc[:, [col for col in samplelargetiprackData]] = pd.DataFrame(
            index=self.DataFrame.index, data=samplelargetiprackData
        )
        self.DataFrame.loc[:, [col for col in lhpblargetiprackData]] = pd.DataFrame(
            index=self.DataFrame.index, data=lhpblargetiprackData
        )
        self.DataFrame.loc[:, [col for col in smalltiprackData]] = pd.DataFrame(
            index=self.DataFrame.index, data=smalltiprackData
        )

        teststripmapMap = {
            "id": "id",
            "Carrier": "carrier",
            "Carrier Position": "carrierPosition",
            "Well": "well",
        }

        teststripmapivdData = {}
        teststripmapldtppmData = {}
        teststripmapldtmmData = {}

        for category in teststripmapMap:
            teststripmapivdData["Test Strip " + category] = [
                x[teststripmapMap[category]] for x in teststripMapIVDs
            ]
            teststripmapldtppmData["Test Strip PPM " + category] = [
                x[teststripmapMap[category]] for x in teststripMapLDTPPMs
            ]
            teststripmapldtmmData["Test Strip MM " + category] = [
                x[teststripmapMap[category]] for x in teststripMapLDTMMs
            ]

        self.DataFrame.loc[:, [col for col in teststripmapivdData]] = pd.DataFrame(
            index=self.DataFrame.index, data=teststripmapivdData
        )
        self.DataFrame.loc[:, [col for col in teststripmapldtppmData]] = pd.DataFrame(
            index=self.DataFrame.index, data=teststripmapldtppmData
        )
        self.DataFrame.loc[:, [col for col in teststripmapldtppmData]] = pd.DataFrame(
            index=self.DataFrame.index, data=teststripmapldtppmData
        )

        crosstalksettingMap = {
            "Green Into Yellow Crosstalk": "greenIntoYellow",
            "Yellow Into Orange Crosstalk": "yellowIntoOrange",
            "Orange Into Red Crosstalk": "orangeIntoRed",
            "Red Into Far Red Crosstalk": "redIntoFarRed",
        }
        crosstalksettingData = {}
        for category in crosstalksettingMap:
            crosstalksettingData[category] = [
                x[crosstalksettingMap[category]] for x in crosstalksettings
            ]
        self.DataFrame.loc[:, [col for col in crosstalksettingMap]] = pd.DataFrame(
            index=self.DataFrame.index, data=crosstalksettingData
        )

        if drop_parent:
            self.DataFrame.drop("chainOfCustodySet", axis=1, inplace=True)

    def unpackAssay(self, drop_parent=True):
        assays = [x for x in self.DataFrame["Assay"]]

        assayMap = {
            "Assay Name": "assayName",
            "Assay Version": "assayVersion",
            "RP Version": "rpVersion",
            "Result Code": "resultCode",
            "Sample Specimen Type": "sampleSpecimenType",
            "Test Specimen Type": "testSpecimenType",
            "Run Type": "runType",
            "Dilution Factor": "dilutionFactor",
            "Primer Probe": "primerProbe",
            "assayChannels": "assayChannels",
        }
        assayData = {}
        for category in assayMap:
            assayData[category] = [x[assayMap[category]] for x in assays]

        self.DataFrame.loc[:, [col for col in assayData]] = pd.DataFrame(
            index=self.DataFrame.index, data=assayData
        )

        assaychannels = self.DataFrame["assayChannels"].to_dict()
        unpackedassaychannels = {}
        for sample in assaychannels:
            sample_assaychannels = assaychannels[sample]
            sample_unpackedassaychannels = {}
            for assaychannel in sample_assaychannels:
                sample_unpackedassaychannels[assaychannel["id"]] = {
                    key: value for key, value in assaychannel.items() if key != "id"
                }

            unpackedassaychannels[sample] = sample_unpackedassaychannels

        unpackedassaychannelsDataFrame = pd.DataFrame.from_dict(
            {
                (i, j): unpackedassaychannels[i][j]
                for i in unpackedassaychannels.keys()
                for j in unpackedassaychannels[i].keys()
            },
            orient="index",
        )

        unpackedassaychannelsDataFrame.index.names = ["id", "Assay Channel Id"]
        unpackedassaychannelsDataFrame.rename(
            {"channel": "Channel", "targetName": "Target Name"}, axis=1, inplace=True
        )
        channelsummarysets = [
            x[0] for x in unpackedassaychannelsDataFrame["channelSummarySets"]
        ]
        channelsummarysetMap = {
            "Localized Result": "localizedResult",
            "Ct": "ct",
            "EPR": "epr",
            "End Point Fluorescence": "endPointFluorescence",
            "Max Peak Height": "maxPeakHeight",
            "Baseline Slope": "baselineSlope",
            "Baseline YIntercept": "baselineYIntercept",
            "Baseline First Cycle": "baselineFirstCycle",
            "Baseline Last Cycle": "baselineLastCycle",
            "Calibration Coefficient": "calibrationCoefficient",
            "Log Conc": "logConc",
            "Conc": "conc",
            "Blank Reading": "blankReading",
            "Dark Reading": "darkReading",
        }

        channelsummarysetData = {}
        for category in channelsummarysetMap:
            channelsummarysetData[category] = [
                x[channelsummarysetMap[category]] for x in channelsummarysets
            ]

        unpackedassaychannelsDataFrame.loc[
            :, [col for col in channelsummarysetData]
        ] = pd.DataFrame(
            index=unpackedassaychannelsDataFrame.index, data=channelsummarysetData
        )
        unpackedassaychannelsDataFrame.drop(
            "channelSummarySets", axis=1, inplace=True)
        self.DataFrame = self.DataFrame.join(unpackedassaychannelsDataFrame)
        self.DataFrame.drop("channelSummarySets", axis=1, inplace=True)

        assaychannelsteps = self.DataFrame["assayChannelSteps"].to_dict()
        unpackedassaychannelsteps = {}
        for sample_channel in assaychannelsteps:
            sample_assaychannelsteps = assaychannelsteps[sample_channel]
            sample_unpackedassaychannelsteps = {}
            for assaychannelstep in sample_assaychannelsteps:
                sample_unpackedassaychannelsteps[assaychannelstep["id"]] = {
                    key: value for key, value in assaychannelstep.items() if key != "id"
                }

            unpackedassaychannelsteps[sample_channel] = sample_unpackedassaychannelsteps

        unpackedassaychannelstepsDataFrame = pd.DataFrame.from_dict(
            {
                (i[0], i[1], j): unpackedassaychannelsteps[i][j]
                for i in unpackedassaychannelsteps.keys()
                for j in unpackedassaychannelsteps[i].keys()
            },
            orient="index",
        )
        unpackedassaychannelstepsDataFrame.rename(
            {"processingStep": "Processing Step"}, axis=1, inplace=True
        )
        unpackedassaychannelstepsDataFrame.drop(
            ["assayChannel", "assayChannelId"], axis=1, inplace=True
        )
        unpackedassaychannelstepsDataFrame.index.names = [
            "id",
            "Assay Channel Id",
            "Assay Channel Step Id",
        ]
        readingSets = [x[0]
                       for x in unpackedassaychannelstepsDataFrame["readingSets"]]
        unpackedreadingsets = []

        for readingSet in readingSets:
            unpackedreadingset = {}
            unpackedreadingset["Reading Set Id"] = readingSet["id"]
            cycles = []
            values = []
            for reading in readingSet["readings"]:
                unpackedreadingset["Reading " + str(reading["cycle"])] = reading[
                    "value"
                ]
                cycles.append(reading["cycle"])
                values.append(reading["value"])
            # unpackedreadingset['Readings Array'] = np.column_stack(
            #     zip(cycles, values))
            unpackedreadingsets.append(unpackedreadingset)

        columns = [x for x in unpackedreadingsets[0].keys()]
        for readingset in unpackedreadingsets:
            for column in [x for x in readingset.keys()]:
                if column not in columns:
                    columns.append(column)

        unpackedassaychannelstepsDataFrame.loc[:, columns] = pd.DataFrame(
            index=unpackedassaychannelstepsDataFrame.index, data=unpackedreadingsets
        )
        unpackedassaychannelstepsDataFrame.drop(
            "readingSets", axis=1, inplace=True)
        self.DataFrame = self.DataFrame.join(
            unpackedassaychannelstepsDataFrame)
        self.DataFrame.drop("readingSets", axis=1, inplace=True)
        self.DataFrame.drop(
            ["Assay", "assayId", "assay", "assayChannels", "assayChannelSteps"],
            axis=1,
            inplace=True,
        )

    def standardDecode(self):
        SampleJSONReader.unpackConsumables(self)
        SampleJSONReader.unpackNeuMoDxSystem(self)
        SampleJSONReader.unpackXPCRModuleLane(self)
        SampleJSONReader.unpackXPCRModuleConfiguration(self)
        SampleJSONReader.unpackHeaterModuleConfiguration(self)
        SampleJSONReader.unpackChainOfCustodySet(self)
        SampleJSONReader.unpackAssay(self)


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


def getSampleDataAsync(sample_ids):
    """
    Used to perform async requests to retreive sample data.
    Parameters
    ----------
    sample_ids (List[guids]):  list of sample ids to get data for.
    """

    async def getSampleData(session, url):
        async with session.get(url) as resp:
            sample = await resp.json()
            return sample

    async def main():
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            tasks = []
            for sample_id in sample_ids:
                url = os.environ["API_HOST"] + "/api/samples/{}/all-info".format(
                    sample_id
                )
                tasks.append(asyncio.ensure_future(
                    getSampleData(session, url)))

            return await asyncio.gather(*tasks)

    samples = asyncio.run(main())
    return samples
