#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YAML-ის ჩაწერის ჰელფერი (ინარჩუნებს გასაღებების თანმიმდევრობას)."""
import os, yaml


class Dumper(yaml.SafeDumper):
    pass


def str_presenter(dumper, data):
    if "\n" in data or len(data) > 110:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


Dumper.add_representer(str, str_presenter)
Dumper.ignore_aliases = lambda *a: True


def dump(path, obj):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(obj, f, Dumper=Dumper, allow_unicode=True,
                  sort_keys=False, width=100, default_flow_style=False)
