debug_mode = True


class Logger:

    @staticmethod
    def log(msg, value=None):
        if value is None:
            print(f"{msg}\n")
        else:
            print(f"{msg}\n {value}\n")

    @staticmethod
    def log_debug(msg, value=None):
        if debug_mode:
            if value is None:
                print(f"[DEBUG] {msg}\n")
            else:
                print(f"[DEBUG] {msg}\n {value}\n")
