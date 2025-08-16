"""
博客同步工具示例脚本
演示如何使用 BlogSync 进行 Markdown 文件与数据库的同步
"""
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib_blog_sync import BlogSync
from lib_database import TableOperations

def main():
    """
    主函数：演示博客同步的完整流程
    """
    print("=== 博客同步工具示例 ===")
    
    # 配置参数
    file_path       = Path(__file__).resolve()
    current_path    = file_path.parent
    parent_path     = current_path.parent
    blog_directory  = parent_path / "blog/blog"
    database_file   = current_path / "example_blog.db"
    database_url    = f"sqlite:///{database_file}"
    
    print(f"博客目录: {blog_directory}")
    print(f"数据库文件: {database_file}")
    
    # 检查博客目录是否存在
    if not os.path.exists(blog_directory):
        print(f"错误: 博客目录不存在: {blog_directory}")
        print("请修改 blog_directory 变量为正确的路径")
        return
    
    # 创建同步工具实例
    sync_tool = BlogSync(blog_directory, database_url)
    table_ops = TableOperations(database_url)
    
    try:
        # 步骤1: 预演同步（不实际修改数据库）
        print("\n=== 步骤1: 预演同步 ===")
        print("正在扫描文件并分析同步需求...")
        
        dry_run_stats = sync_tool.sync_to_database(dry_run=True)
        
        print("\n预演结果:")
        print(f"  发现文件总数: {dry_run_stats['total_files']}")
        print(f"  需要新增: {dry_run_stats['new_files']} 个")
        print(f"  需要更新: {dry_run_stats['updated_files']} 个")
        print(f"  无需变化: {dry_run_stats['skipped_files']} 个")
        print(f"  处理失败: {dry_run_stats['failed_files']} 个")
        print(f"  失去同步: {dry_run_stats['lost_sync_files']} 个")
        
        # 询问用户是否继续
        if dry_run_stats['total_files'] == 0:
            print("\n没有找到任何 Markdown 文件，请检查目录路径。")
            return
        
        print("\n是否继续执行实际同步？(y/n): ", end="")
        user_input = input().strip().lower()
        
        if user_input not in ['y', 'yes', '是', '确定']:
            print("同步已取消。")
            return
        
        # 步骤2: 执行实际同步
        print("\n=== 步骤2: 执行实际同步 ===")
        print("正在同步文件到数据库...")
        
        real_stats = sync_tool.sync_to_database(dry_run=False)
        
        print("\n同步完成！结果统计:")
        print(f"  处理文件总数: {real_stats['total_files']}")
        print(f"  新增博客: {real_stats['new_files']} 篇")
        print(f"  更新博客: {real_stats['updated_files']} 篇")
        print(f"  跳过文件: {real_stats['skipped_files']} 个")
        print(f"  处理失败: {real_stats['failed_files']} 个")
        print(f"  失去同步: {real_stats['lost_sync_files']} 篇")
        
        # 步骤3: 显示数据库统计信息
        print("\n=== 步骤3: 数据库统计信息 ===")
        try:
            db_stats = table_ops.get_statistics()
            print("数据库当前状态:")
            print(f"  博客总数: {db_stats['total_blogs']}")
            print(f"  分类数量: {db_stats['total_categories']}")
            print(f"  标签数量: {db_stats['total_tags']}")
            print(f"  作者数量: {db_stats['total_authors']}")
            print(f"  状态类型: {db_stats['total_statuses']}")
            
            # 按状态统计
            if 'blogs_by_status' in db_stats:
                print("\n按状态分布:")
                for status, count in db_stats['blogs_by_status'].items():
                    print(f"  {status}: {count} 篇")
            
            # 按分类统计（只显示前5个）
            if 'blogs_by_category' in db_stats:
                print("\n主要分类分布:")
                categories = list(db_stats['blogs_by_category'].items())
                for category, count in categories[:5]:
                    print(f"  {category}: {count} 篇")
                if len(categories) > 5:
                    print(f"  ... 还有 {len(categories) - 5} 个分类")
                    
        except Exception as e:
            print(f"获取数据库统计信息失败: {e}")
        
        # 步骤4: 检查失去同步的博客
        if real_stats['lost_sync_files'] > 0:
            print("\n=== 步骤4: 失去同步的博客 ===")
            try:
                lost_blogs = table_ops.get_blogs_by_status('lost_sync')
                print(f"发现 {len(lost_blogs)} 篇博客失去同步（源文件可能已删除）:")
                for i, blog in enumerate(lost_blogs[:10], 1):  # 只显示前10个
                    print(f"  {i}. {blog.title}")
                if len(lost_blogs) > 10:
                    print(f"  ... 还有 {len(lost_blogs) - 10} 篇")
                    
                print("\n建议: 检查这些博客是否需要删除或恢复源文件。")
            except Exception as e:
                print(f"检查失去同步的博客时出错: {e}")
        
        print("\n=== 同步完成 ===")
        print(f"数据库文件已保存为: {database_file}")
        print("您可以使用数据库管理工具查看同步结果。")
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作。")
    except Exception as e:
        print(f"\n同步过程中发生错误: {e}")
        print("请检查文件路径、权限设置和文件格式。")

def quick_sync(blog_dir: str, db_file: str = "quick_blog.db"):
    """
    快速同步函数 - 适合脚本调用
    
    Args:
        blog_dir: Markdown文件目录
        db_file: 数据库文件名
    
    Returns:
        同步统计信息字典
    """
    sync_tool = BlogSync(blog_dir, f"sqlite:///{db_file}")
    return sync_tool.sync_to_database(dry_run=False)

if __name__ == "__main__":
    # 如果直接运行此脚本，执行交互式同步
    main()
    
    # 如果要在其他脚本中调用，可以使用:
    # from example_sync import quick_sync
    # stats = quick_sync("/path/to/blog", "my_blog.db")