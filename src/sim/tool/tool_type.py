class ToolType:
    # common tools
    NONE = 0
    MOVE_TO = 1
    INSPECT = 2
    SPEAK = 3
    REST = 4
    USE = 5
    GIVE = 6
    TAKE = 7
    WEB_SEARCH = 8
    EXPLORE = 9

    # cast away sim specific tools
    BUILD_RAFT = 500

    # nebula tower sim specific tools
    RESURRECT = 600
    RELEASE = 601