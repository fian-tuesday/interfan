from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class Parameter:
    arg_name: str
    type_name: Optional[str] = None
    description: Optional[str] = None
    default: Optional[str] = None


@dataclass
class DocString:
    short_description: str
    long_description: str
    params: List[Parameter]


def parse(doc: str) -> DocString:
    """
    Docstring parser

    Description

    :param str doc: docstring
    :param range(10, 100, 100) something: just for test default 10
    :return:
    """
    doc_lines = doc.strip().splitlines()
    if not doc_lines:
        return DocString('', '', [])
    name, *doc_lines = doc_lines
    description = []
    params = []
    for line in doc_lines:
        line = line.strip()
        if not line.startswith(':'):
            description.append(line)
        elif line.startswith(':param'):
            arg, desc = line[6:].split(':', 1)
            *arg_type, arg_name = arg.split()
            arg_type = ' '.join(arg_type)
            default = None
            if 'default' in desc:
                desc, default = desc.split('default')
                default = default.strip()
            params.append(Parameter(arg_name, arg_type, desc.strip(), default))
    return DocString(name, '\n'.join(description), params)


if __name__ == '__main__':
    print(parse(parse.__doc__))
