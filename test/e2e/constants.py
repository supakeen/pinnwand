from enum import Enum


class Theme(Enum):
    DEFAULT = {
        "class": "",
        "font": "rgb(51, 51, 51)",
        "background": "rgb(238, 238, 238)",
    }
    DARK = {
        "class": "other-color",
        "font": "rgb(238, 238, 238)",
        "background": "rgb(51, 51, 51)",
    }


class Filetype(Enum):
    TEXT = {"label": "Text only", "value": "text"}
    PYTHON = {"label": "Python", "value": "python"}
    JAVA = {"label": "Java", "value": "java"}
    JAVASCRIPT = {"label": "JavaScript", "value": "javascript"}
    JSON = {"label": "JSON", "value": "json"}
