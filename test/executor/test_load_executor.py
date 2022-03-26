# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import pandas as pd

from mock import patch, call
from eva.executor.load_executor import LoadDataExecutor
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType
from test.util import create_sample_csv, file_remove
from eva.expression.tuple_value_expression import TupleValueExpression


class LoadExecutorTest(unittest.TestCase):

    @patch('eva.storage.storage_engine.StorageEngine.create')
    @patch('eva.storage.storage_engine.StorageEngine.write')
    def test_should_call_opencv_reader_and_storage_engine(
            self, write_mock, create_mock):
        batch_frames = [list(range(5))] * 2
        file_path = 'video'
        table_metainfo = 'info'
        batch_mem_size = 3000
        file_options = {}
        file_options['file_format'] = FileFormatType.VIDEO
        column_list = None
        plan = type(
            "LoadDataPlan", (), {
                'table_metainfo': table_metainfo,
                'file_path': file_path,
                'batch_mem_size': batch_mem_size,
                'column_list': column_list,
                'file_options': file_options})

        load_executor = LoadDataExecutor(plan)
        batch = next(load_executor.exec())
        create_mock.assert_called_once_with(table_metainfo)
        write_mock.has_calls(call(table_metainfo, batch_frames[0]), call(
            table_metainfo, batch_frames[1]))
        # Note: We call exec() from the child classes.
        self.assertEqual(batch, Batch(pd.DataFrame(
            [{'Video': file_path, 'Num Loaded Frames': 0}])))

    @patch('eva.storage.storage_engine.StorageEngine.write')
    def test_should_call_csv_reader_and_storage_engine(
            self, write_mock):
        batch_frames = [list(range(5))] * 2

        # creates a dummy.csv
        create_sample_csv()

        file_path = 'dummy.csv'
        table_metainfo = 'info'
        batch_mem_size = 3000
        file_options = {}
        file_options['file_format'] = FileFormatType.CSV
        column_list = [
            TupleValueExpression(col_name='id', table_name='dummy'),
            TupleValueExpression(col_name='frame_id', table_name='dummy'),
            TupleValueExpression(col_name='video_id', table_name='dummy')
        ]
        plan = type(
            "LoadDataPlan", (), {
                'table_metainfo': table_metainfo,
                'file_path': file_path,
                'batch_mem_size': batch_mem_size,
                'column_list': column_list,
                'file_options': file_options})

        load_executor = LoadDataExecutor(plan)
        batch = next(load_executor.exec())
        write_mock.has_calls(call(table_metainfo, batch_frames[0]), call(
            table_metainfo, batch_frames[1]))

        # Note: We call exec() from the child classes.
        self.assertEqual(batch, Batch(pd.DataFrame(
            [{'CSV': file_path, 'Number of loaded frames': 20}])))

        # remove the dummy.csv
        file_remove('dummy.csv')
        

        

