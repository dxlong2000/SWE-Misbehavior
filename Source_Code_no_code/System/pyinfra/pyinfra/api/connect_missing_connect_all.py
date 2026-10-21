from typing import TYPE_CHECKING

import gevent



if TYPE_CHECKING:
    from pyinfra.api.state import State


def connect_all(state: "State"):
    """This function connects to all the configured servers in parallel. It reads and writes the inventory of the input State instance. It activates the hosts that are initially connected to and updates the state accordingly.
    Input-Output Arguments
    :param state: State. The state object containing the inventory to connect to.
    :return: No return values.
    """


def disconnect_all(state: "State"):
    for host in state.activated_hosts:  # only hosts we connected to please!
        host.disconnect()  # normally a noop