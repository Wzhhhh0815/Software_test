import sys
import requests
import pytest

sys.path.append("../")  # 添加上级目录到系统路径，使得能够导入其他模块

# 从utils包中导入BaiduMapAPI类和get函数
from utils.mapserv import BaiduMapAPI
from utils.sfrequest import get


@pytest.fixture
def api_key():
    """
    返回API密钥，用于访问百度地图API。
    """
    return "wdzFSF98TRzTYrHOnro9rUYZY2NTiNTK"


@pytest.fixture
def baidu_map(api_key):
    """
    利用提供的API密钥初始化并返回一个BaiduMapAPI对象。
    """
    return BaiduMapAPI(api_key)


class BaiduMapAPI:
    def __init__(self, api_key):
        """
        构造函数，初始化百度地图API对象。

        参数:
        api_key (str): API密钥，用于认证请求。
        """
        self.api_key = api_key
        self.base_url = "https://api.map.baidu.com"

    def get_route(self, origin, destination, waypoints=None, tactics=None):
        """
        请求百度地图路线规划API以获取两点间的驾车路线。

        参数:
        origin (str): 起点坐标，格式为 "纬度,经度"。
        destination (str): 终点坐标，格式同上。
        waypoints (str): 可选，途径点坐标，格式为 "纬度,经度|纬度,经度"。
        tactics (int): 可选，路线策略编号，例如 1 表示不走高速。

        返回:
        dict: 包含路线规划结果的字典。
        """
        url = f"{self.base_url}/directionlite/v1/driving"
        params = {
            "origin": origin,
            "destination": destination,
            "ak": self.api_key,
            "waypoints": waypoints,
            "tactics": tactics
        }
        response = requests.get(url, params=params)
        return response.json()


def test_route_planning_basic(baidu_map):
    """
    测试基本路线规划功能，确保API能够返回有效的路线数据。
    """
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    response = baidu_map.get_route(origin, destination)
    assert response['status'] == 0, "API 调用失败"
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线或路线为空"
    assert response['result']['routes'][0]['distance'] > 0, "路线距离应该大于0"


def test_route_planning_with_waypoints(baidu_map):
    """
    测试带途径点的路线规划功能，验证API是否能正确处理途径点数据。
    """
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    waypoints = "40.015,116.340|40.035,116.420"
    response = baidu_map.get_route(origin, destination, waypoints=waypoints)
    assert response['status'] == 0, "带途经点的路线规划失败"
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线"


def test_route_planning_with_tactics(baidu_map):
    """
    测试带策略的路线规划功能，检查是否能根据策略避免走收费路线。
    """
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    tactics = 1  # 不走高速
    response = baidu_map.get_route(origin, destination, tactics=tactics)
    assert response['status'] == 0, "带策略的路线规划失败"
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线或路线为空"
    assert response['result']['routes'][0]['toll'] == 0, "策略处理失败，包含了收费道路"


def test_route_planning_invalid_coordinates(baidu_map):
    """
    测试无效坐标的处理，确认API能返回正确的错误状态。
    """
    origin = "91,181"  # 无效的经纬度
    destination = "91,181"
    response = baidu_map.get_route(origin, destination)
    assert response['status'] == 2, "无效坐标应返回错误状态"


if __name__ == "__main__":
    pytest.main(["-v", "test_map.py"])  # 使用pytest执行测试
