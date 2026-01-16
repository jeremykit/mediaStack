# 第二阶段集成测试清单

## 环境准备

```bash
# 1. 确保第一阶段已完成并正常运行
docker-compose up -d

# 2. 访问 http://localhost 确认服务正常

# 3. 使用管理员账号登录
# 默认账号: admin/admin123
```

## 测试场景

### 1. 分类管理
- [ ] 访问 `/admin/categories`
- [ ] 创建分类（名称：测试分类1）
- [ ] 创建分类（名称：测试分类2）
- [ ] 编辑分类名称
- [ ] 拖拽调整分类排序
- [ ] 删除空分类（无关联视频）
- [ ] 尝试删除有视频的分类（应显示错误）
- [ ] 分类名称重复校验

### 2. 标签管理
- [ ] 访问 `/admin/tags`
- [ ] 创建标签（名称：标签A）
- [ ] 创建标签（名称：标签B）
- [ ] 创建标签（名称：标签C）
- [ ] 删除未使用的标签
- [ ] 标签名称重复校验
- [ ] 显示每个标签的使用次数

### 3. 文件上传 - 小文件
- [ ] 访问 `/admin/upload`
- [ ] 拖拽上传小视频文件（< 50MB）
- [ ] 进度条正常显示
- [ ] 上传完成显示成功提示
- [ ] 自动生成缩略图
- [ ] 在视频列表中可见新上传的视频

### 4. 文件上传 - 大文件分片
- [ ] 上传大视频文件（> 100MB）
- [ ] 分片上传进度正常
- [ ] 暂停上传
- [ ] 继续上传（断点续传）
- [ ] 上传完成，文件完整可播放
- [ ] 取消上传，临时文件被清理

### 5. 文件上传 - 音频文件
- [ ] 上传 MP3 文件
- [ ] 上传 WAV 文件
- [ ] 上传 AAC 文件
- [ ] 上传 FLAC 文件
- [ ] 文件类型正确识别为 audio
- [ ] 不生成缩略图（音频无缩略图）

### 6. 文件上传 - 错误处理
- [ ] 上传不支持的文件格式（如 .avi）显示错误
- [ ] 上传超过大小限制的文件显示错误
- [ ] 网络中断后可恢复上传

### 7. 视频分类/标签编辑
- [ ] 访问 `/admin/videos`
- [ ] 编辑视频，设置分类
- [ ] 编辑视频，设置多个标签
- [ ] 列表正确显示分类和标签
- [ ] 清除视频分类
- [ ] 清除视频标签

### 8. 观看码管理
- [ ] 访问 `/admin/view-codes`
- [ ] 创建观看码（6位字母数字）
- [ ] 创建观看码（12位字母数字）
- [ ] 创建观看码并关联分类
- [ ] 设置观看码过期时间
- [ ] 编辑观看码
- [ ] 禁用观看码
- [ ] 启用观看码
- [ ] 删除观看码
- [ ] 复制观看码到剪贴板
- [ ] 观看码格式校验（非法字符）
- [ ] 观看码唯一性校验

### 9. 观看码验证 - 正常流程
- [ ] 退出管理员登录
- [ ] 清除 localStorage
- [ ] 访问首页 `/`
- [ ] 自动跳转到 `/verify`
- [ ] 输入有效观看码
- [ ] 验证成功，跳转首页
- [ ] 首页显示对应分类的视频
- [ ] 刷新页面，无需重新验证

### 10. 观看码验证 - 错误处理
- [ ] 输入无效观看码，显示错误
- [ ] 输入已禁用的观看码，显示错误
- [ ] 输入已过期的观看码，显示错误
- [ ] 错误提示清晰明确

### 11. 首页筛选功能
- [ ] 访问首页 `/`
- [ ] 分类筛选正常工作
- [ ] 标签筛选正常工作（多选）
- [ ] 搜索功能正常
- [ ] 分类 + 标签组合筛选
- [ ] 分类 + 搜索组合筛选
- [ ] 清除筛选条件
- [ ] 只显示观看码允许的分类

### 12. 访问控制
- [ ] 观看码 A 只能访问分类 1
- [ ] 观看码 B 可以访问分类 1 和 2
- [ ] 切换观看码后，可见内容变化
- [ ] 管理员可以看到所有内容

## 性能验收

- [ ] 上传 1GB 文件成功
- [ ] 分片上传速度稳定
- [ ] 首页加载时间 < 2 秒
- [ ] 筛选响应时间 < 500ms

## API 测试

### 分类 API
```bash
# 获取分类列表
curl http://localhost/api/categories

# 创建分类
curl -X POST http://localhost/api/categories \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "测试分类", "sort_order": 0}'

# 更新分类
curl -X PUT http://localhost/api/categories/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "新名称", "sort_order": 1}'

# 删除分类
curl -X DELETE http://localhost/api/categories/1 \
  -H "Authorization: Bearer <token>"
```

### 标签 API
```bash
# 获取标签列表
curl http://localhost/api/tags

# 创建标签
curl -X POST http://localhost/api/tags \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "新标签"}'

# 删除标签
curl -X DELETE http://localhost/api/tags/1 \
  -H "Authorization: Bearer <token>"
```

### 上传 API
```bash
# 初始化上传
curl -X POST http://localhost/api/upload/init \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.mp4", "file_size": 104857600}'

# 查询上传状态
curl http://localhost/api/upload/{task_id}/status \
  -H "Authorization: Bearer <token>"

# 取消上传
curl -X DELETE http://localhost/api/upload/{task_id} \
  -H "Authorization: Bearer <token>"
```

### 观看码 API
```bash
# 获取观看码列表
curl http://localhost/api/view-codes \
  -H "Authorization: Bearer <token>"

# 创建观看码
curl -X POST http://localhost/api/view-codes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC123", "is_active": true, "category_ids": [1, 2]}'

# 验证观看码
curl -X POST http://localhost/api/view-codes/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC123"}'
```

### 视频分类/标签 API
```bash
# 设置视频分类
curl -X PUT http://localhost/api/videos/1/category \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"category_id": 1}'

# 设置视频标签
curl -X PUT http://localhost/api/videos/1/tags \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"tag_ids": [1, 2, 3]}'
```

## 数据库验证

```sql
-- 检查新表是否创建
SELECT name FROM sqlite_master WHERE type='table';

-- 检查分类数据
SELECT * FROM categories;

-- 检查标签数据
SELECT * FROM tags;

-- 检查视频-标签关联
SELECT * FROM video_tags;

-- 检查观看码数据
SELECT * FROM view_codes;

-- 检查观看码-分类关联
SELECT * FROM view_code_categories;

-- 检查上传任务
SELECT * FROM upload_tasks;

-- 检查 VideoFile 新字段
SELECT id, title, category_id, file_type FROM video_files;
```

## 已知限制

- 第二阶段不包含：审核流程、扩展信息（关联图片/文本/链接）、音频提取与下载
- 这些功能将在后续阶段实现

## 测试备注

- 测试日期：____
- 测试人员：____
- 测试环境：____
- 备注：____
