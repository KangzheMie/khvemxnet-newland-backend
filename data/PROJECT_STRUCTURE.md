# 博客同步工具项目结构

本文档描述了博客同步工具的项目结构和各文件的作用。

## 项目结构

```
database/
├── lib_database.py          # 数据库操作核心库
├── lib_blog_sync.py         # 博客同步核心逻辑
├── models.py                # 数据库模型定义
├── example_sync.py          # 示例同步脚本（推荐使用）
├── test_new_sync.py         # 新同步逻辑测试脚本
├── simple_sync_test.py      # 简化测试脚本
├── README_blog_sync.md      # 详细使用说明文档
├── PROJECT_STRUCTURE.md     # 本文件 - 项目结构说明
├── requirements.txt         # Python依赖包列表
└── *.db                     # SQLite数据库文件（运行时生成）
```

## 核心文件说明

### 1. 核心库文件

#### `lib_database.py`
- **作用**: 数据库操作的底层接口
- **主要功能**:
  - 数据库连接管理
  - CRUD操作（创建、读取、更新、删除）
  - 数据库统计信息获取
  - 按状态、标题等条件查询博客

#### `lib_blog_sync.py`
- **作用**: 博客同步的核心逻辑
- **主要功能**:
  - Markdown文件扫描和解析
  - Frontmatter元数据提取
  - 基于标题的智能同步策略
  - 失去同步状态检测
  - 内容哈希比较和更新检测

#### `models.py`
- **作用**: 数据库表结构定义
- **包含模型**:
  - Blog（博客文章）
  - Category（分类）
  - Tag（标签）
  - Author（作者）
  - Status（状态）
  - 以及相关的关联表

### 2. 使用脚本

#### `example_sync.py` ⭐ **推荐使用**
- **作用**: 完整的交互式同步示例
- **特点**:
  - 用户友好的交互界面
  - 预演模式（dry-run）
  - 详细的统计信息显示
  - 错误处理和用户提示
  - 可直接运行或作为模块导入

#### `test_new_sync.py`
- **作用**: 新同步逻辑的测试脚本
- **用途**: 开发和调试时使用

#### `simple_sync_test.py`
- **作用**: 简化的测试脚本
- **用途**: 快速验证基本功能

### 3. 文档文件

#### `README_blog_sync.md`
- **作用**: 详细的使用说明文档
- **内容**:
  - 功能概述和特性介绍
  - 安装和配置指南
  - 同步逻辑详细说明
  - Markdown文件格式要求
  - 故障排除指南

#### `requirements.txt`
- **作用**: Python依赖包列表
- **用途**: 使用 `pip install -r requirements.txt` 安装依赖

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行示例脚本
```bash
python example_sync.py
```

### 3. 自定义使用
```python
from lib_blog_sync import BlogSync

# 创建同步工具
sync_tool = BlogSync("/path/to/blog", "sqlite:///my_blog.db")

# 执行同步
stats = sync_tool.sync_to_database(dry_run=False)
print(f"同步完成，处理了 {stats['total_files']} 个文件")
```

## 同步逻辑概述

1. **扫描阶段**: 递归扫描指定目录下的所有 `.md` 文件
2. **解析阶段**: 提取每个文件的 frontmatter 元数据和正文内容
3. **匹配阶段**: 基于标题匹配数据库中的现有博客
4. **同步阶段**: 
   - 新文章：创建新的数据库记录
   - 现有文章：比较内容和元数据，必要时更新
   - 失去同步：标记源文件已删除的数据库记录

## 支持的文件格式

```markdown
---
title: "文章标题"
category: "技术"
author: "作者名"
tags: ["标签1", "标签2"]
status: "published"
created_time: "2024-01-01 12:00:00"
---

# 文章正文

这里是文章内容...
```

## 注意事项

1. **备份重要数据**: 首次使用前请备份现有数据库
2. **文件编码**: 确保 Markdown 文件使用 UTF-8 编码
3. **权限设置**: 确保程序对目标目录和数据库文件有读写权限
4. **路径格式**: Windows 系统请使用原始字符串（r"path"）或双反斜杠

## 故障排除

- **找不到文件**: 检查路径是否正确，使用绝对路径
- **编码错误**: 确保文件使用 UTF-8 编码保存
- **数据库锁定**: 关闭其他可能占用数据库的程序
- **权限问题**: 以管理员身份运行或检查文件夹权限

更多详细信息请参考 `README_blog_sync.md` 文档。