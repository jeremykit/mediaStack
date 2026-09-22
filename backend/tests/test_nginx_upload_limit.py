"""测试：分片上传基础设施约束（Nginx 请求体限制 vs 前端分片大小）。

对应需求文档 2.3 节：
- 前端分片大小默认 5MB/片。
- Nginx 反向代理需设置 `client_max_body_size` ≥ 单片大小，
  否则分片请求会在进入后端之前被 Nginx 以 413 Content Too Large 拒绝。

关联缺陷修复：commit 617dc6c（nginx: add client_max_body_size to allow 5MB chunk uploads）
"""
import re
from pathlib import Path

import pytest

from conftest import REPO_ROOT, NGINX_CONF

# 前端分片大小（字节）：frontend/src/views/admin/Upload.vue 中 const n = 5 * 1024 * 1024
FRONTEND_CHUNK_SIZE_BYTES = 5 * 1024 * 1024
BACKEND_DEFAULT_CHUNK_SIZE_BYTES = 5 * 1024 * 1024  # app/schemas/upload.py 默认值


def _parse_max_body_size_mb(conf: str):
    """从 nginx 配置中解析 client_max_body_size，返回字节数。"""
    # 支持 20m / 20M / 2048k / 2048K 等形式
    pattern = re.compile(
        r"client_max_body_size\s+(\d+)([kKmMgG])\s*;", re.IGNORECASE
    )
    match = pattern.search(conf)
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2).lower()
    if unit == "k":
        return value * 1024
    if unit == "m":
        return value * 1024 * 1024
    if unit == "g":
        return value * 1024 * 1024 * 1024
    return value


@pytest.fixture(scope="module")
def nginx_conf() -> str:
    assert NGINX_CONF.exists(), f"nginx 配置文件不存在: {NGINX_CONF}"
    return NGINX_CONF.read_text(encoding="utf-8")


def test_nginx_config_file_exists():
    """nginx 配置模板文件必须存在。"""
    assert NGINX_CONF.exists(), f"未找到 nginx 配置模板: {NGINX_CONF}"


def test_client_max_body_size_is_set(nginx_conf: str):
    """Nginx 必须显式配置 client_max_body_size，
    否则默认 1MB 会拒绝 5MB 分片上传（413 Content Too Large）。"""
    max_body = _parse_max_body_size_mb(nginx_conf)
    assert max_body is not None, (
        "nginx.conf.template 中缺少 client_max_body_size 指令，"
        "默认 1MB 会拒绝超过 1MB 的请求体（分片上传 413）。"
    )


def test_client_max_body_size_covers_frontend_chunk(nginx_conf: str):
    """Nginx 请求体上限必须 ≥ 前端单分片大小，否则分片上传被 413 拦截。"""
    max_body = _parse_max_body_size_mb(nginx_conf)
    assert max_body is not None
    assert max_body >= FRONTEND_CHUNK_SIZE_BYTES, (
        f"Nginx 请求体上限 ({max_body} 字节) 小于前端分片大小 "
        f"({FRONTEND_CHUNK_SIZE_BYTES} 字节)，分片上传会被 413 拒绝。"
    )


def test_nginx_body_limit_margin(nginx_conf: str):
    """留有余量：http 块级别的指令应对分片请求带上的 multipart 头部开销留出空间。"""
    max_body = _parse_max_body_size_mb(nginx_conf)
    assert max_body is not None
    # 要求上限比单分片至少大 1MB 余量（当前配置 20m）
    assert max_body >= FRONTEND_CHUNK_SIZE_BYTES + 1024 * 1024, (
        "client_max_body_size 建议比单分片至少大 1MB 余量，"
        "以容纳 multipart/form-data 的字段与边界开销。"
    )


def test_frontend_backend_chunk_size_consistent():
    """前端与后端默认分片大小应保持一致（均为 5MB）。"""
    frontend = FRONTEND_CHUNK_SIZE_BYTES
    backend = BACKEND_DEFAULT_CHUNK_SIZE_BYTES
    assert frontend == backend, (
        f"前端分片大小 ({frontend}) 与后端默认分片大小 ({backend}) 不一致。"
    )
