"""The core module provides functions to process the data files.
"""

import pathlib
from datetime import datetime, date, time, timedelta
import numpy as np
import functools


def data_dir():
    # TODO(Gang): Implement it.
    mock_dir = "C:\\Users\\Wang Gang\\projects\\fiberdata"
    return mock_dir

def list_files(line_id, datetime_, len_):
    """list_files can filter the files for the specified filters.

        Example:
        list_files('p0', '2019-07-15 00:00', 5)
        it will filter data files that are from p0, in date 2019-07-15,
        starting at 00 hour 00 minute, and the total (max) count is 5.
    """
    the_dir = pathlib.Path(data_dir())/str(line_id)
    format_spec= "%Y-%m-%d %H:%M"
    dt = datetime.strptime(datetime_, format_spec)
    format_spec2 = "%Y/%m/%d" # For path.
    date_path = dt.strftime(format_spec2)

    format_spec3 = "%Y%m%d%H" # For filename, excluding the minute part for matching all.
    filename_part = dt.strftime(format_spec3)

    leaf_dir = the_dir.joinpath(date_path)
    # sorted helps make sure the files are in ascending order.
    files_in_hour = sorted(leaf_dir.glob("*{}*.bin".format(filename_part)))

    # Filter further to include only the files starting at the minute and the length.
    starting_minute = dt.time().minute
    ending_minute = starting_minute + len_
    ending_dt = dt + timedelta(minutes=len_)
    
    # define a filter function.
    def filter_by_minutes(file_: pathlib.Path):
        parts = file_.name.split('-')
        assert len(parts) == 3
        file_dt_minute = int(parts[1][10:12])  # Only the yyyymmddHHMM length is 12. 
        return file_dt_minute >= starting_minute and file_dt_minute <= ending_minute
 

    result_files = list(filter(filter_by_minutes, files_in_hour))

    return result_files

@functools.lru_cache(maxsize=3)
def load_data(line_id, datetime_, len_, points):
    files = list_files(line_id, datetime_, len_)
    f32 = np.dtype(np.float32)
    matrix_list = []
    for f in files:
        data = np.fromfile(str(f.absolute()), f32)
        shape = (-1, points)

        matrix = data.reshape(shape)
        matrix_list.append(matrix)
    result_data = np.vstack(matrix_list)

    return result_data










