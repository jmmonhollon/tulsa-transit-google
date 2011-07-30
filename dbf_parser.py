#!/usr/bin/env python
# encoding: utf-8

import csv
import getopt
import os
import sqlite3
import sys

import dbfpy.dbf

def latlon_transformer(value):
    '''Transforms latitude and longitude values to valid degree decimals'''
    try:
        return float(value) / 1000000
    except:
        return value


def convert_color(value):
    '''Convert integer value into a hex color value'''
    try:
        return '%06x' % value
    except:
        return value


def str_exists_validator(value):
    '''validates thats that a string is not empty'''
    try:
        return isinstance(value, str) and len(value) > 0
    except:
        return False


def latlon_validator(value):
    from numbers import Number
    try:
        return isinstance(value, Number) and value != 0
    except:
        return False


'''
Mapping for DBF input files to database.  Fields are:
- DBF Field Name
- Database column name
- DBF data transformer (optional)
- DBF data validator (optional)
'''
DBF_MAPPING = {
    'stops': {
        'table': 'stops',
        'fields': (
            ('StopId', 'stop_id'),
            ('StopName', 'stop_name', None, str_exists_validator),
            ('lat', 'stop_lat', latlon_transformer, latlon_validator),
            ('lon', 'stop_lon', latlon_transformer, latlon_validator),
            ('SiteName', 'stop_desc'),
            ('StopAbbr', 'stop_code'),
        )},
    'lines': {
        'table': 'routes',
        'fields': (
            ('LineID', 'route_id'),
            ('LineAbbr', 'route_short_name'),
            ('LineName', 'route_long_name'),
            ('', 'route_type', lambda x: 3),
            ('LineColor', 'route_color', convert_color),
        )},
}

def is_useful(full_path):
    '''Check if a file is an MTTA dbf file'''
    return get_key_name(full_path) is not None

def get_key_name(full_path):
    mapping = DBF_MAPPING
    name = os.path.split(full_path)[-1].lower()
    if not '.dbf' in name:
        return None
    name = name.replace('.dbf','')
    if name not in mapping:
        name += 's'
    if name in mapping:
        return name
    else:
        return None

def read(dbf_path, database):
    '''Read an MTTA dbf file into the database'''
    key_name = get_key_name(dbf_path)
    feed = DBF_MAPPING[key_name]
    table_name = feed['table']
    db_f = dbfpy.dbf.Dbf(dbf_path, readOnly=True)
    rows = []
    header = []
    for fh in feed['fields']:
        header.append(fh[1])
    for record in db_f:
        row = []
        invalid_fields = False
        for field in feed['fields']:
            if field[0]:
                field_value = record[field[0]]
            if len(field) >= 3 and callable(field[2]):
                field_value = field[2](field_value)
            if len(field) >= 4 and callable(field[3]):
                if not field[3](field_value):
                    invalid_fields = True
            if isinstance(field_value, str):
                
                row.append(unicode(field_value, encoding='latin-1'))
            else:
                row.append(field_value)
        if not invalid_fields:
            rows.append(row)
    if rows:
        sql = 'INSERT INTO %s (' % table_name
        sql += ', '.join([h for h in header])
        sql += ') VALUES (' + ', '.join(['?' for _ in header]) + ');'
        # Faster but harder to debug
        # database.executemany(sql, rows)
        
        for row in rows:
            database.execute(sql, row)

