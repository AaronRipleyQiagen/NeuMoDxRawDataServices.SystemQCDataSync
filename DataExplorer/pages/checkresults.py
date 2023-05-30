from dash import (
    html,
    callback,
    Output,
    Input,
    State,
    register_page,
    dcc,
    dash_table,
    ctx,
    no_update,
)
import dash_bootstrap_components as dbc
import aiohttp
import asyncio
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import requests
from flask import session
from flask_mail import Message
import dash_ag_grid as dag

fig = go.Figure()

colorDict = {
    1: "#FF0000",  # Red 1
    2: "#00B050",  # Green 2
    3: "#0070C0",  # Blue 3
    4: "#7030A0",  # Purple 4
    5: "#808080",  # Light Grey 5
    6: "#FF6600",  # Orange 6
    7: "#FFCC00",  # Yellow 7
    8: "#9999FF",  # Light Purple 8
    9: "#333333",  # Black 9
    10: "#808000",  # Goldish 10
    11: "#FF99CC",  # Hot Pink 11
    12: "#003300",  # Dark Green 12
}

register_page(__name__, path="/results/")


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
            pd.read_json(json_data).rename(self.column_mapper, axis=1).set_index("id")
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
            self.DataFrame.drop("xpcrModuleConfiguration", axis=1, inplace=True)

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
            self.DataFrame.drop("heaterModuleConfiguration", axis=1, inplace=True)

    def unpackChainOfCustodySet(self, drop_parent=True):
        chainofcustodysets = [x for x in self.DataFrame["chainOfCustodySet"].values]
        sampledefinitions = [x["sampleDefinition"] for x in chainofcustodysets]
        operators = [x["operator"] for x in sampledefinitions]
        lhpatraces = [x["lhpATrace"] for x in chainofcustodysets]
        bufferlargetipracks = [x["bufferLargeTipRack"] for x in lhpatraces]
        samplelargetipracks = [x["sampleLargeTipRack"] for x in lhpatraces]
        lysisbindingtraces = [x["lysisBindingTrace"] for x in chainofcustodysets]
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
            operatorData[category] = [x[operatorMap[category]] for x in operators]
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
            lhpatraceData[category] = [x[lhpatraceMap[category]] for x in lhpatraces]
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
            lhpbtraceData[category] = [x[lhpbtraceMap[category]] for x in lhpbtraces]
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
            lhpctraceData[category] = [x[lhpctraceMap[category]] for x in lhpctraces]
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
            pcrtraceData[category] = [x[pcrtraceMap[category]] for x in pcrtraces]
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
        unpackedassaychannelsDataFrame.drop("channelSummarySets", axis=1, inplace=True)
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
        readingSets = [x[0] for x in unpackedassaychannelstepsDataFrame["readingSets"]]
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
        unpackedassaychannelstepsDataFrame.drop("readingSets", axis=1, inplace=True)
        self.DataFrame = self.DataFrame.join(unpackedassaychannelstepsDataFrame)
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
                tasks.append(asyncio.ensure_future(getSampleData(session, url)))

            return await asyncio.gather(*tasks)

    samples = asyncio.run(main())
    return samples


