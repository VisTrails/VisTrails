from __future__ import division, print_function

import re
import pandas as pd
import os
import types
from sqlalchemy import MetaData, Table, select, text
import sqlalchemy

from vistrails.core.modules.vistrails_module import ModuleError, Module
from vistrails.core.modules.config import ModuleSettings, IPort, OPort

__author__ = "Matthew Dirks"
__email__ = "matt@skylogic.ca"

UNIT = 1./2

SHAPE_DF = [
	(1,1),

	(0,1),
	(0,0),
	(1,0),
	(1,2),

	(0,2),
	(0,1),
	(2,1),

	(2,2),
	(1,2),
	(1,1),

	(2,1),
	(2,0),
	(1,0),
]
SHAPE_DF = [(x[0]*UNIT, x[1]*UNIT) for x in SHAPE_DF]

class DataFrame(Module):
	""" Allows a Pandas DataFrame to be used as input/output ports in VisTrails. """
	_settings = ModuleSettings(abstract=True)

	def __init__(self):
		pass

	@staticmethod
	def validate(x):
		return isinstance(x, pd.DataFrame)

class DataFrameToClipboard(Module):
	""" Places the contents of the input DataFrame in to the clipboard (for pasting into other applications). """
	_settings = ModuleSettings(abstract=False)

	_input_ports = [IPort(name="df", signature="org.vistrails.vistrails.pandas:DataFrame", shape=SHAPE_DF),]
	_output_ports = []

	def __init__(self):
		Module.__init__(self)

	def compute(self):
		df = self.get_input("df")
		if (df is not None):
			df.to_clipboard()
		else:
			raise ModuleError(self, 'DataFrame = None')

class DataFrameToCSV(Module):
	""" Writes input DataFrame to a CSV file at the given path (output_path). """
	_settings = ModuleSettings(abstract=False)

	_input_ports = [
		IPort(name='df', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF),
		IPort(name='output_path', signature='basic:OutputPath'), # basic:File is only for files that already exist
		IPort(name='overwrite_if_exists', signature='basic:Boolean'),
	]
	_output_ports = []

	def __init__(self):
		Module.__init__(self)

	def compute(self):
		pathOb = self.get_input('output_path')
		path = pathOb.name

		overwrite = self.get_input('overwrite_if_exists')

		if (os.path.exists(path) and not overwrite):
			raise ModuleError(self, 'Output path already exists, and user has required that files not be overwritten, aborting CSV export.')
		else:
			df = self.get_input('df')
			if (df is not None):
				df.to_csv(path)
				print('DataFrameToCSV: wrote CSV')
			else:
				raise ModuleError(self, 'No data found. DataFrame = None')

class LoadFile(Module):
	""" Loads file from disk as a Pandas DataFrame. inputFile extension can be pickle (.pkl), excel (.xlsx), csv, hdf, or json. """

	_settings = ModuleSettings(abstract=False)

	_input_ports = [
		# Note: basic:File is only for files that already exist (which it should in this case)
		IPort(name='inputFile', signature='basic:File', 
			docstring='A file that pandas library can process as a DataFrame (pkl, xlsx, csv, hdf, or json)'),
	]
	_output_ports = [
		OPort(name='df', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF,
			docstring='A pandas DataFrame'),
	]

	def compute(self):
		fpath = self.get_input('inputFile').name

		ext = os.path.splitext(fpath)[1]
		if (ext == '.pkl'):
			df = pd.read_pickle(fpath)
		elif (ext == '.xlsx'):
			df = pd.read_excel(fpath)
		elif (ext == '.csv'):
			df = pd.read_csv(fpath)
		elif (ext == '.hdf'):
			df = pd.read_hdf(fpath)
		elif (ext == '.json'):
			df = pd.read_json(fpath)
		else:
			raise ValueError(Fore.RED+'Filename extension not recognized (%s); expecting pkl, xlsx, csv, hdf, or json.' % fpath +Fore.RESET)

		self.set_output('df', df)

