
def every(element, namespace):
    return element.iter(namespace)


def find_first(element, namespace):
    return element.find(r'.//' + namespace)


def children(element):
    # the element itself is an iterator of its children
    return element
