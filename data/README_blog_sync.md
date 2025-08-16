# 博客同步工具使用说明

## 概述

博客同步工具 (`BlogSync`) 实现了 Markdown 文件与 SQLite 数据库之间的双向同步功能。该工具支持基于标题的智能匹配、内容和元数据的完整更新检测，以及失去同步状态的自动检测。

## 主要特性

### 1. 智能同步策略
- **基于标题匹配**：优先通过博客标题进行匹配，而非内容哈希
- **完整更新检测**：检测内容、元数据的所有变化
- **失去同步检测**：自动识别已删除的源文件，标记为 `lost_sync` 状态

### 2. 支持的文件格式
- **标准 Frontmatter 格式**：支持 YAML 格式的元数据头
- **旧格式兼容**：自动处理没有 frontmatter 的文件
- **多种日期格式**：灵活解析各种日期时间格式

### 3. 元数据支持
- `title`: 博客标题
- `content`: 正文内容
- `summary`: 摘要（可选，默认截取前200字符）
- `category`/`categories`: 分类
- `authors`: 作者列表
- `tags`: 标签列表
- `status`: 状态（published, draft, lost_sync 等）
- `created_time`: 创建时间
- `updated_time`: 更新时间

## 安装和配置

### 依赖要求
```bash
pip install sqlalchemy>=2.0.0 pyyaml
```

### 基本使用

```python
from lib_blog_sync import BlogSync

# 创建同步工具实例
blog_dir = "path/to/your/markdown/files"
db_url = "sqlite:///blog.db"  # 或其他数据库URL
sync_tool = BlogSync(blog_dir, db_url)

# 执行同步（预演模式）
stats = sync_tool.sync_to_database(dry_run=True)
print("预演统计:", stats)

# 执行实际同步
stats = sync_tool.sync_to_database(dry_run=False)
print("同步统计:", stats)
```

## 同步逻辑详解

### 同步流程

1. **初始化阶段**
   - 将数据库中所有博客状态标记为 `lost_sync`
   - 扫描指定目录下的所有 `.md` 文件

2. **文件处理阶段**
   - 解析每个 Markdown 文件的 frontmatter 元数据
   - 基于标题查找数据库中的对应博客

3. **同步决策**
   - **如果找到匹配标题**：
     - 检查内容和元数据是否有变化
     - 有变化则更新，无变化则恢复为原状态
   - **如果未找到匹配**：
     - 创建新的博客记录

4. **失去同步检测**
   - 同步完成后，仍为 `lost_sync` 状态的博客即为失去同步的文件
   - 打印失去同步的博客列表

### 状态说明

- `published`: 已发布（默认状态）
- `draft`: 草稿
- `lost_sync`: 失去同步（源文件已删除）

## 示例脚本

### 基本同步示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from lib_blog_sync import BlogSync

def main():
    # 配置路径
    blog_dir = r"d:\path\to\your\blog\files"
    db_path = "blog_sync.db"
    
    # 创建同步工具
    sync_tool = BlogSync(blog_dir, f'sqlite:///{db_path}')
    
    print("开始博客同步...")
    
    # 执行同步
    stats = sync_tool.sync_to_database(dry_run=False)
    
    # 显示结果
    print("\n同步完成！统计信息:")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  新增文件: {stats['new_files']}")
    print(f"  更新文件: {stats['updated_files']}")
    print(f"  跳过文件: {stats['skipped_files']}")
    print(f"  失败文件: {stats['failed_files']}")
    print(f"  失去同步: {stats['lost_sync_files']}")

if __name__ == "__main__":
    main()
```

### 高级使用示例

```python
from lib_blog_sync import BlogSync
from lib_database import TableOperations

def advanced_sync():
    blog_dir = "path/to/blog"
    db_url = "sqlite:///advanced_blog.db"
    
    sync_tool = BlogSync(blog_dir, db_url)
    table_ops = TableOperations(db_url)
    
    # 1. 预演同步
    print("=== 预演模式 ===")
    dry_stats = sync_tool.sync_to_database(dry_run=True)
    
    # 2. 实际同步
    print("\n=== 实际同步 ===")
    real_stats = sync_tool.sync_to_database(dry_run=False)
    
    # 3. 获取详细统计
    db_stats = table_ops.get_statistics()
    print("\n=== 数据库统计 ===")
    for key, value in db_stats.items():
        print(f"{key}: {value}")
    
    # 4. 查看失去同步的博客
    lost_blogs = table_ops.get_blogs_by_status('lost_sync')
    if lost_blogs:
        print("\n=== 失去同步的博客 ===")
        for blog in lost_blogs:
            print(f"- {blog.title}")

if __name__ == "__main__":
    advanced_sync()
```

## Markdown 文件格式示例

### 标准 Frontmatter 格式

```markdown
---
title: "我的第一篇博客"
summary: "这是一篇关于博客同步工具的介绍文章"
categories: "技术"
authors:
  - "张三"
  - "李四"
tags:
  - "Python"
  - "数据库"
  - "同步"
status: "published"
created_time: "2024-01-15 10:30:00"
updated_time: "2024-01-16 15:45:00"
---

# 博客正文开始

这里是博客的正文内容...

## 小节标题

更多内容...
```

### 旧格式（无 Frontmatter）

```markdown
# 技术_我的编程心得

这是一篇没有 frontmatter 的旧格式文章。
工具会自动从文件名提取分类和标题信息。
```

## 注意事项

1. **文件编码**：确保 Markdown 文件使用 UTF-8 编码
2. **标题唯一性**：建议保持博客标题的唯一性，避免同步冲突
3. **备份数据**：在首次同步前建议备份现有数据库
4. **权限问题**：确保程序对博客目录和数据库文件有读写权限
5. **大量文件**：处理大量文件时建议先使用预演模式检查

## 故障排除

### 常见问题

1. **Session 分离错误**
   - 已在最新版本中修复
   - 确保使用最新的 `lib_database.py`

2. **YAML 解析错误**
   - 检查 frontmatter 的 YAML 格式是否正确
   - 确保缩进使用空格而非制表符

3. **文件编码问题**
   - 确保文件使用 UTF-8 编码
   - 检查文件中是否有特殊字符

4. **数据库连接问题**
   - 检查数据库 URL 格式是否正确
   - 确保数据库文件路径存在且可写

### 调试技巧

1. **使用预演模式**：先用 `dry_run=True` 检查同步结果
2. **查看日志**：注意控制台输出的错误信息
3. **分批处理**：对于大量文件，可以分批次处理
4. **检查统计**：通过返回的统计信息了解同步状态

## 更新日志

### v2.0.0 (最新)
- 改进同步策略：从基于哈希匹配改为基于标题匹配
- 新增失去同步状态检测功能
- 修复 SQLAlchemy Session 分离问题
- 增强错误处理和日志输出
- 支持完整的内容和元数据更新

### v1.0.0
- 基础的 Markdown 到数据库同步功能
- 支持 frontmatter 元数据解析
- 基于内容哈希的重复检测

## 技术支持

如遇到问题，请检查：
1. 依赖包版本是否正确
2. 文件路径和权限设置
3. 数据库连接配置
4. Markdown 文件格式

更多技术细节请参考源代码中的注释和测试用例。