"""
Layout Components
"""
created_runset_id = dcc.Store(id="created-runset-id", storage_type="session")
sample_results_table = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="sample-results-table",
)
reviewgroup_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Runset Review Assignemnts")),
        dbc.ModalBody(
            children=[
                html.Label("Select Groups required to review this runset."),
                dbc.Checklist(id="review-group-options", switch=True),
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit",
                    id="submit-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
                dbc.Button(
                    "Cancel",
                    id="cancel-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
            ]
        ),
    ],
    id="reviewgroup-selector-modal",
    is_open=False,
)
post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Run Review Creation Result")),
        dbc.ModalBody("Run Review was successfully created"),
    ],
    id="post-response",
    is_open=False,
)
runset_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Run Type Selector")),
        dbc.ModalBody("Please Make A Run Type Selection"),
        dcc.Dropdown(id="runset-type-options"),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit", id="submit-button", className="ms-auto", n_clicks=0
                ),
                dbc.Button(
                    "Cancel", id="cancel-button", className="ms-auto", n_clicks=0
                ),
            ]
        ),
    ],
    id="runset-selector-modal",
    is_open=False,
)
channel_selector = dcc.Dropdown(
    ["Yellow", "Green", "Orange", "Red", "Far Red"],
    value="Yellow",
    id="channel-selector",
)
process_step_selector = dcc.Dropdown(
    ["Normalized", "Raw", "2nd"], value="Raw", id="process-step-selector"
)
create_run_review_button = dbc.Button(
    "Create Run Review from Dataset", id="create-run-review-button"
)
run_review_confirmation = html.H1(id="run-review-confirmation")
fig = dcc.Graph(id="curves", figure=fig)
layout = html.Div(
    children=[
        created_runset_id,
        html.H1(id="h1_1", children="Results Viewer"),
        dcc.Loading(
            id="samples-loading",
            type="graph",
            fullscreen=True,
            children=[
                channel_selector,
                process_step_selector,
                fig,
                sample_results_table,
                create_run_review_button,
                run_review_confirmation,
            ],
        ),
        dcc.Loading(
            id="pending-post",
            type="cube",
            fullscreen="true",
            children=[reviewgroup_selector_modal, post_response, runset_selector_modal],
        ),
    ]
)


@callback(
    [
        Output("channel-selector", "value"),
        Output("process-step-selector", "value"),
        Output("sample-info", "data"),
        Output("runset-type-options", "options"),
    ],
    [Input("url", "href"), State("selected-cartridge-sample-ids", "data")],
)
def get_sample_ids_from_dcc_store(href, selected_cartridge_sample_ids):
    print("Getting Data from DCC Store")
    selected_sample_ids = []
    sample_id_container = []
    for cartridge_id in selected_cartridge_sample_ids:
        for sample_id in selected_cartridge_sample_ids[cartridge_id]:
            selected_sample_ids.append(sample_id)
    sample_data = getSampleDataAsync(selected_sample_ids)

    # the json file where the output must be stored
    # out_file = open("myfile.json", "w")

    # json.dump(sample_data, out_file)
    jsonReader = SampleJSONReader(json.dumps(sample_data))
    jsonReader.standardDecode()
    dataframe = jsonReader.DataFrame
    # dataframe.to_csv('test3.csv')
    dataframe["RawDataDatabaseId"] = dataframe.reset_index()["id"].values
    dataframe["Channel"] = dataframe["Channel"].replace("Far_Red", "Far Red")

    # dataframe = dataframe.reset_index().set_index(['Channel', 'Processing Step', 'XPCR Module Serial'])

    if dataframe["Result Code"][0] in ["QUAL", "HCV", "CTNG"]:
        SPC2_channel = "Yellow"
    else:
        SPC2_channel = "Red"

    """
    Get Run Set Type Options based on Result Codes contained in DataFrame
    """

    runsettypeoptions = {}
    for resultcode in dataframe["Result Code"].unique():
        request_url = os.environ[
            "RUN_REVIEW_API_BASE"
        ] + "QualificationAssays/{}".format(resultcode)
        print(request_url)
        try:
            resp = requests.get(request_url, verify=False).json()

            for runsettype in resp["runSetTypes"]:
                runsettypeoptions[runsettype["id"]] = runsettype["description"]
        except:
            pass

    return (
        SPC2_channel,
        "Normalized",
        dataframe.to_dict(orient="records"),
        runsettypeoptions,
    )


