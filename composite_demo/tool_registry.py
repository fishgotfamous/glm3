import copy
import inspect
from pprint import pformat
import traceback
from types import GenericAlias
from typing import get_origin, Annotated

_TOOL_HOOKS = {}
_TOOL_DESCRIPTIONS = {}

def register_tool(func: callable):
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip()
    python_params = inspect.signature(func).parameters
    tool_params = []
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")
        if get_origin(annotation) != Annotated:
            raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")
        
        typ, (description, required) = annotation.__origin__, annotation.__metadata__
        typ: str = str(typ) if isinstance(typ, GenericAlias) else typ.__name__
        if not isinstance(description, str):
            raise TypeError(f"Description for `{name}` must be a string")
        if not isinstance(required, bool):
            raise TypeError(f"Required for `{name}` must be a bool")

        tool_params.append({
            "name": name,
            "description": description,
            "type": typ,
            "required": required
        })
    tool_def = {
        "name": tool_name,
        "description": tool_description,
        "params": tool_params
    }

    print("[registered tool] " + pformat(tool_def))
    _TOOL_HOOKS[tool_name] = func
    _TOOL_DESCRIPTIONS[tool_name] = tool_def

    return func

def dispatch_tool(tool_name: str, tool_params: dict) -> str:
    if tool_name not in _TOOL_HOOKS:
        return f"Tool `{tool_name}` not found. Please use a provided tool."
    tool_call = _TOOL_HOOKS[tool_name]
    try:
        ret = tool_call(**tool_params)  
    except:
        ret = traceback.format_exc()
    return str(ret)

def get_tools() -> dict:
    return copy.deepcopy(_TOOL_DESCRIPTIONS)

# Tool Definitions

@register_tool
def random_number_generator(
    seed: Annotated[int, 'The random seed used by the generator', True], 
    range: Annotated[tuple[int, int], 'The range of the generated numbers', True],
) -> int:
    """
    Generates a random number x, s.t. range[0] <= x < range[1]
    """
    if not isinstance(seed, int):
        raise TypeError("Seed must be an integer")
    if not isinstance(range, tuple):
        raise TypeError("Range must be a tuple")
    if not isinstance(range[0], int) or not isinstance(range[1], int):
        raise TypeError("Range must be a tuple of integers")

    import random
    return random.Random(seed).randint(*range)

@register_tool
def get_weather(
    city_name: Annotated[str, 'The name of the city to be queried', True],
) -> str:
    """
    Get the current weather for `city_name`
    """

    if not isinstance(city_name, str):
        raise TypeError("City name must be a string")

    key_selection = {
        "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc",  "observation_time"],
    }
    import requests
    try:
        resp = requests.get(f"https://wttr.in/{city_name}?format=j1")
        resp.raise_for_status()
        resp = resp.json()
        ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
    except:
        import traceback
        ret = "Error encountered while fetching weather data!\n" + traceback.format_exc() 

    return str(ret)


@register_tool
def IM_Handbook(
        key_word_name: Annotated[str, 'The name of the Knowledge', True],
) -> str:
    """
    Get the explain for `key_word_name`
    """

    book = {
        "FIOS": "Factory Intelligent Operation System，工厂智能运营管理：是一种采用人工智能和物联网技术的工厂数字化管理系统。它可以实现生产过程的全面监控、数据分析和预测，实现生产资源的精细化管理和智能化运营监控，帮助企业优化生产流程、提高生产效率和降低成本。包括：生产计划、仓储物流、质量控制、机器维护、供应链管理、和成本分析等管理功能。",
        "APS": "Advanced Planning System，高级计划排程系统：提供爬坡、试产和量产等不同阶段的物料计划与生产计划的排布与调整、以及监控与反馈生产达成情况的功能。",
        "PMS": "Process management system，工艺管理系统：提供工艺SOP设计与制作、审批与转发、工艺项目管理、工艺差异分析、工艺问题诊断与解决方案推荐的一系列工艺数字化功能",
        "MES": "Manufacturing execution system，制造执行系统：对产线生产过程进行管理和卡控	包括：过站配置与管理、与自动化对接、产线物流调度、数据采集与分析等",
        "WMS": "Warehouse management system，仓储物流管理系统：提供物料、半成品和成品的仓储物流全部环节的管理，包括：出库、入库、库内管理、备品备件管理、与AGV或智能货架等智能设备对接、物流调度等",
        "QMS": "Quality Management System，质量管理系统：依据质量管理体系对工厂从来料到成品出厂进行全流程的质量管理，包括：lQC、IPQC、FQC、0QC、质量分析、质量溯源等",
        "TPM": "Total Productive Maintenance，设备管理系统：提供工厂内生产设备全生命周期的维保管理和资产管理工具，包括：维保计划、维保实施、备件管理、资产管理等",
        "MOM": "Manufacturing Operation Management，制造运营管理：制造运营管理系统平台",
        "于成铭": "软件工程部下属工业智能组的一名成员，负责数字员工项目"
    }
    if not isinstance(key_word_name, str):
        raise TypeError("Key word name must be a string")
    if key_word_name not in book.keys():
        raise TypeError("Key word name is not contained")
    else:
        result = book[key_word_name]
    return result

if __name__ == "__main__":
    print(dispatch_tool("get_weather", {"city_name": "beijing"}))
    print(get_tools())
