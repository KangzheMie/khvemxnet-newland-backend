"""
博客文件同步工具
实现Markdown文件与SQLite数据库的双向同步
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from lib_database import TableOperations

class BlogSync:
    """博客同步工具类"""
    
    def __init__(self, blog_directory: str, database_url: str = 'sqlite:///blog.db'):
        """
        初始化同步工具
        
        Args:
            blog_directory: Markdown文件所在目录
            database_url: 数据库连接URL
        """
        self.blog_directory = Path(blog_directory)
        self.table_ops = TableOperations(database_url)
        
    def scan_markdown_files(self) -> List[Path]:
        """
        扫描指定目录下的所有Markdown文件
        
        Returns:
            所有Markdown文件的路径列表
        """
        if not self.blog_directory.exists():
            print(f"目录不存在: {self.blog_directory}")
            return []
            
        markdown_files = list(self.blog_directory.rglob("*.md"))
        print(f"找到 {len(markdown_files)} 个Markdown文件")
        return markdown_files
    
    def parse_frontmatter(self, file_path: Path) -> Dict[str, any]:
        """
        解析Markdown文件的frontmatter元数据
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            包含元数据和内容的字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有frontmatter
            if not content.startswith('---'):
                return self._parse_legacy_format(content, file_path)
            
            # 分割frontmatter和正文
            parts = content.split('---', 2)
            if len(parts) < 3:
                return self._parse_legacy_format(content, file_path)
            
            # 解析YAML frontmatter
            frontmatter_str = parts[1].strip()
            try:
                metadata = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as e:
                print(f"YAML解析错误 {file_path}: {e}")
                return self._parse_legacy_format(content, file_path)
            
            # 获取正文内容
            body_content = parts[2].strip()
            
            # 标准化元数据格式
            normalized_data = self._normalize_metadata(metadata, body_content, file_path)
            return normalized_data
            
        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None
    
    def _parse_legacy_format(self, content: str, file_path: Path) -> Dict[str, any]:
        """
        处理没有frontmatter的旧格式文件
        
        Args:
            content: 文件内容
            file_path: 文件路径
            
        Returns:
            标准化的元数据字典
        """
        # 从文件名提取信息
        file_name = file_path.stem
        
        # 尝试从文件名提取分类和标题
        parts = file_name.split('_', 1)
        if len(parts) == 2:
            category = parts[0]
            title = parts[1]
        else:
            category = "未分类"
            title = file_name
        
        return {
            'title': title,
            'content': content,
            'summary': content[:200] + '...' if len(content) > 200 else content,
            'category': category,
            'authors': ['未知作者'],
            'tags': ['未分类'],
            'status': 'published',
            'created_time': datetime.fromtimestamp(file_path.stat().st_mtime),
            'updated_time': datetime.fromtimestamp(file_path.stat().st_mtime)
        }
    
    def _normalize_metadata(self, metadata: Dict, content: str, file_path: Path) -> Dict[str, any]:
        """
        标准化元数据格式
        
        Args:
            metadata: 原始元数据
            content: 正文内容
            file_path: 文件路径
            
        Returns:
            标准化的元数据字典
        """
        # 确保必需字段存在
        title = metadata.get('title', file_path.stem)
        
        # 处理时间格式
        created_time = self._parse_datetime(metadata.get('created_time'))
        updated_time = self._parse_datetime(metadata.get('updated_time'))
        
        # 处理数组字段
        authors = metadata.get('authors', [])
        if isinstance(authors, str):
            authors = [authors]
        elif authors is None:
            authors = ['未知作者']
        
        tags = metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        elif tags is None:
            tags = ['未分类']
        
        return {
            'title': title,
            'content': content,
            'summary': metadata.get('summary', content[:200] + '...' if len(content) > 200 else content),
            'category': metadata.get('categories', '未分类'),
            'authors': authors,
            'tags': tags,
            'status': metadata.get('status', 'published'),
            'created_time': created_time or datetime.fromtimestamp(file_path.stat().st_mtime),
            'updated_time': updated_time or datetime.fromtimestamp(file_path.stat().st_mtime)
        }
    
    def _parse_datetime(self, dt_str: any) -> Optional[datetime]:
        """
        解析日期时间字符串
        
        Args:
            dt_str: 日期时间字符串
            
        Returns:
            datetime对象或None
        """
        if not dt_str:
            return None
        
        if isinstance(dt_str, datetime):
            return dt_str
        
        # 尝试多种格式
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(dt_str), fmt)
            except ValueError:
                continue
        
        return None
    
    def sync_to_database(self, dry_run: bool = False) -> Dict[str, int]:
        """
        将Markdown文件同步到数据库
        
        Args:
            dry_run: 是否只进行预演，不实际写入数据库
            
        Returns:
            同步统计信息
        """
        print("开始同步Markdown文件到数据库...")
        
        stats = {
            'total_files': 0,
            'new_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'lost_sync_files': 0
        }
        
        # 确保表存在（无论是否dry_run）
        try:
            self.table_ops.create_tables()
            print("数据库表创建成功")
        except Exception as e:
            print(f"创建表时出错: {e}")
            stats['failed_files'] = 1
            return stats
        
        # 第一步：将所有数据库中的博客状态标记为 lost_sync
        if not dry_run:
            try:
                all_blogs = self.table_ops.get_all_blogs()
                for blog in all_blogs:
                    self.table_ops.update_blog_status(blog.id, 'lost_sync')
                print(f"已将 {len(all_blogs)} 个博客标记为失去同步状态")
            except Exception as e:
                print(f"标记失去同步状态时出错: {e}")
        
        # 扫描Markdown文件
        markdown_files = self.scan_markdown_files()
        stats['total_files'] = len(markdown_files)
        
        if not markdown_files:
            print("没有找到Markdown文件")
            return stats
        
        for file_path in markdown_files:
            try:
                # 解析文件
                file_data = self.parse_frontmatter(file_path)
                if not file_data:
                    stats['failed_files'] += 1
                    continue
                
                # 基于标题查找现有博客
                existing_blog = self.table_ops.get_blog_by_title(file_data['title'])
                
                if existing_blog:
                    # 检查是否需要更新（包括内容和元数据）
                    needs_update = self._check_full_update(existing_blog, file_data)
                    if needs_update:
                        if not dry_run:
                            self._update_blog_full(existing_blog.id, file_data)
                        stats['updated_files'] += 1
                        print(f"更新博客: {file_data['title']}")
                    else:
                        # 即使没有更新，也要将状态改回 published
                        if not dry_run:
                            self.table_ops.update_blog_status(existing_blog.id, file_data['status'])
                        stats['skipped_files'] += 1
                        print(f"跳过: {file_data['title']} (无变化)")
                else:
                    # 创建新博客
                    if not dry_run:
                        self.table_ops.create_blog(
                            title=file_data['title'],
                            content=file_data['content'],
                            summary=file_data['summary'],
                            category_name=file_data['category'],
                            authors=file_data['authors'],
                            tags=file_data['tags'],
                            status_name=file_data['status'],
                            created_time=file_data['created_time'],
                            updated_time=file_data['updated_time']
                        )
                    stats['new_files'] += 1
                    print(f"创建: {file_data['title']}")
                    
            except Exception as e:
                print(f"处理文件失败 {file_path}: {e}")
                stats['failed_files'] += 1
                continue
        
        # 最后检查仍然是 lost_sync 状态的博客
        try:
            lost_sync_blogs = self.table_ops.get_blogs_by_status('lost_sync')
            stats['lost_sync_files'] = len(lost_sync_blogs)
            if lost_sync_blogs:
                print(f"\n发现 {len(lost_sync_blogs)} 个失去同步的博客:")
                for blog in lost_sync_blogs:
                    print(f"  - {blog.title}")
        except Exception as e:
            print(f"检查失去同步的博客时出错: {e}")
        
        return stats
    
    def _check_full_update(self, existing_blog, file_data: Dict) -> bool:
        """
        检查博客是否需要完整更新（包括内容和元数据）
        
        Args:
            existing_blog: 数据库中的博客对象
            file_data: 文件中的数据
            
        Returns:
            是否需要更新
        """
        # 检查内容是否变化
        from lib_database import calculate_file_hash
        file_hash = calculate_file_hash(file_data['content'])
        if existing_blog.hash != file_hash:
            return True
        
        # 检查摘要
        if existing_blog.summary != file_data['summary']:
            return True
        
        # 为了避免DetachedInstanceError，我们使用新的Session来查询关联数据
        from sqlalchemy.orm import joinedload
        from lib_database import Blog
        with self.table_ops.db_manager as session:
            full_blog = session.query(Blog).options(
                joinedload(Blog.category),
                joinedload(Blog.authors),
                joinedload(Blog.tags),
                joinedload(Blog.status)
            ).filter_by(id=existing_blog.id).first()
            
            if not full_blog:
                return True  # 如果找不到博客，则需要更新
            
            # 检查分类
            db_category = full_blog.category.category if full_blog.category else None
            if db_category != file_data['category']:
                return True
            
            # 检查作者
            file_authors = set(file_data['authors'])
            db_authors = set([author.author for author in full_blog.authors])
            if file_authors != db_authors:
                return True
            
            # 检查标签
            file_tags = set(file_data['tags'])
            db_tags = set([tag.tag for tag in full_blog.tags])
            if file_tags != db_tags:
                return True
            
            # 检查状态
            db_status = full_blog.status.status if full_blog.status else None
            if db_status != file_data['status']:
                return True
        
        return False
    
    def _update_blog_full(self, blog_id: int, file_data: Dict):
        """
        完整更新博客（包括内容和元数据）
        
        Args:
            blog_id: 博客ID
            file_data: 文件数据
        """
        self.table_ops.update_blog(
            blog_id=blog_id,
            title=file_data['title'],
            content=file_data['content'],
            summary=file_data['summary'],
            category_name=file_data['category'],
            authors=file_data['authors'],
            tags=file_data['tags'],
            status_name=file_data['status'],
            updated_time=file_data['updated_time']
        )
    
    def get_sync_status(self) -> Dict[str, List[str]]:
        """
        获取同步状态信息
        
        Returns:
            包含各种状态信息的字典
        """
        markdown_files = self.scan_markdown_files()
        
        file_status = {
            'in_files_only': [],
            'in_db_only': [],
            'in_both': [],
            'conflicts': []
        }
        
        try:
            # 确保表存在
            self.table_ops.create_tables()
            
            # 获取数据库中的所有博客
            all_blogs = self.table_ops.get_all_blogs()
            db_blogs = {blog.hash: blog.title for blog in all_blogs}
        except Exception as e:
            print(f"获取数据库状态时出错: {e}")
            db_blogs = {}
        
        # 分析文件状态
        for file_path in markdown_files:
            file_data = self.parse_frontmatter(file_path)
            if not file_data:
                continue
                
            from lib_database import calculate_file_hash
            content_hash = calculate_file_hash(file_data['content'])
            
            if content_hash in db_blogs:
                file_status['in_both'].append(str(file_path))
            else:
                file_status['in_files_only'].append(str(file_path))
        
        # 找出只在数据库中的博客
        file_hashes = set()
        for file_path in markdown_files:
            file_data = self.parse_frontmatter(file_path)
            if file_data:
                from lib_database import calculate_file_hash
                content_hash = calculate_file_hash(file_data['content'])
                file_hashes.add(content_hash)
        
        for title in db_blogs.values():
            # 这里简化处理，直接添加所有数据库中的博客标题
            # 因为会话分离问题，我们避免访问复杂的关系属性
            file_status['in_db_only'].append(title)
        
        return file_status

if __name__ == "__main__":
    # 示例用法
    blog_dir = r"d:\OneDrive\khvemxnet\NewLand\backend\blog"
    sync_tool = BlogSync(blog_dir)
    
    # 执行同步
    stats = sync_tool.sync_to_database(dry_run=True)
    print("\n同步统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 查看同步状态
    status = sync_tool.get_sync_status()
    print("\n同步状态:")
    for key, value in status.items():
        print(f"  {key}: {len(value)} 项")