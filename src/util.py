from asyncio import Transport

def get_local_addr(transport: Transport) -> tuple[int, int] | None:
    socket_info = transport.get_extra_info('socket')
    if socket_info is not None:
        info = socket_info.get_sockname()   # (ip_address_str, port_int)
        return (str(info[0])), int(info[1]) if isinstance(info, tuple) and len(info) == 2 else None
    info = transport.get_extra_info('sockname')
    if info is not None:
        return (str(info[0])), int(info[1]) if isinstance(info, tuple) and len(info) == 2 else None
    return None


def get_remote_addr(transport: Transport) -> tuple[str, int] | None:
    socket_info = transport.get_extra_info("socket")
    if socket_info is not None:
        info = socket_info.getpeername()
        return (str(info[0]), int(info[1])) if isinstance(info, tuple) else None

    info = transport.get_extra_info("peername")
    if info is not None and isinstance(info, (list, tuple)) and len(info) == 2:
        return (str(info[0]), int(info[1]))
    return None


def is_ssl(transport: Transport) -> bool:
    return bool(transport.get_extra_info("sslcontext"))
