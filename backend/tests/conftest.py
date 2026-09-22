"""Pytest 共享配置与统一定位规则。"""
import os
from pathlib import Path

# 仓库根目录（backend/tests/.. 的上级为仓库根）
REPO_ROOT = Path(__file__).resolve().parents[2]
NGINX_CONF = REPO_ROOT / "nginx" / "nginx.conf.template"
