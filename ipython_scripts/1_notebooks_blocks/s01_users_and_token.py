# %% [markdown]
# ## Building Blocks: Getting tokens to your users
# To interact in Ocean Protocol, you will need a wallet and you will fund it with some
# Token to access the assets in the network.
#
# In this notebook, we will work with a class which represents a
# User of Ocean Protocol.
#
# To use Ocean, a User requires
# - A wallet address
# - A password
#
# With this information, the Ocean instance can be instantiated with the Ocean.main_account attribute.
# This attribute enables the User to unlock event calls in the networks.
# This class will be used in later scripts to simulate behaviour of actors on the network.
# See the /script_fixtures directory for utilities such as the User() class

# %% [markdown]
# ### Section 0: Import modules, and setup logging
#%%
# Standard imports
import random
import os
import names
import logging
from pathlib import Path
import csv
# Import mantaray and the Ocean API (squid)
# mantaray_utilities is an extra helper library to simulate interactions with the Ocean API.
import squid_py
from squid_py.ocean.ocean import Ocean

import mantaray_utilities.config as manta_config
import mantaray_utilities.logging as manta_logging
import mantaray_utilities.user as manta_user
logging.info("Squid API version: {}".format(squid_py.__version__))

# Setup logging to a higher level and not flood the console with debug messages
manta_logging.logger.setLevel('INFO')


#%%
# Get the configuration file path for this environment
# You can specify your own configuration file at any time, and pass it to the Ocean class.
# os.environ['USE_K8S_CLUSTER'] = 'true'
logging.info("Deployment type: {}".format(manta_config.get_deployment_type()))
CONFIG_INI_PATH = manta_config.get_config_file_path()
logging.info("Configuration file selected: {}".format(CONFIG_INI_PATH))

#%% Get passwords from file

class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)
    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

PASSWORD_FILE = manta_config.get_project_path() / 'passwords.csv'
PASSWORD_MAP = CaseInsensitiveDict() # New dict
with open(PASSWORD_FILE, mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        PASSWORD_MAP[row[0]] = row[1]

# %% [markdown]
# ## Section 1: Instantiate the Ocean Protocol interface
#%%
ocn = Ocean(CONFIG_INI_PATH)
logging.info("Ocean smart contract node connected ".format())

#%%
# List the accounts created in Ganache
# ocn.accounts is a {address: Account} dict
print(len(ocn.accounts), "ocean accounts available with following addresses:")
for address in ocn.accounts:
    acct = ocn.accounts[address]
    print(acct.address)

# %% [markdown]
# From accounts, to Users
#
# A simple wrapper for each address is used to represent a user
# See: ./script_fixtures/user.py

#%% [markdown]
# Users are instantiated and listed
#
# Selected accounts are unlocked via password.
# A password.csv file should be located in the project root directory, with each row containing <address>,<password>
#%%
# Create some simulated users of Ocean Protocol
# Alternate between Data Scientists (Consumers)
# and Data Owners (providers)
users = list()
num_users = 4
address_list = [acct for acct in ocn.accounts]
for i, acct_address in enumerate(address_list[0:num_users]):
    if i%2 == 0: role = 'Data Scientist'
    else: role = 'Data Owner'
    if acct_address.lower() in list(PASSWORD_MAP.keys()):
        this_password = PASSWORD_MAP[acct_address]
    else:
        this_password = None

    user = manta_user.User(names.get_full_name(), role, acct_address, this_password, CONFIG_INI_PATH)

    users.append(user)

# Select only unlocked accounts
unlocked_users = [u for u in users if u.credentials]
logging.info("Selected {} unlocked accounts for simulation.".format(len(unlocked_users)))

#%%
# (Optional)
# Delete the configuration files in the /user_configurations folder
for f in Path('.').glob('user_configurations/*.ini'):
    f.unlink()

#%% [markdown]
# List the users
#%%
for u in unlocked_users: print(u)

#%% [markdown]
# Get these users some Ocean token
#%%
for usr in unlocked_users:
    if usr.account.ocean_balance == 0:
        rcpt = usr.account.request_tokens(random.randint(0, 100))
        usr.ocn._web3.eth.waitForTransactionReceipt(rcpt)

#%% [markdown]
# List the users, and notice the updated balance
#%%
for u in unlocked_users: print(u)