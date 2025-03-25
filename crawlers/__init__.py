from .ifc import parse_html as ifc_parse, pull_html as ifc_pull
from .quad_cinema import parse_html as quad_parse, pull_html as quad_pull
from .metrograph import parse_html as metrograph_parse, pull_html as metrograph_pull


def pull_all():
    return {
        "ifc": ifc_pull(),
        "quad": quad_pull(),
        "metrograph": metrograph_pull(),
    }


def parse_all():
    return (
        ifc_parse() +
        quad_parse() +
        metrograph_parse()
    )


__all__ = [
    "ifc_parse", "ifc_pull",
    "quad_parse", "quad_pull",
    "metrograph_parse", "metrograph_pull",
    "pull_all", "parse_all"
]
