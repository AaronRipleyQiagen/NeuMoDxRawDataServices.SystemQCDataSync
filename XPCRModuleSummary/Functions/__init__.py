import pandas as pd


def get_dataframe_from_records(records: list[dict], column_map: dict) -> pd.DataFrame:
    """
    A function used to populate a dataframe from records (i.e. as stored in a dcc.Store component).
    Args:
        records: Records to be used to populate DataFrame.
        column_map: Dictionary to be used to map properties of records to columns in DataFrame. Key: Source -> Record property, Value: Target -> DataFrame Column
    Returns:
        DataFrame populated from Records.
    """

    # Initialize the dataframe used to collect information from records
    dataframe = pd.DataFrame(columns=[x for x in column_map])

    # Iterate through the records and add each record as a new row.
    idx = 0
    for record in records:
        dataframe.loc[idx] = record
        idx += 1

    # Rename the columns in dataframe to match the column names defined in the column_map.
    dataframe.rename(column_map, axis=1, inplace=True)

    return dataframe


def get_column_defs(
    dataframe: pd.DataFrame, hide_columns: list[str] = None
) -> list[dict]:
    """
    A function used to get the columnDefs for the DataFrame inputed.
    Args:
      dataframe: DataFrame to get columnDefs for.
      hide_columns: Columns in the DataFrame to hide. Defaults to columns containing "Id" or "id".
    """

    column_definitions = []

    if hide_columns == None:
        hide_columns = [x for x in dataframe.columns if "Id" in x or "id" in x]

    for column in dataframe.columns:
        column_definition = {
            "headerName": column,
            "field": column,
            "filter": True,
            "sortable": True,
        }
        if column in hide_columns:
            column_definition["hide"] = True

        column_definitions.append(column_definition)

    return column_definitions


def clean_date_columns(
    dataframe: pd.DataFrame,
    date_columns: list[str] | None = None,
    date_format: str = "%d %B %Y %H:%M:%S",
) -> pd.DataFrame:
    """
    A function used to convert the columns that can be converted to a datetime64 type to a specfied format.

    Args:
        dataframe: DataFrame used for conversion

    Optional Args:
        date_columns: List of columns to be converted.  Defaults to columns containing "Date" or "date".
        date_format: The strftime format to convert target columns to. Defaults to "%d %B %Y %H:%M:%S" (22 February 2023 18:19:43)


    """
    if date_columns == None:
        date_columns = [x for x in dataframe if "Date" in x or "date" in x]
    for column in date_columns:
        dataframe[column] = (
            dataframe[column].astype("datetime64[ns]").dt.strftime(date_format)
        )

    return dataframe


def get_dash_ag_grid_from_records(
    records: list[dict],
    column_map: dict,
    date_columns: list[str] | None = None,
    date_format: str = "%d %B %Y %H:%M:%S",
    hide_columns: list[str] = None,
) -> tuple[list[dict], list[dict]]:
    """
    A function used to provide a standardized method to populate the rowData and columnDefs of a Dash AG Grid from a list of records

    Args:
        records: Records to be used to populate DataFrame.
        column_map: Dictionary to be used to map properties of records to columns in DataFrame. Key: Source -> Record property, Value: Target -> DataFrame Column

    Optional Args:
        date_columns: List of columns to be converted.  Defaults to columns containing "Date" or "date".
        date_format: The strftime format to convert target columns to. Defaults to "%d %B %Y %H:%M:%S" (22 February 2023 18:19:43)
        hide_columns: Columns in the DataFrame to hide. Defaults to columns containing "Id" or "id".

    Returns:
        A tuple containing two list[dict] (RowData, ColumnDefs)
    """

    dataframe = get_dataframe_from_records(records, column_map)
    dataframe.pipe(
        clean_date_columns, date_columns=date_columns, date_format=date_format
    )
    columnDefs = get_column_defs(dataframe, hide_columns=hide_columns)

    return dataframe.to_dict("records"), columnDefs
