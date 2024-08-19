import sys
import requests
import pytest

sys.path.append("../")
from utils.mapserv import BaiduMapAPI
from utils.sfrequest import get

@pytest.fixture
def api_key():
    return "wdzFSF98TRzTYrHOnro9rUYZY2NTiNTK"

@pytest.fixture
def baidu_map(api_key):
    return BaiduMapAPI(api_key)

class BaiduMapAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.map.baidu.com"

    def get_route(self, origin, destination, waypoints=None, tactics=None):
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
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    response = baidu_map.get_route(origin, destination)
    assert response['status'] == 0, "API 调用失败"
    # 确保访问到嵌套在result中的routes
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线或路线为空"
    assert response['result']['routes'][0]['distance'] > 0, "路线距离应该大于0"

def test_route_planning_with_waypoints(baidu_map):
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    waypoints = "40.015,116.340|40.035,116.420"
    response = baidu_map.get_route(origin, destination, waypoints=waypoints)
    assert response['status'] == 0, "带途经点的路线规划失败"
    # 确保routes在response['result']中存在且非空
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线"

def test_route_planning_with_tactics(baidu_map):
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    tactics = 1  # 不走高速
    response = baidu_map.get_route(origin, destination, tactics=tactics)
    assert response['status'] == 0, "带策略的路线规划失败"
    # 验证路线中是否正确避开了收费道路
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线或路线为空"
    assert response['result']['routes'][0]['toll'] == 0, "策略处理失败，包含了收费道路"

def test_route_planning_invalid_coordinates(baidu_map):
    origin = "91,181"  # 无效的经纬度
    destination = "91,181"
    response = baidu_map.get_route(origin, destination)
    assert response['status'] == 2, "无效坐标应返回错误状态"

if __name__ == "__main__":
    pytest.main(["-v", "test_map.py"])
