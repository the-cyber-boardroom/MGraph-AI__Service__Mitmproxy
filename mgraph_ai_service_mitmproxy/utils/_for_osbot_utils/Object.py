from typing                                         import Dict
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str
from osbot_utils.utils.Objects                      import obj


def obj__dict(data : Dict):
    safe_data = { str(Safe_Str(k)): v for k, v in data.items()}        # we should add this behaviour to the normal obj() since we should always return a key that is valid python variable
    return obj(safe_data)