from .jlf_dict import JLFDict
from .jlf_list import JLFList
from .__version__ import __version__
import json


class JLFEncoder(json.JSONEncoder):
    """自定义 JSON encoder，支持 JLFDict 和 JLFList 序列化"""
    def default(self, obj):
        if isinstance(obj, JLFList):
            return obj.to_list()
        if isinstance(obj, JLFDict):
            return obj.to_dict()
        return super().default(obj)


__all__ = ['JLFDict', 'JLFList', 'JLFEncoder', '__version__']
