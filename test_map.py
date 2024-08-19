import sys
import requests
import pytest

sys.path.append("../")  # 将上级目录添加到系统路径，以便导入其他模块
from utils.mapserv import BaiduMapAPI  # 从utils模块的mapserv文件导入BaiduMapAPI类
from utils.sfrequest import get  # 导入sfrequest文件的get函数

@pytest.fixture
def api_key():
    return "wdzFSF98TRzTYrHOnro9rUYZY2NTiNTK"  # 返回API密钥

@pytest.fixture
def baidu_map(api_key):
    return BaiduMapAPI(api_key)  # 使用API密钥初始化BaiduMapAPI对象，并返回

class BaiduMapAPI:
    def __init__(self, api_key):
        self.api_key = api_key  # API密钥
        self.base_url = "https://api.map.baidu.com"  # 百度地图API的基础URL

    def get_route(self, origin, destination, waypoints=None, tactics=None):
        url = f"{self.base_url}/directionlite/v1/driving"  # 构造请求URL
        params = {
            "origin": origin,  # 起点坐标
            "destination": destination,  # 终点坐标
            "ak": self.api_key,  # API密钥
            "waypoints": waypoints,  # 途经点
            "tactics": tactics  # 路线策略
        }
        response = requests.get(url, params=params)  # 发起GET请求
        return response.json()  # 返回解析为JSON格式的响应数据

def test_route_planning_basic(baidu_map):
    origin = "40.01116,116.339303"  # 设置起点坐标
    destination = "39.936404,116.452562"  # 设置终点坐标
    response = baidu_map.get_route(origin, destination)  # 请求路线规划
    assert response['status'] == 0, "API 调用失败"  # 断言状态码为0，即调用成功
    # 确保返回的路线信息是有效的
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线或路线为空"
    assert response['result']['routes'][0]['distance'] > 0, "路线距离应该大于0"

def test_route_planning_with_waypoints(baidu_map):
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    waypoints = "40.015,116.340|40.035,116.420"  # 设置途经点
    response = baidu_map.get_route(origin, destination, waypoints=waypoints)  # 请求带途经点的路线规划
    assert response['status'] == 0, "带途经点的路线规划失败"
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线"

def test_route_planning_with_tactics(baidu_map):
    origin = "40.01116,116.339303"
    destination = "39.936404,116.452562"
    tactics = 1  # 设置策略为不走高速
    response = baidu_map.get_route(origin, destination, tactics=tactics)  # 请求带策略的路线规划
    assert response['status'] == 0, "带策略的路线规划失败"
    assert 'result' in response and 'routes' in response['result'] and response['result']['routes'], "没有返回路线或路线为空"
    assert response['result']['routes'][0]['toll'] == 0, "策略处理失败，包含了收费道路"

def test_route_planning_invalid_coordinates(baidu_map):
    origin = "91,181"  # 设置无效的经纬度
    destination = "91,181"
    response = baidu_map.get_route(origin, destination)  # 请求路线规划
    assert response['status'] == 2, "无效坐标应返回错误状态"

if __name__ == "__main__":
    pytest.main(["-v", "test_map.py"])  # 使用pytest模块运行测试
