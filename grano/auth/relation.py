import network as network_auth


def list(network):
    return network_auth.read(network)


def create(network):
    return network_auth.update(network)


def read(network, relation):
    return network_auth.read(network)


def update(network, relation):
    return network_auth.update(network)


def delete(network, relation):
    return network_auth.update(network)
