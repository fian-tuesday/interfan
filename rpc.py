import os


def remote(fun):
    """ Mock decorator to be reloaded. """
    return fun


INTERFAN_RPC_SIDE = os.getenv('INTERFAN_RPC_SIDE')
print(INTERFAN_RPC_SIDE)
if INTERFAN_RPC_SIDE == 'client':
    from rpc_client import *
else:
    print('RPC module imported without environment variable INTERFAN_RPC_SIDE.')