class DataFrameToVistrailsTable(Module):
	""" Converts a Pandas DataFrame to view in VisTrails Spreadsheet. """

	_settings = ModuleSettings(abstract=False)

	_input_ports = [
		IPort(name='df', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF)
	]
	_output_ports = [
		OPort(name='table', signature='org.vistrails.vistrails.tabledata:Table'),
	]

	def compute(self):
		df = self.get_input('df')

		n, d = df.shape

		def get_column(self, colIdx):
			return self.df[self.df.columns[colIdx]].tolist()

		# create an instance of made-up class, which will imitate the behavior of the real TableData
		# just enough to get the required functionality to work
		out = type("TableDataImitator", (object,), {})
		out.columns = d
		out.rows = n
		out.df = df
		out.get_column = types.MethodType(get_column, out)
		out.names = df.columns.tolist()

		self.set_output('table', out)

class FilterNulls(Module):
	""" Filters a Pandas DataFrame to either keep or discard rows that are NaN, empty, None, or Null. """

	_settings = ModuleSettings(abstract=False)

	_input_ports = [
		IPort(name='df', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF, docstring='DataFrame to filter.'),
		IPort(name='columnName', signature='basic:String', docstring='Name of column in DataFrame (df) to perform filtering on.'),
		IPort(name='discard', signature='basic:Boolean', default=True, docstring='If checked, will discard null (empty) rows. If not checked, will keep only the empty rows.')
	]
	_output_ports = [
		OPort(name='df_filtered', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF)
	]

	def compute(self):
		df = self.get_input('df')
		columnName = self.get_input('columnName')
		discard = self.get_input('discard')

		if (columnName not in df):
			raise ValueError('DataFrame does not have specified column (%s). Valid column names are: %s.' % (columnName, ','.join(['"%s"' % col for col in df.columns])))

		mask = df[columnName].isnull()

		if (discard):
			mask = ~mask

		df_filtered = df[mask]
		self.set_output('df_filtered', df_filtered)

class FilterByValue(Module):
	""" Filters a Pandas DataFrame to either keep or discard rows that match the input value. """

	_settings = ModuleSettings(abstract=False)

	_input_ports = [
		IPort(name='df', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF, docstring='DataFrame to filter.'),
		IPort(name='columnName', signature='basic:String', docstring='Name of column in DataFrame (df) to perform filtering on.'),
		IPort(name='value', signature='basic:Variant', docstring='All rows of DataFrame (df) in column (columnName) will be compared to this value.'),
		IPort(name='discard', signature='basic:Boolean', default=False, docstring='If checked, will discard the rows that match, otherwise will keep only the matching rows.')
	]
	_output_ports = [
		OPort(name='df_filtered', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF)
	]

	def compute(self):
		df = self.get_input('df')
		columnName = self.get_input('columnName')
		value = self.get_input('value')
		discard = self.get_input('discard')

		if (columnName not in df):
			raise ValueError('DataFrame does not have specified column (%s). Valid column names are: %s.' % (columnName, ','.join(['"%s"' % col for col in df.columns])))

		# cast value into the same data type as the DataFrame column
		try:
			value = df[columnName].dtype.type(value)
		except:
			# failed to cast dtype
			try:
				# attempt to match by equality, even though dtype cast failed, just to see if it works
				mask = df[columnName]==value
			except:
				raise Exception('Failed to cast value as ' + str(df[columnName].dtype) + '. Check that columnName and value are correct.')

		if (isinstance(value, str)):
			mask = df[columnName].str.match(value, as_indexer=True)
		else:
			mask = df[columnName]==value

		if (discard):
			mask = ~mask

		df_filtered = df[mask]
		self.set_output('df_filtered', df_filtered)

class ReadSqlQuery(Module):
	""" Runs a SQL query on database (given by sql:DBConnection) and returns the result in a pandas DataFrame. """
	_settings = ModuleSettings(abstract=False)

	_input_ports = [
		IPort(name='sqlStatement', signature='basic:String'),
		IPort(name='connection', signature='sql:DBConnection'),
	]
	_output_ports = [
		OPort(name='df', signature='org.vistrails.vistrails.pandas:DataFrame', shape=SHAPE_DF),
	]

	def compute(self):
		sqlStatement = self.get_input('sqlStatement')
		connection = self.get_input('connection')

		engine = connection.engine
		metadata = MetaData(bind=connection)

		df = pd.read_sql_query(sqlStatement, engine)

		self.set_output('df', df)

_modules = [DataFrame, DataFrameToClipboard, DataFrameToCSV, LoadFile, DataFrameToVistrailsTable, FilterNulls, FilterByValue, ReadSqlQuery]
