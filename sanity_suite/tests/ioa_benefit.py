from sanity_suite.conf_tcs.config import *
from sanity_suite.lib_tcs.utils import *
from sanity_suite.tests.ioa_endpoints import *

uuids = [
         "9499602801_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9569634997_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9637573374_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9688823184_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9713651976_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9718113104_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9735476350_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9791267212_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9833571161_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9889680994_6000C2960dc48023d865148fe29fd46f_Win_2012",
         "9918085134_6000C2960dc48023d865148fe29fd46f_Win_2012"
         ]

level  = 0

class IOATest(unittest.TestCase):

    def test_01_ioa_benefit(self):
        data = submit_ioa_request(GET_VMDK_BENEFITS_URL, uuids, values={'level': level})
        for d in data:
            assert(d["status"] == 0)
            assert(d["data"] is not None)
        print (data)
