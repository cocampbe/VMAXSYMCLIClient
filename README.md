# VMAXSYMCLIClient

This class provides a small number of usueful methods for VMAX arrays.
My primary use has been for taking snapshots of storage groups.

## Getting started

import client

cl = client.symcli_client('sym_id')

cl.get_sgnames # This will return a list of storage group names
cl.get_sg_children('sgname') # This will return a list of child storage groups
cl.get_dict_name_tdevs # Return a dictionary of {device_name: tdev}.
                       # You will need to have added a device_name identifier to the tdev.

### Prerequsites

You will need to have solutions enabler installed. You will also need some gatekeepers.

#### Installing

You can put this module in the same directory as your project.
