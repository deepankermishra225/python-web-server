class Config:

    def __init__(
            self,
            host,
            port,
            ssl,
            backlog,
            timeout_graceful_shutdown
    ):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.backlog = backlog
        self.timeout_graceful_shutdown = timeout_graceful_shutdown
