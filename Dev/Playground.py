

import numpy as np

filtered_list = ["NIO","AAPL","MSFT"]
print(filtered_list)
np.savetxt("file_name.csv", filtered_list, delimiter=",", fmt="%s")