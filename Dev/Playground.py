

import numpy as np
from cookies import *


option_info = get_option_chain_barchart(ticker = "AAPL", expi ='2021-01-22', Type = "weekly")

print(option_info)

# =============================================================================
# weekly_expiratons =option_info["meta"]["expirations"]["weekly"] 
# monthly_expiratons =option_info["meta"]["expirations"]["monthly"]
# print(weekly_expiratons)
# print(monthly_expiratons)
# print(type(option_info))
# option_info_raw = list()
# for i in option_info["data"]["Put"]:
#     option_info_raw.append(i["raw"])
# #print(option_info_raw)
# =============================================================================
