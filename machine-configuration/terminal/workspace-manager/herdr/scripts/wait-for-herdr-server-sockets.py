import errno
import pathlib
import socket
import sys
import time


def socket_is_occupied(socket_path):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(1)
        try:
            connection.connect(str(socket_path))
        except OSError as error:
            if error.errno in {errno.ENOENT, errno.ECONNREFUSED}:
                return False
            raise
    return True


def wait_for_server_sockets(configuration_directory):
    socket_paths = tuple(
        configuration_directory / socket_name
        for socket_name in ("herdr.sock", "herdr-client.sock")
    )
    while any(socket_is_occupied(socket_path) for socket_path in socket_paths):
        time.sleep(5)


if __name__ == "__main__":
    wait_for_server_sockets(pathlib.Path(sys.argv[1]))
