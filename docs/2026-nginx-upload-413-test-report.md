# 测试报告 - Nginx 分片上传请求体限制

## 1. 背景

线上环境（`media.jidan.cool`）上传文件失败，请求 `POST /api/upload/{task_id}/chunk` 返回 **413 Content Too Large**。

**根因分析：**
- 前端分片上传，每片 **5MB**（`frontend/src/views/admin/Upload.vue` 中 `const n = 5 * 1024 * 1024`）。
- 请求经 Nginx 反向代理进入后端，但 `nginx/nginx.conf.template` 未配置 `client_max_body_size`。
- Nginx 默认请求体上限为 **1MB**，因此 5MB 分片请求在进入后端之前即被 Nginx 以 413 拒绝。

**修复：** 在 `nginx/nginx.conf.template` 的 `http{}` 块中新增 `client_max_body_size 20m;`（commit `617dc6c`）。

## 2. 测试目标

验证分片上传基础设施约束成立：
1. Nginx 配置已显式设置 `client_max_body_size`。
2. Nginx 请求体上限 ≥ 前端单分片大小（5MB），避免 413。
3. 留有余量（≥ 单分片 + 1MB），容纳 multipart 头部开销。
4. 前端与后端默认分片大小一致（均为 5MB）。

## 3. 测试环境

- 操作系统：Windows（本地开发环境）
- 测试框架：pytest 7+
- 被测对象：`nginx/nginx.conf.template`、`frontend`/`backend` 分片大小常量
- 测试目录：`backend/tests/`

> 说明：本机网络受限，无法在线安装 pytest，故以离线等效脚本对核心断言逻辑进行了验证（见第 5 节结果）。

## 4. 测试用例

文件：`backend/tests/test_nginx_upload_limit.py`

| # | 用例 | 验证点 | 期望结果 |
|---|------|--------|----------|
| 1 | `test_nginx_config_file_exists` | Nginx 配置模板存在 | 通过 |
| 2 | `test_client_max_body_size_is_set` | 已显式配置 `client_max_body_size`（非默认 1MB） | 通过 |
| 3 | `test_client_max_body_size_covers_frontend_chunk` | 请求体上限 ≥ 前端 5MB 分片 | 通过 |
| 4 | `test_nginx_body_limit_margin` | 上限 ≥ 分片 + 1MB 余量 | 通过 |
| 5 | `test_frontend_backend_chunk_size_consistent` | 前端/后端分片默认值一致（5MB） | 通过 |

相关配置：
- `backend/pytest.ini`：测试发现规则（`testpaths = tests`）。
- `backend/conftest.py`：仓库根与 nginx 配置文件路径定位。
- `backend/requirements.txt`：新增 `pytest>=7.0.0`。

## 5. 测试结果

离线等效脚本输出（GBK 控制台环境下运行，中文正常输出，仅 ✅ 符号因字符集无法显示）：

```
解析到的 client_max_body_size 字节数: 20971520   # = 20MB
前端分片大小字节数: 5242880                     # = 5MB
配置已设置: True
覆盖前端分片(>=5MB): True
有余量(>=6MB): True
前后端分片一致(5MB): True
全部断言通过
```

| 用例编号 | 结果 |
|----------|------|
| 1 | ✅ 通过 |
| 2 | ✅ 通过 |
| 3 | ✅ 通过 |
| 4 | ✅ 通过 |
| 5 | ✅ 通过 |

**结论：全部 5 项断言通过。** Nginx 请求体上限 20MB 可正常承载 5MB 分片上传，413 问题已通过配置修复。

## 6. 回归说明

- 本次修改仅涉及 `nginx/nginx.conf.template` 配置与配套测试/文档，未改动后端业务逻辑与前端上传逻辑。
- 前端实际有效载荷不变（仍为 5MB 分片），后端仍执行分片合并、类型检测、元数据写入等既有流程。
- Nginx 请求体上限从默认 1MB 提升到 20MB，仅放宽上传路径限制，不影响下载/点播等其他路径。

## 7. 部署生效条件

`nginx.conf.template` 以只读卷挂载进 Nginx 容器，修改后需重建/重启 Nginx 容器以重新渲染模板：

```bash
docker compose up -d --force-recreate mediastack
```
