# 博客数据库操作库

这是一个基于SQLAlchemy的Python数据库操作库，专门用于处理博客系统的数据管理。

## 功能特性

- 完整的博客数据模型（Blog、Category、Tag、Author、Status）
- 多对多关系支持（博客-标签、博客-作者）
- 单对多关系支持（博客-分类、博客-状态）
- 完整的CRUD操作
- 自动哈希计算防重复
- 会话管理和事务支持
- 统计信息查询

## 安装依赖

```bash
pip install -r requirements.txt
```

## 文件结构

```
├── database_models.py      # 数据库模型定义
├── table_operations.py     # 数据库操作函数库
├── test_database.py        # 测试脚本
├── requirements.txt        # 依赖包列表
└── README_database.md      # 使用说明
```

## 数据库表结构

### 主要表

1. **blogs** - 博客文章表
   - id: 主键
   - title: 标题
   - summary: 摘要
   - content: 内容
   - created_time: 创建时间
   - updated_time: 更新时间
   - hash: 内容哈希值
   - category_id: 分类ID（外键）
   - status_id: 状态ID（外键）

2. **categories** - 分类表
   - id: 主键
   - category: 分类名称

3. **tags** - 标签表
   - id: 主键
   - tag: 标签名称

4. **authors** - 作者表
   - id: 主键
   - author: 作者名称

5. **status** - 状态表
   - id: 主键
   - status: 状态名称

### 关系表

- **blog_tags** - 博客标签多对多关系表
- **blog_authors** - 博客作者多对多关系表

## 快速开始

### 1. 基本使用

```python
from table_operations import TableOperations

# 创建数据库操作实例
table_ops = TableOperations('sqlite:///blog.db')

# 创建数据库表
table_ops.create_tables()
```

### 2. 创建博客文章

```python
# 创建博客文章
blog = table_ops.create_blog(
    title="我的第一篇博客",
    content="这是博客的内容...",
    summary="博客摘要",
    category_name="技术",
    authors=["张三", "李四"],
    tags=["Python", "数据库"],
    status_name="published"
)

print(f"创建博客成功，ID: {blog.id}")
```

### 3. 查询操作

```python
# 获取所有博客
all_blogs = table_ops.get_all_blogs()

# 根据分类查询
tech_blogs = table_ops.get_blogs_by_category("技术")

# 根据标签查询
python_blogs = table_ops.get_blogs_by_tag("Python")

# 根据作者查询
author_blogs = table_ops.get_blogs_by_author("张三")

# 根据状态查询
published_blogs = table_ops.get_all_blogs("published")
```

### 4. 更新操作

```python
# 更新博客
table_ops.update_blog(
    blog_id=1,
    title="更新后的标题",
    status_name="draft",
    tags=["Python", "教程"]
)
```

### 5. 删除操作

```python
# 删除博客
result = table_ops.delete_blog(blog_id=1)
print(f"删除结果: {'成功' if result else '失败'}")
```

### 6. 统计信息

```python
# 获取统计信息
stats = table_ops.get_statistics()
print(stats)
# 输出示例:
# {
#     'total_blogs': 10,
#     'total_categories': 3,
#     'total_tags': 15,
#     'total_authors': 5,
#     'total_statuses': 2,
#     'blogs_by_status': {'published': 8, 'draft': 2},
#     'blogs_by_category': {'技术': 6, '生活': 4}
# }
```

## API 参考

### TableOperations 类

#### 博客操作
- `create_blog(title, content, summary=None, category_name=None, authors=None, tags=None, status_name="published", created_time=None, updated_time=None)` - 创建博客
- `get_blog_by_id(blog_id)` - 根据ID获取博客
- `get_blog_by_hash(content_hash)` - 根据哈希值获取博客
- `get_blogs_by_category(category_name)` - 根据分类获取博客列表
- `get_blogs_by_tag(tag_name)` - 根据标签获取博客列表
- `get_blogs_by_author(author_name)` - 根据作者获取博客列表
- `get_all_blogs(status_name=None)` - 获取所有博客
- `update_blog(blog_id, **kwargs)` - 更新博客
- `delete_blog(blog_id)` - 删除博客

#### 分类操作
- `create_category(category_name)` - 创建分类
- `get_all_categories()` - 获取所有分类
- `update_category(category_id, new_name)` - 更新分类
- `delete_category(category_id)` - 删除分类

#### 标签操作
- `create_tag(tag_name)` - 创建标签
- `get_all_tags()` - 获取所有标签
- `update_tag(tag_id, new_name)` - 更新标签
- `delete_tag(tag_id)` - 删除标签

#### 作者操作
- `create_author(author_name)` - 创建作者
- `get_all_authors()` - 获取所有作者
- `update_author(author_id, new_name)` - 更新作者
- `delete_author(author_id)` - 删除作者

#### 状态操作
- `create_status(status_name)` - 创建状态
- `get_all_statuses()` - 获取所有状态
- `update_status(status_id, new_name)` - 更新状态
- `delete_status(status_id)` - 删除状态

#### 其他操作
- `create_tables()` - 创建数据库表
- `drop_tables()` - 删除数据库表
- `get_statistics()` - 获取统计信息

## 运行测试

```bash
python test_database.py
```

测试脚本会自动：
1. 创建测试数据库
2. 测试所有CRUD操作
3. 验证查询功能
4. 显示统计信息
5. 清理测试数据

## 注意事项

1. **哈希防重复**: 系统会自动计算文件内容的MD5哈希值，防止重复内容的博客
2. **会话管理**: 使用上下文管理器自动处理数据库会话的开启和关闭
3. **关系处理**: 创建博客时会自动创建不存在的分类、标签、作者等
4. **删除限制**: 删除分类或状态时，如果有关联的博客会抛出异常
5. **数据库支持**: 默认使用SQLite，可以通过修改连接字符串支持其他数据库

## 数据库连接

支持多种数据库：

```python
# SQLite
table_ops = TableOperations('sqlite:///blog.db')

# MySQL
table_ops = TableOperations('mysql://user:password@localhost/blog')

# PostgreSQL
table_ops = TableOperations('postgresql://user:password@localhost/blog')
```

## 错误处理

```python
try:
    blog = table_ops.create_blog(
        title="测试博客",
        content="重复内容"
    )
except ValueError as e:
    print(f"创建失败: {e}")
```

## 许可证

本项目采用 MIT 许可证。