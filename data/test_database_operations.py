from lib_database import TableOperations
import os

os.chdir(os.path.dirname(__file__))

def test_database_operations():
    """测试数据库操作功能"""
    print("=" * 50)
    print("开始测试数据库操作功能")
    print("=" * 50)
    
    # 使用测试数据库
    test_db_path = "./test_database_operations.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    table_ops = TableOperations(f'sqlite:///{test_db_path}')
    
    try:
        # 1. 创建数据库表
        print("\n1. 创建数据库表...")
        table_ops.create_tables()
        print("✓ 数据库表创建成功")
        
        # 2. 创建基础数据
        print("\n2. 创建基础数据...")
        
        # 创建状态
        table_ops.create_status("published")
        table_ops.create_status("published")
        table_ops.create_status("published")
        table_ops.create_status("published")
        table_ops.create_status("draft")
        print("✓ 创建状态: published, draft")
        
        # 创建分类
        table_ops.create_category("技术")
        table_ops.create_category("生活")
        print("✓ 创建分类: 技术, 生活")
        
        # 创建作者
        table_ops.create_author("张三")
        table_ops.create_author("李四")
        print("✓ 创建作者: 张三, 李四")
        
        # 创建标签
        table_ops.create_tag("Python")
        table_ops.create_tag("数据库")
        table_ops.create_tag("教程")
        print("✓ 创建标签: Python, 数据库, 教程")
        
        # 3. 创建博客文章
        print("\n3. 创建博客文章...")
        
        blog1 = table_ops.create_blog(
            title="Python数据库操作教程",
            content="这是一篇关于Python数据库操作的详细教程。\n\n## 简介\n\n本教程将介绍如何使用SQLAlchemy进行数据库操作...",
            summary="学习如何使用Python进行数据库操作",
            category_name="技术",
            authors=["张三", "李四"],
            tags=["Python", "数据库", "教程"],
            status_name="published"
        )
        blog1_id = blog1.id
        print(f"✓ 创建博客1: Python数据库操作教程 (ID: {blog1_id})")
        
        blog2 = table_ops.create_blog(
            title="我的编程学习心得",
            content="分享一些编程学习的心得体会...\n\n学习编程需要持之以恒...",
            summary="编程学习经验分享",
            category_name="生活",
            authors=["张三"],
            tags=["教程"],
            status_name="draft"
        )
        blog2_id = blog2.id
        print(f"✓ 创建博客2: 我的编程学习心得 (ID: {blog2_id})")
        
        # 4. 查询操作测试
        print("\n4. 测试博客查询操作...")
        
        # 根据ID查询
        found_blog = table_ops.get_blog_by_id(blog1_id)
        print(f"✓ 根据ID查询博客: {'找到' if found_blog else '未找到'}")
        
        # 根据分类查询
        tech_blogs = table_ops.get_blogs_by_category("技术")
        print(f"✓ 技术分类下的博客数量: {len(tech_blogs)}")
        
        # 根据标签查询
        python_blogs = table_ops.get_blogs_by_tag("Python")
        print(f"✓ Python标签下的博客数量: {len(python_blogs)}")
        
        # 根据作者查询
        zhang_blogs = table_ops.get_blogs_by_author("张三")
        print(f"✓ 张三的博客数量: {len(zhang_blogs)}")
        
        # 获取所有博客
        all_blogs = table_ops.get_all_blogs()
        print(f"✓ 总博客数量: {len(all_blogs)}")
        
        # 按状态查询
        published_blogs = table_ops.get_all_blogs("published")
        print(f"✓ 已发布博客数量: {len(published_blogs)}")
        
        # 5. 更新操作测试
        print("\n5. 测试更新操作...")
        
        updated_blog = table_ops.update_blog(
            blog2_id,
            title="114514",
            status_name="published",
            tags=["教程", "Python"]
        )
        print(f"✓ 更新博客: {'成功' if updated_blog else '失败'}")
        
        # 6. 统计信息
        print("\n6. 获取统计信息...")
        stats = table_ops.get_statistics()
        print("✓ 数据库统计信息:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # 7. 测试所有列表查询
        print("\n7. 测试列表查询...")
        
        categories = table_ops.get_all_categories()
        print(f'获取所有分类:{categories}')
        print(f"第一个分类的ID: {categories[0].id}")
        print(f"第一个分类的名称: {categories[0].category}")
        print(f"✓ 所有分类数量: {len(categories)}")
        
        tags = table_ops.get_all_tags()
        print(f"✓ 所有标签数量: {len(tags)}")
        
        authors = table_ops.get_all_authors()
        print(f"✓ 所有作者数量: {len(authors)}")
        
        statuses = table_ops.get_all_statuses()
        print(f"✓ 所有状态数量: {len(statuses)}")
        
        # # 8. 测试删除操作
        # print("\n8. 测试删除操作...")
        
        # # 删除博客
        # delete_result = table_ops.delete_blog(blog2_id)
        # print(f"✓ 删除博客结果: {'成功' if delete_result else '失败'}")
        
        # 验证删除
        remaining_blogs = table_ops.get_all_blogs()
        print(f"✓ 删除后剩余博客数量: {len(remaining_blogs)}")
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    test_database_operations()
    