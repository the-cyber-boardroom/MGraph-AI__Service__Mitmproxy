from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

# todo: refactor to OSBot_Utils
#       also see is we can improve this validate

class Safe_Str__HTTP__Method(Safe_Str):                               # HTTP method validation
    max_length = 10