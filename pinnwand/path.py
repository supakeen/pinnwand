"""Shorthands for paths for templates, static assets, etc."""
import pathlib

base = pathlib.Path(__file__).parent

template = base / "template"
static = base / "static"
