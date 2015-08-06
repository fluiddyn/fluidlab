
import unittest

import os
import shutil
from glob import glob

from fluiddyn.io import stdout_redirected

from fluidlab.exp.session import Session


class SimpleTestCase(unittest.TestCase):
    # def setUp(self):
    #     pass

    def test_saveindir(self):

        with stdout_redirected():
            session = Session(name='test', save_in_dir=True)

        # clean-up
        shutil.rmtree(session.path)

    def test_savehere(self):
        with stdout_redirected():
            session = Session(name='test', save_in_dir=False)

        # clean-up
        paths = glob(os.path.join(session.path, session.name) + '_*')
        for path in paths:
            os.remove(path)

if __name__ == '__main__':
    unittest.main(exit=False)
