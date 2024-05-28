from dotenv import load_dotenv
import os.path
import pandas as pd

import gspread
from gspread.utils import ValueRenderOption


load_dotenv()


class google_worksheet():
    def __init__(self, spreadsheet_id: str = None, work_sheet_index: int = 0) -> None:
        self.SPREADSHEET_ID = spreadsheet_id

        self._CREDENTIALS = None
        self._client = None
        self._sheet = None

        self._work_sheet_index = work_sheet_index
        self.work_sheet = None
        self.headers = None

        if self.SPREADSHEET_ID:
            self.setup_google_sheet(self.SPREADSHEET_ID)

    def setup_google_sheet(self, spreadsheet_id: str):
        self._CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
        self._client = gspread.oauth(
            credentials_filename=self._CREDENTIALS,
            scopes=gspread.auth.READONLY_SCOPES
        )

        self.SPREADSHEET_ID = spreadsheet_id
        self._sheet = self._client.open_by_key(self.SPREADSHEET_ID)
        self.work_sheet = self._sheet.get_worksheet(self._work_sheet_index)

        headers = self.get_data_by_range(['A1:Z1'])[0]
        self.headers = {element: index+1 for index,
                        element in enumerate(headers)}

    @property
    def row_count(self):
        return len(self.work_sheet.col_values(1))

    @property
    def column_count(self):
        return len(self.work_sheet.row_values(1))

    def get_columns(self):
        headers = self.work_sheet.row_values(1)
        headers_dict = dict.fromkeys(headers, True)

        return headers_dict

    def get_data_by_range(self, range: list, **kwargs):
        major_dimension = kwargs.get('major_dimension')
        if not major_dimension:
            major_dimension = 'ROWS'

        data = self.work_sheet.batch_get(
            range, major_dimension=major_dimension,
            value_render_option=ValueRenderOption.unformatted)

        return data[0]

    def get_range_as_dataframe(self, range: list):
        data = self.get_data_by_range(range)
        df = pd.DataFrame(data, columns=self.headers.keys())
        return df

    def get_headers_elements(self, headers: list, value_render=None):
        if not value_render:
            value_render = ValueRenderOption.unformatted

        elements = {}

        for header in headers:
            col_number = self.headers.get(header)
            if col_number:
                col_data = self.work_sheet.col_values(
                    self.headers[header], value_render_option=value_render)
                col_data.pop(0)
                elements[header] = col_data

        return elements


if __name__ == '__main__':
    sheet = google_worksheet('1AqO1v_tswba4ElDiA-gLboUjGQIfIMYAIqIIBe4I6L0')
    data = sheet.get_range_as_dataframe(['A2:Z9'])
    print(data)
