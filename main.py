# https://googleapis.dev/python/bigtable/latest/row.html#google.cloud.bigtable.row.ConditionalRow
import datetime, re, os

from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.cloud.bigtable import row_filters
from google.cloud.bigtable.row_set import RowSet

PROJECT_ID=os.environ.get('PROJECT_ID')
INSTANCE_ID=os.environ.get('BT_INSTANCE','bt-instance')
TABLE_ID=os.environ.get('BT_TABLE','bt-table01')

client = bigtable.Client(project=PROJECT_ID, admin=True)
instance = client.instance(INSTANCE_ID)
table = instance.table(TABLE_ID)
column_1 = os.environ.get('BT_COLUM_A','my_column_a').encode()

C_FAMILY = [ os.environ.get('BT_COLUM_FAMILY','bt-familycol1')]
COL_NAMES = ['ROWKEY',column_1]
KEY_ARRAY_1 = ['rowkey#a#1','test1-value-1a']
KEY_ARRAY_2 = ['rowkey#a#2','test2-value-1a']
KEY_ARRAY_3 = ['rowkey#b#1','test1-value-1a']
LIMIT_GET = 3
max_versions_rule = column_family.MaxVersionsGCRule(2)

def crate_table():
    print('Creating the {} table.'.format(TABLE_ID))
    print('Creating column family cf1 with Max Version GC rule...')
    # Create a column family with GC policy : most recent N versions
    # Define the GC policy to retain only the most recent 2 versions
    column_families = {C_FAMILY[0]: max_versions_rule}
    if not table.exists():
        table.create(column_families=column_families)
    else:
        print("Table {} already exists.".format(TABLE_ID))


def cell_insert(key_array):
    row_key = key_array[0]
    row_obj = table.row(row_key)
    row_obj.set_cell(C_FAMILY[0], COL_NAMES[1], key_array[1].encode(), timestamp=datetime.datetime.strptime('00', '%y').replace(year=1970))
    resp = row_obj.commit()
    return resp


def cell_delete(key_array):
    row_key = key_array[0]
    row_obj = table.row(row_key)
    row_obj.delete_cell(C_FAMILY[0], COL_NAMES[1])
    resp = row_obj.commit()
    return resp


def row_delete(key_array):
    row_key = key_array[0]
    row_obj = table.row(row_key)
    row_obj.delete()
    resp = row_obj.commit()
    return resp


def rows_delete(prefix, sufix='', limit=2):
    row_filter = row_filters.RowKeyRegexFilter(f'{prefix}.*$'.encode("utf-8"))
    row_set = RowSet()
    row_set.add_row_range_from_keys(prefix.encode("utf-8"))

    #rows = table.read_rows(filter_=row_filter)
    rows = table.read_rows(row_set=row_set, filter_=row_filter)
    rows.delete()
    resp = rows.commit()
    return resp


def row_insert(key_array):
    row_key = key_array[0]
    rows = []
    row = table.direct_row(row_key=row_key)
    col_name = COL_NAMES[1]
    # set cfclient
    colum_family = C_FAMILY[0]

    row.set_cell(
        colum_family
        ,col_name.encode()
        ,key_array[1].encode()
        ,timestamp=datetime.datetime.strptime('00', '%y').replace(year=1970)
        )
    rows.append(row)

    response = table.mutate_rows(rows)
        
    return response


def read_row(row_key):
    row_filter = row_filters.CellsColumnLimitFilter(LIMIT_GET)
    
    key = row_key.encode()

    row = table.read_row(key, filter_=row_filter)
    if row:
        cells = row.cells
        cell_data = cells[C_FAMILY[0]] if C_FAMILY[0] in cells else None
        print(f'--cell_data--: {cell_data}')
    return row


def read_rows(prefix='', sufix='', limit=2):
    # https://googleapis.dev/python/bigtable/latest/row-filters.html#google.cloud.bigtable.row_filters.RowFilter
    # https://cloud.google.com/bigtable/docs/reading-data
    row_filter = row_filters.CellsColumnLimitFilter(limit)
    row_set = RowSet()
    if prefix and not sufix:
        row_set.add_row_range_from_keys(start_key=prefix.encode("utf-8"))
        row_filter = row_filters.RowKeyRegexFilter(f'^{prefix}.*$'.encode("utf-8"))
    elif sufix and not prefix:
        row_set.add_row_range_from_keys(end_key=sufix.encode("utf-8"))
        row_filter = row_filters.RowKeyRegexFilter(f'^.*{sufix}$'.encode("utf-8"))
    elif sufix and prefix:
        row_set.add_row_range_from_keys(start_key=prefix.encode("utf-8"))
        row_filter = row_filters.RowKeyRegexFilter(f'^{prefix}.*{sufix}$'.encode("utf-8"))

    #rows = table.read_rows(filter_=row_filter)
    rows = table.read_rows(row_set=row_set)
    #rows = table.read_rows(row_set=row_set, filter_=row_filter)
    count = 0
    for row in rows:
        count = count + 1
        cells = row.cells
        cell_data = cells[C_FAMILY[0]] if C_FAMILY[0] in cells else None
        print(f'->>({count}) -- {row.row_key} -- {cell_data}')
        print(f'_________________')
    
    return rows


def cells_delete_by_time(key_array):
    row_key = key_array[0]
    row = table.row(row_key=row_key)
    row.delete_cells(C_FAMILY[0], row.ALL_COLUMNS,
                 time_range=time_range)
    row.delete()


def delete_table():
    print('Deleting the {} table.'.format(TABLE_ID))
    table.delete()


#crate_table()
#row_insert(KEY_ARRAY_1)
#row_delete(KEY_ARRAY_1)
#rows_delete(prefix="2", limit=1)
#cell_insert(KEY_ARRAY_1)
read_rows(prefix='rowkey#', limit=100)
#cell_delete(KEY_ARRAY_1)
#read_row("rowkey#a#1")
#delete_table(KEY_ARRAY_1)