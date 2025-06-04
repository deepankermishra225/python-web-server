class Config:

    def __init__(
            self,
            host,
            port,
            ssl,
            backlog,
            timeout_graceful_shutdown,
            root_path,
            asgi_version,
            limit_concurrency
    ):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.backlog = backlog
        self.timeout_graceful_shutdown = timeout_graceful_shutdown
        self.root_path=root_path
        self.asgi_version = asgi_version
        self.limit_concurency = limit_concurrency
