class ToolType:
    # common tools
    NONE = 0
    MOVE_TO = 1
    INSPECT = 2
    USE = 3
    SPEAK = 4
    TAKE = 5
    GIVE = 6
    REST = 7
    WEB_SEARCH = 8
    RULE_MAKE = 9

    # cast away sim specific tools
    EXPLORE = 500
    BUILD_RAFT = 501
    LIGHT_SIGNAL = 502