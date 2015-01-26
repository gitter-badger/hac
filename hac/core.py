# -*- coding: utf-8 -*-
"""This module provides the main functionality.
"""
import os
import sys
import textwrap

from hac import ExitStatus
from hac.config import DEFAULTS, config_parser
from hac.cli import cli_parser
from hac.plugins import collect_sites
from hac.utility import match_site, get_site


def dict_override(a, b):
    """Overriding dictionary values.

    Values in second dictionary override the values in the first one (except
    when relevant value in second dictionary is None).

    >>> dict_override({'a': 1,'b': 2}, {'a': 3,'b': None}) == {'a': 3,'b': 2}
    True

    >>> dict_override({'a': 3,'b': None}, {'a': 1,'b': 2}) == {'a': 1,'b': 2}
    True
    """
    res = {}
    for key in (set(a.keys()) | set(b.keys())):
        if (key in b) and (b[key] != None):
            res[key] = b[key]
        else:
            res[key] = a[key]
    return res


def reduce_list(a):
    """Reduces provided list in two steps:
        1) removes all elements from list that appear prior to any 'no' element,
        2) removes duplicates and sorts elements.

    >>> reduce_list(['cpp', 'no', 'php', 'py', 'php', 'py'])
    ['php', 'py']

    >>> reduce_list(['cpp', 'no', 'php', 'py', 'php', 'no', 'py', 'cpp'])
    ['cpp', 'py']
    """
    b = list(reversed(a))
    if "no" in b:
        ind = b.index("no")
        del b[ind:]
    return sorted(set(b))


def remove_optionals(a):
    """Removes optional arguments that precede mandatory arguments.

    >>> remove_optionals(['--cpp', '-no', 'php', '-t', 'py'])
    ['php', '-t', 'py']

    >>> remove_optionals(['--cpp', '-no'])
    []
    """
    b = a[:]
    while(len(b)>0 and b[0].startswith("-")):
        del b[0]
    return b


def main(args=sys.argv[1:]):
    """Execution flow of the main function:

    1) get configuration (priorities: default < local < cli)
    2) branch according to command (prep, show)
    """

    # Get default application configuration
    global_config_file = os.path.join(DEFAULTS["config_app_dirpath"],
        DEFAULTS["config_filename"])
    env_global = config_parser.parse_args(['@' + global_config_file])

    # Get user specifirc configuration
    user_config_file = os.path.join(DEFAULTS["config_user_dirpath"],
        DEFAULTS["config_filename"])
    if os.path.exists(user_config_file):
        env_user = config_parser.parse_args(['@' + user_config_file])

    # Resolve configuration read from files
    conf_user = dict_override(vars(env_global), vars(env_user))

    # Show help and exit when no arguments given.
    if len(args) == 0:
        cli_parser.print_help()
        sys.exit(ExitStatus.ERROR)

    # When no command given, use default from configuration files
    rargs = remove_optionals(args)
    if (len(rargs) < 1) or (rargs[0] not in {"prep", "show"}):
        args.insert(0, conf_user["command"])

    # Parse CLI arguments and resolve with respect to configuration files
    env_cli = cli_parser.parse_args(args=args)
    conf_all = dict_override(conf_user, vars(env_cli))

    # Reduce lang and runner lists
    conf_all["lang"] = reduce_list(conf_all["lang"])
    conf_all["runner"] = reduce_list(conf_all["runner"])

    # Get web-site processors (user-defined and default)
    sites = collect_sites()

    # 1) Heuristically match web-site -> site-url
    # 2) Extract site object
    # NOTE: Done in two steps for consistency and testability
    site_url = match_site(sites, conf_all)
    site_obj = get_site(sites, site_url)

    # TODO to-logging
    import pprint; pp = pprint.PrettyPrinter(indent=4)
    print("USER"); pp.pprint(conf_user)
    print("ALL"); pp.pprint(conf_all)

    # TODO to-logging
    print(sites[0].url, sites[0].match_contest(None))
    print(sites[1].url, sites[1].match_contest(None))

    # TODO to-logging
    print("Picked {0}".format(site_obj.url))

    # TODO #1 web page-information DS
    # TODO #2 web-parsing DS and processor
    # TODO #3 decipher which problems to fetch (URL, other)
    # TODO #4 show command
    # TODO #5 prep command

    # TODO create whole directory structure for dir that doesn't exist
    # TODO resolve paths got from user (~ etc.)
    # TODO configurable name of directories for site (ID or NAME)
    # TODO configurable name of directories for contest (ID or NAME)
    # TODO configurable name of directories for problem (ID or NAME)
    # TODO quiet mode -> don't show errors
    # TODO support for site-specific templates and multiple templates per language

