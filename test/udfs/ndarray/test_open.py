# coding=utf-8
# Copyright 2018-2022 EVA
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
from test.util import create_sample_image

import numpy as np
import pandas as pd
import pytest
from mock import patch

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.executor_utils import ExecutorError
from eva.udfs.ndarray.open import Open


@pytest.mark.notparallel
class OpenTests(unittest.TestCase):
    def setUp(self):
        self.open_instance = Open()
        self.config = ConfigurationManager()
        self.image_file_path = create_sample_image()

    def test_open_name_exists(self):
        assert hasattr(self.open_instance, "name")

    def test_should_open_image(self):
        df = self.open_instance(pd.DataFrame([self.image_file_path]))
        actual_img = df["data"].to_numpy()[0]

        expected_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        expected_img[0] -= 1
        expected_img[2] += 1

        self.assertEqual(actual_img.shape, expected_img.shape)
        self.assertEqual(np.sum(actual_img[0]), np.sum(expected_img[0]))
        self.assertEqual(np.sum(actual_img[1]), np.sum(expected_img[1]))
        self.assertEqual(np.sum(actual_img[2]), np.sum(expected_img[2]))

    def test_open_same_path_should_use_cache(self):
        # un-cached open
        with patch("eva.udfs.ndarray.open.cv2") as mock_cv2:
            self.open_instance(pd.DataFrame([self.image_file_path]))
            mock_cv2.imread.assert_called_once_with(self.image_file_path)

        # cached open
        with patch("eva.udfs.ndarray.open.cv2") as mock_cv2:
            self.open_instance(pd.DataFrame([self.image_file_path]))
            mock_cv2.imread.assert_not_called()

    def test_open_path_should_raise_error(self):
        with self.assertRaises(ExecutorError):
            self.open_instance(pd.DataFrame(["incorrect_path"]))