class ToolType:
    # common tools
    NONE = 0
    MOVE_TO = 1
    INSPECT = 2
    SPEAK = 3
    REST = 4
    WEB_SEARCH = 5
    CUSTOM_RULE_TOOL = 6

    # cast away sim specific tools
    EXPLORE = 500