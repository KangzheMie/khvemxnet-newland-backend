from lib_database import TableOperations
import os

os.chdir(os.path.dirname(__file__))

def main():
    """主函数 - 演示数据库操作库的使用"""
    print("博客数据库操作库使用示例")
    print("=" * 40)
    
    # 1. 初始化数据库
    print("\n1. 初始化数据库...")
    db_path = "./test_blog_operations.db"
    
    # 如果数据库已存在，删除它以便重新开始
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建数据库操作实例
    table_ops = TableOperations(f'sqlite:///{db_path}')
    
    # 创建所有表
    table_ops.create_tables()
    print("✓ 数据库表创建完成")
    
    # 2. 创建基础数据
    print("\n2. 创建基础数据...")
    
    # 创建一些示例博客文章
    blogs_data = [
        {
            "title": "Python入门教程",
            "content": """# Python入门教程

## 什么是Python？

Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。

## 安装Python

1. 访问Python官网
2. 下载适合你操作系统的版本
3. 按照安装向导完成安装

## 第一个Python程序

```python
print("Hello, World!")
```

这就是你的第一个Python程序！
""",
            "summary": "从零开始学习Python编程语言的基础知识",
            "category_name": "编程教程",
            "authors": ["张三", "李四"],
            "tags": ["Python", "编程", "入门", "教程"],
            "status_name": "published"
        },
        {
            "title": "数据库设计原则",
            "content": """# 数据库设计原则

## 范式化

数据库设计应该遵循范式化原则，避免数据冗余。

### 第一范式（1NF）
- 每个字段都是原子性的
- 不可再分

### 第二范式（2NF）
- 满足1NF
- 非主键字段完全依赖于主键

### 第三范式（3NF）
- 满足2NF
- 非主键字段不依赖于其他非主键字段

## 索引设计

合理的索引设计可以大大提高查询性能。
""",
            "summary": "介绍数据库设计的基本原则和最佳实践",
            "category_name": "数据库",
            "authors": ["王五"],
            "tags": ["数据库", "设计", "范式", "索引"],
            "status_name": "published"
        },
        {
            "title": "我的编程学习心得",
            "content": """# 我的编程学习心得

## 学习方法

编程学习需要理论与实践相结合：

1. **理论学习**：阅读书籍和文档
2. **动手实践**：编写代码解决实际问题
3. **项目经验**：参与开源项目或自己创建项目
4. **持续学习**：技术更新很快，需要保持学习

## 遇到的困难

- 语法理解困难
- 调试技巧不足
- 项目经验缺乏

## 解决方案

- 多练习，多写代码
- 学会使用调试工具
- 从小项目开始积累经验
""",
            "summary": "分享个人编程学习过程中的经验和心得",
            "category_name": "个人感悟",
            "authors": ["张三"],
            "tags": ["学习", "经验", "编程"],
            "status_name": "draft"
        }
    ]
    
    created_blogs = []
    for blog_data in blogs_data:
        blog = table_ops.create_blog(**blog_data)
        created_blogs.append(blog)
        print(f"✓ 创建博客: {blog_data['title']} (ID: {blog.id})")
    
    # 3. 查询操作演示
    print("\n3. 查询操作演示...")
    
    # 获取所有博客
    all_blogs = table_ops.get_all_blogs()
    print(f"✓ 总博客数量: {len(all_blogs)}")
    
    # 按状态查询
    published_blogs = table_ops.get_all_blogs("published")
    draft_blogs = table_ops.get_all_blogs("draft")
    print(f"✓ 已发布博客: {len(published_blogs)} 篇")
    print(f"✓ 草稿博客: {len(draft_blogs)} 篇")
    
    # 按分类查询
    categories = table_ops.get_all_categories()
    print(f"\n✓ 所有分类 ({len(categories)} 个):")
    for category in categories:
        blogs_in_category = table_ops.get_blogs_by_category(category.category)
        print(f"   - {category.category}: {len(blogs_in_category)} 篇博客")
    
    # 按标签查询
    tags = table_ops.get_all_tags()
    print(f"\n✓ 所有标签 ({len(tags)} 个):")
    for tag in tags:
        blogs_with_tag = table_ops.get_blogs_by_tag(tag.tag)
        print(f"   - {tag.tag}: {len(blogs_with_tag)} 篇博客")
    
    # 按作者查询
    authors = table_ops.get_all_authors()
    print(f"\n✓ 所有作者 ({len(authors)} 个):")
    for author in authors:
        author_blogs = table_ops.get_blogs_by_author(author.author)
        print(f"   - {author.author}: {len(author_blogs)} 篇博客")
    
    # 4. 更新操作演示
    print("\n4. 更新操作演示...")
    
    # 将草稿状态的博客发布
    draft_blog = created_blogs[2]  # "我的编程学习心得"
    updated_blog = table_ops.update_blog(
        draft_blog.id,
        status_name="published",
        tags=["学习", "经验", "编程", "心得"]
    )
    print(f"✓ 更新博客状态: {updated_blog.id if updated_blog else '失败'}")
    
    # 5. 统计信息
    print("\n5. 数据库统计信息...")
    stats = table_ops.get_statistics()
    print("✓ 统计结果:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"     - {sub_key}: {sub_value}")
        else:
            print(f"   {key}: {value}")
    
    # 6. 高级查询示例
    print("\n6. 高级查询示例...")
    
    # 查找包含"Python"标签的博客
    python_blogs = table_ops.get_blogs_by_tag("Python")
    print(f"✓ 包含'Python'标签的博客: {len(python_blogs)} 篇")
    
    # 查找"张三"的所有博客
    zhang_blogs = table_ops.get_blogs_by_author("张三")
    print(f"✓ 张三的博客: {len(zhang_blogs)} 篇")
    
    # 查找"编程教程"分类的博客
    tutorial_blogs = table_ops.get_blogs_by_category("编程教程")
    print(f"✓ 编程教程分类的博客: {len(tutorial_blogs)} 篇")
    
    # 7. 清理演示
    print("\n7. 清理演示...")
    
    # 删除一篇博客
    delete_result = table_ops.delete_blog(created_blogs[0].id)
    print(f"✓ 删除博客结果: {'成功' if delete_result else '失败'}")
    
    # 验证删除后的数量
    remaining_blogs = table_ops.get_all_blogs()
    print(f"✓ 删除后剩余博客数量: {len(remaining_blogs)}")
    
    print("\n" + "=" * 40)
    print("示例演示完成！")
    print(f"数据库文件: {db_path}")
    print("你可以使用SQLite工具查看数据库内容")
    print("=" * 40)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"运行出错: {e}")
        import traceback
        traceback.print_exc()