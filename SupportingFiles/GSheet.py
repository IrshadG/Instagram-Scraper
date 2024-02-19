import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
APIKeyFileName = 'gsheet_api.json'

class GSheet:
    def __init__(self):
        self.users = []
        creds = ServiceAccountCredentials.from_json_keyfile_name(APIKeyFileName, scope)
        self.client = gspread.authorize(creds)

    def openSheet(self,sheetName):
        self.sheet = self.client.open(sheetName)
        print(type(self.sheet)) # should be gspread.models.Spreadsheet  
        return self.sheet
        # return sheet

    def getWorksheet(self,sheet,worksheetNumber):
        worksheet = sheet.get_worksheet(worksheetNumber)
        return worksheet

    def get_df(self,sheet,worksheetNumber=0):
        worksheet = sheet.get_worksheet(worksheetNumber)
        records_data = worksheet.get_all_records()
        records_df = pd.DataFrame.from_dict(records_data)
        return records_df

    def get_5kprofiles(self,sheetName,worksheetNumber=0):
        self.sheet = self.client.open(sheetName)
        self.worksheet = self.sheet.get_worksheet(worksheetNumber)
        records_data = self.worksheet.get_all_records()
        records_df = pd.DataFrame.from_dict(records_data)
        five_k_profiles = [x[1:] for x in records_df["Profile"]]
        return five_k_profiles

    def updateValue(self,i,j,value):
        self.worksheet.update(values =[[value]],range_name=str(j)+str(i+2))
    
    def getValue(self,i,j):
        cell_value=self.worksheet.get(str(j)+str(i+2))
        return cell_value[0][0]
