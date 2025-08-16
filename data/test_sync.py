"""
测试新的博客同步逻辑
基于标题匹配和失去同步状态检测
"""

import os
import sys
from pathlib import Path
from lib_blog_sync import BlogSync
from lib_database import TableOperations

def main():
    print("=== 测试新的博客同步逻辑 ===")
    
    # 设置路径
    file_path       = Path(__file__).resolve()
    current_path    = file_path.parent
    parent_path     = current_path.parent
    blog_dir        = parent_path / "blog/blog"
    db_path         = current_path / "test_sync.db"

    # 删除旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已删除旧数据库: {db_path}")
    
    # 创建同步工具
    sync_tool = BlogSync(blog_dir, f'sqlite:///{db_path}')
    table_ops = TableOperations(f'sqlite:///{db_path}')
    
    print(f"\n博客目录: {blog_dir}")
    print(f"数据库: {db_path}")
    
    # 第一次同步（预演）
    print("\n=== 第一次同步（预演模式） ===")
    stats = sync_tool.sync_to_database(dry_run=True)
    print("\n预演统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 第一次实际同步
    print("\n=== 第一次实际同步 ===")
    stats = sync_tool.sync_to_database(dry_run=False)
    print("\n同步统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 查看数据库状态
    try:
        db_stats = table_ops.get_statistics()
        print("\n数据库统计:")
        for key, value in db_stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"获取数据库统计失败: {e}")
    
    # 第二次同步（应该没有变化）
    print("\n=== 第二次同步（应该没有变化） ===")
    stats = sync_tool.sync_to_database(dry_run=False)
    print("\n同步统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试失去同步的检测
    print("\n=== 测试失去同步检测 ===")
    print("手动删除一个博客来模拟失去同步...")
    
    try:
        # 获取第一个博客并删除
        all_blogs = table_ops.get_all_blogs()
        if all_blogs:
            first_blog = all_blogs[0]
            print(f"删除博客: {first_blog.title}")
            table_ops.delete_blog(first_blog.id)
            
            # 再次同步
            print("\n再次同步以检测失去同步的文件...")
            stats = sync_tool.sync_to_database(dry_run=False)
            print("\n同步统计:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"测试失去同步检测时出错: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()