@callback(
    [
        Output("curves", "figure"),
        Output("sample-results-table", "rowData"),
        Output("sample-results-table", "columnDefs"),
    ],
    [
        Input("channel-selector", "value"),
        Input("process-step-selector", "value"),
        Input("sample-info", "data"),
    ],
    prevent_initial_call=True,
)
def update_pcr_curves(channel, process_step, data):
    dataframe = pd.DataFrame.from_dict(data)
    dataframe["Channel"] = dataframe["Channel"].replace("Far_Red", "Far Red")
    # Start making graph...
    fig = go.Figure()
    df = dataframe.reset_index().set_index(
        ["Channel", "Processing Step", "XPCR Module Serial"]
    )
    try:
        df_Channel = df.loc[channel]
    except KeyError:
        channel = df.index.unique(0)[0]
        df_Channel = df.loc[channel]

    df_Channel_Step = df_Channel.loc[process_step].reset_index()
    df_Channel_Step.sort_values("XPCR Module Lane", inplace=True)

    readings_columns = df_Channel_Step[
        [
            x
            for x in df_Channel_Step.columns
            if "Reading " in x
            and "Blank" not in x
            and "Dark" not in x
            and "Id" not in x
        ]
    ]
    cycles = np.arange(1, len(readings_columns.columns) + 1)
    df_Channel_Step["Readings Array"] = [
        np.column_stack(zip(cycles, x)) for x in readings_columns.values
    ]

    for idx in df_Channel_Step.index:
        X = np.array([read for read in df_Channel_Step.loc[idx, "Readings Array"]][0])
        Y = np.array([read for read in df_Channel_Step.loc[idx, "Readings Array"]][1])
        _name = str(df_Channel_Step.loc[idx, "XPCR Module Lane"])
        fig.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=_name,
                line=dict(
                    color=colorDict[df_Channel_Step.loc[idx, "XPCR Module Lane"]]
                ),
            )
        )
    output_frame = df_Channel_Step  # .to_dict('records'

    inital_selection = [
        "XPCR Module Serial",
        "XPCR Module Lane",
        "Sample ID",
        "Target Name",
        "Localized Result",
        "Overall Result",
        "Ct",
        "End Point Fluorescence",
        "Max Peak Height",
        "EPR",
    ]
    column_definitions = []
    aggregates = ["Ct", "EPR", "End Point Fluorescence", "Max Peak Height"] + [
        x for x in output_frame.columns if "Baseline" in x or "Reading" in x
    ]
    groupables = ["XPCR Module Serial"] + [
        x for x in output_frame.columns if "Lot" in x or "Serial" in x or "Barcode" in x
    ]
    floats = ["Ct", "EPR"]
    ints = ["End Point Fluorescence", "Max Peak Height"]
    for column in output_frame.columns:
        column_definition = {"headerName": column, "field": column, "filter": True}
        if column not in inital_selection:
            column_definition["hide"] = True
        if column in aggregates:
            column_definition["enableValue"] = True
        if column in groupables:
            column_definition["enableRowGroup"] = True
        # if column in ints:
        #     column_definition['valueFormatter'] = {
        #         "function": "'$' + (params.value)"}
        column_definitions.append(column_definition)
    return fig, output_frame.to_dict("records"), column_definitions


@callback(
    Output("runset-selector-modal", "is_open"),
    [
        Input("create-run-review-button", "n_clicks"),
        Input("submit-button", "n_clicks"),
        Input("cancel-button", "n_clicks"),
    ],
    [State("runset-selector-modal", "is_open")],
    prevent_initial_call=True,
)
def switch_runset_selector(create_clicks, submit_clicks, cancel_clicks, is_open):
    if create_clicks or cancel_clicks or submit_clicks:
        return not is_open

    return is_open


@callback(
    Output("reviewgroup-selector-modal", "is_open"),
    Input("review-group-options", "options"),
    Input("submit-reviewgroup-selection-button", "n_clicks"),
    Input("cancel-reviewgroup-selection-button", "n_clicks"),
    State("reviewgroup-selector-modal", "is_open"),
    prevent_initial_call=True,
)
def switch_runset_selector(
    options, submit_button, cancel_button, reviewgroup_selector_modal_is_open
):
    # if (ctx.triggered_id == 'review-group-options' and len(options) > 0):
    return not reviewgroup_selector_modal_is_open
    # return reviewgroup_selector_modal_is_open
