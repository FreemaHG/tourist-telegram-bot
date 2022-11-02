class HistoryData:
    """ Для сохранения данных по истории запроса """
    def __init__(self, command, request_time):
        self.command = command
        self.request_time = request_time
