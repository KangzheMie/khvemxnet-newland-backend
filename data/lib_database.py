from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
import hashlib

Base = declarative_base()

# 多对多关系表
blog_tags = Table('blog_tags', Base.metadata,
    Column('blog_id', Integer, ForeignKey('blogs.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

blog_authors = Table('blog_authors', Base.metadata,
    Column('blog_id', Integer, ForeignKey('blogs.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)

class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text)
    content = Column(Text, nullable=False)
    created_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    hash = Column(String(64), unique=True)  # MD5 hash of file content
    
    # 外键关系
    category_id = Column(Integer, ForeignKey('categories.id'))
    status_id = Column(Integer, ForeignKey('status.id'))
    
    # 关系映射
    category = relationship("Category", back_populates="blogs")
    status = relationship("Status", back_populates="blogs")
    tags = relationship("Tag", secondary=blog_tags, back_populates="blogs")
    authors = relationship("Author", secondary=blog_authors, back_populates="blogs")
    
    def __repr__(self):
        return f"<Blog(id={self.id}, title='{self.title}')>"

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), unique=True, nullable=False)
    
    # 关系映射
    blogs = relationship("Blog", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, category='{self.category}')>"

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(100), unique=True, nullable=False)
    
    # 关系映射
    blogs = relationship("Blog", secondary=blog_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, tag='{self.tag}')>"

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String(100), unique=True, nullable=False)
    
    # 关系映射
    blogs = relationship("Blog", secondary=blog_authors, back_populates="authors")
    
    def __repr__(self):
        return f"<Author(id={self.id}, author='{self.author}')>"

class Status(Base):
    __tablename__ = 'status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), unique=True, nullable=False)
    
    # 关系映射
    blogs = relationship("Blog", back_populates="status")
    
    def __repr__(self):
        return f"<Status(id={self.id}, status='{self.status}')>"

class DatabaseManager:
    """数据库管理类，提供数据库连接和会话管理"""
    
    def __init__(self, database_url='sqlite:///blog.db'):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = None
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)
        print("数据库表创建成功！")
    
    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)
        print("数据库表删除成功！")
    
    def get_session(self):
        """获取数据库会话"""
        if self.session is None:
            self.session = self.SessionLocal()
        return self.session
    
    def close_session(self):
        """关闭数据库会话"""
        if self.session:
            self.session.close()
            self.session = None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self.get_session()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.close_session()

def calculate_file_hash(content):
    """计算文件内容的MD5哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# 便捷函数
def create_database(database_url='sqlite:///blog.db'):
    """创建数据库和所有表"""
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    return db_manager

def get_or_create_category(session, category_name):
    """获取或创建分类"""
    category = session.query(Category).filter_by(category=category_name).first()
    if not category:
        category = Category(category=category_name)
        session.add(category)
        session.flush()  # 获取ID但不提交
        session.expunge(category)  # 从会话中分离对象
    return category

def get_or_create_tag(session, tag_name):
    """获取或创建标签"""
    tag = session.query(Tag).filter_by(tag=tag_name).first()
    if not tag:
        tag = Tag(tag=tag_name)
        session.add(tag)
        session.flush()
        session.expunge(tag)  # 从会话中分离对象
    return tag

def get_or_create_author(session, author_name):
    """获取或创建作者"""
    author = session.query(Author).filter_by(author=author_name).first()
    if not author:
        author = Author(author=author_name)
        session.add(author)
        session.flush()
        session.expunge(author)  # 从会话中分离对象
    return author

def get_or_create_status(session, status_name):
    """获取或创建状态"""
    status = session.query(Status).filter_by(status=status_name).first()
    if not status:
        status = Status(status=status_name)
        session.add(status)
        session.flush()
        session.expunge(status)  # 从会话中分离对象
    return status


class TableOperations:
    """数据库表操作类，提供各种CRUD操作"""
    
    def __init__(self, database_url='sqlite:///blog.db'):
        self.db_manager = DatabaseManager(database_url)
    
    def create_tables(self):
        """创建所有数据库表"""
        self.db_manager.create_tables()
    
    def drop_tables(self):
        """删除所有数据库表"""
        self.db_manager.drop_tables()
    
    # ==================== Blog 操作 ====================
    
    def create_blog(self, title: str, content: str, summary: str = None, 
                   category_name: str = None, authors: List[str] = None, 
                   tags: List[str] = None, status_name: str = "published",
                   created_time: datetime = None, updated_time: datetime = None) -> Blog:
        """创建新的博客文章"""
        with self.db_manager as session:
            # 计算内容哈希
            content_hash = calculate_file_hash(content)
            
            # 检查是否已存在相同哈希的文章
            existing_blog = session.query(Blog).filter_by(hash=content_hash).first()
            if existing_blog:
                raise ValueError(f"具有相同内容的博客已存在: {existing_blog.title}")
            
            # 创建博客对象
            blog = Blog(
                title=title,
                content=content,
                summary=summary or "",
                hash=content_hash,
                created_time=created_time or datetime.now(timezone.utc),
                updated_time=updated_time or datetime.now(timezone.utc)
            )
            
            # 设置分类
            if category_name:
                blog.category = get_or_create_category(session, category_name)
            
            # 设置状态
            blog.status = get_or_create_status(session, status_name)
            
            # 设置作者
            if authors:
                for author_name in authors:
                    author = get_or_create_author(session, author_name)
                    blog.authors.append(author)
            
            # 设置标签
            if tags:
                for tag_name in tags:
                    tag = get_or_create_tag(session, tag_name)
                    blog.tags.append(tag)
            
            session.add(blog)
            session.flush()
            session.expunge(blog)  # 从会话中分离对象
            return blog
    
    def get_blog_by_id(self, blog_id: int) -> Optional[Blog]:
        """根据ID获取博客"""
        with self.db_manager as session:
            blog = session.query(Blog).filter_by(id=blog_id).first()
            if blog:
                session.expunge(blog)
            return blog
    
    def get_blog_by_hash(self, content_hash: str) -> Optional[Blog]:
        """根据哈希值获取博客"""
        with self.db_manager as session:
            blog = session.query(Blog).filter_by(hash=content_hash).first()
            if blog:
                session.expunge(blog)
            return blog
    
    def get_blog_by_title(self, title: str) -> Optional[Blog]:
        """根据标题获取博客"""
        with self.db_manager as session:
            blog = session.query(Blog).filter_by(title=title).first()
            if blog:
                session.expunge(blog)
            return blog
    
    def get_blogs_by_category(self, category_name: str) -> List[Blog]:
        """根据分类获取博客列表"""
        with self.db_manager as session:
            category = session.query(Category).filter_by(category=category_name).first()
            if category:
                return category.blogs
            return []
    
    def get_blogs_by_tag(self, tag_name: str) -> List[Blog]:
        """根据标签获取博客列表"""
        with self.db_manager as session:
            tag = session.query(Tag).filter_by(tag=tag_name).first()
            if tag:
                return tag.blogs
            return []
    
    def get_blogs_by_author(self, author_name: str) -> List[Blog]:
        """根据作者获取博客列表"""
        with self.db_manager as session:
            author = session.query(Author).filter_by(author=author_name).first()
            if author:
                return author.blogs
            return []
    
    def get_all_blogs(self, status_name: str = None) -> List[Blog]:
        """获取所有博客，可按状态筛选"""
        with self.db_manager as session:
            query = session.query(Blog)
            if status_name:
                status = session.query(Status).filter_by(status=status_name).first()
                if status:
                    query = query.filter_by(status_id=status.id)
            blogs = query.all()
            for blog in blogs:
                session.expunge(blog)
            return blogs
    
    def get_blogs_by_status(self, status_name: str) -> List[Blog]:
        """根据状态获取博客列表"""
        with self.db_manager as session:
            status = session.query(Status).filter_by(status=status_name).first()
            if status:
                blogs = session.query(Blog).filter_by(status_id=status.id).all()
                for blog in blogs:
                    session.expunge(blog)
                return blogs
            return []
    
    def update_blog(self, blog_id: int, **kwargs) -> Optional[Blog]:
        """更新博客信息"""
        with self.db_manager as session:
            blog = session.query(Blog).filter_by(id=blog_id).first()
            if not blog:
                return None
            
            # 更新基本字段
            for key, value in kwargs.items():
                if key in ['title', 'content', 'summary']:
                    setattr(blog, key, value)
                    if key == 'content':
                        blog.hash = calculate_file_hash(value)
                elif key == 'category_name':
                    blog.category = get_or_create_category(session, value)
                elif key == 'status_name':
                    blog.status = get_or_create_status(session, value)
                elif key == 'authors':
                    blog.authors.clear()
                    for author_name in value:
                        author = get_or_create_author(session, author_name)
                        blog.authors.append(author)
                elif key == 'tags':
                    blog.tags.clear()
                    for tag_name in value:
                        tag = get_or_create_tag(session, tag_name)
                        blog.tags.append(tag)
            
            blog.updated_time = datetime.now(timezone.utc)
            session.commit()
            session.expunge(blog)
            return blog
    
    def update_blog_status(self, blog_id: int, status_name: str) -> Optional[Blog]:
        """更新博客状态"""
        with self.db_manager as session:
            blog = session.query(Blog).filter_by(id=blog_id).first()
            if not blog:
                return None
            
            blog.status = get_or_create_status(session, status_name)
            blog.updated_time = datetime.now(timezone.utc)
            session.commit()
            session.expunge(blog)
            return blog
    
    def delete_blog(self, blog_id: int) -> bool:
        """删除博客"""
        with self.db_manager as session:
            blog = session.query(Blog).filter_by(id=blog_id).first()
            if blog:
                session.delete(blog)
                return True
            return False
    
    # ==================== Category 操作 ====================
    
    def create_category(self, category_name: str) -> Category:
        """创建新分类"""
        with self.db_manager as session:
            category = get_or_create_category(session, category_name)
            return category
    
    def get_all_categories(self) -> List[Category]:
        """获取所有分类"""
        with self.db_manager as session:
            categories = session.query(Category).all()
            for category in categories:
                session.expunge(category)
            return categories
    
    def update_category(self, category_id: int, new_name: str) -> Optional[Category]:
        """更新分类名称"""
        with self.db_manager as session:
            category = session.query(Category).filter_by(id=category_id).first()
            if category:
                category.category = new_name
                session.expunge(category)
                return category
            return None
    
    def delete_category(self, category_id: int) -> bool:
        """删除分类（需要先处理关联的博客）"""
        with self.db_manager as session:
            category = session.query(Category).filter_by(id=category_id).first()
            if category:
                # 检查是否有关联的博客
                if category.blogs:
                    raise ValueError(f"无法删除分类 '{category.category}'，因为还有 {len(category.blogs)} 篇博客使用此分类")
                session.delete(category)
                return True
            return False
    
    # ==================== Tag 操作 ====================
    
    def create_tag(self, tag_name: str) -> Tag:
        """创建新标签"""
        with self.db_manager as session:
            tag = get_or_create_tag(session, tag_name)
            return tag
    
    def get_all_tags(self) -> List[Tag]:
        """获取所有标签"""
        with self.db_manager as session:
            tags = session.query(Tag).all()
            for tag in tags:
                session.expunge(tag)
            return tags
    
    def update_tag(self, tag_id: int, new_name: str) -> Optional[Tag]:
        """更新标签名称"""
        with self.db_manager as session:
            tag = session.query(Tag).filter_by(id=tag_id).first()
            if tag:
                tag.tag = new_name
                session.expunge(tag)
                return tag
            return None
    
    def delete_tag(self, tag_id: int) -> bool:
        """删除标签"""
        with self.db_manager as session:
            tag = session.query(Tag).filter_by(id=tag_id).first()
            if tag:
                session.delete(tag)
                return True
            return False
    
    # ==================== Author 操作 ====================
    
    def create_author(self, author_name: str) -> Author:
        """创建新作者"""
        with self.db_manager as session:
            author = get_or_create_author(session, author_name)
            return author
    
    def get_all_authors(self) -> List[Author]:
        """获取所有作者"""
        with self.db_manager as session:
            authors = session.query(Author).all()
            for author in authors:
                session.expunge(author)
            return authors
    
    def update_author(self, author_id: int, new_name: str) -> Optional[Author]:
        """更新作者名称"""
        with self.db_manager as session:
            author = session.query(Author).filter_by(id=author_id).first()
            if author:
                author.author = new_name
                session.expunge(author)
                return author
            return None
    
    def delete_author(self, author_id: int) -> bool:
        """删除作者"""
        with self.db_manager as session:
            author = session.query(Author).filter_by(id=author_id).first()
            if author:
                session.delete(author)
                return True
            return False
    
    # ==================== Status 操作 ====================
    
    def create_status(self, status_name: str) -> Status:
        """创建新状态"""
        with self.db_manager as session:
            status = get_or_create_status(session, status_name)
            return status
    
    def get_all_statuses(self) -> List[Status]:
        """获取所有状态"""
        with self.db_manager as session:
            statuses = session.query(Status).all()
            for status in statuses:
                session.expunge(status)
            return statuses
    
    def update_status(self, status_id: int, new_name: str) -> Optional[Status]:
        """更新状态名称"""
        with self.db_manager as session:
            status = session.query(Status).filter_by(id=status_id).first()
            if status:
                status.status = new_name
                session.expunge(status)
                return status
            return None
    
    def delete_status(self, status_id: int) -> bool:
        """删除状态（需要先处理关联的博客）"""
        with self.db_manager as session:
            status = session.query(Status).filter_by(id=status_id).first()
            if status:
                # 检查是否有关联的博客
                if status.blogs:
                    raise ValueError(f"无法删除状态 '{status.status}'，因为还有 {len(status.blogs)} 篇博客使用此状态")
                session.delete(status)
                return True
            return False
    
    # ==================== 统计信息 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        with self.db_manager as session:
            stats = {
                'total_blogs': session.query(Blog).count(),
                'total_categories': session.query(Category).count(),
                'total_tags': session.query(Tag).count(),
                'total_authors': session.query(Author).count(),
                'total_statuses': session.query(Status).count(),
            }
            
            # 按状态统计博客数量
            status_stats = {}
            for status in session.query(Status).all():
                status_stats[status.status] = len(status.blogs)
            stats['blogs_by_status'] = status_stats
            
            # 按分类统计博客数量
            category_stats = {}
            for category in session.query(Category).all():
                category_stats[category.category] = len(category.blogs)
            stats['blogs_by_category'] = category_stats
            
            return stats

if __name__ == "__main__":
    # 示例用法
    db_manager = create_database()
    
    with db_manager as session:
        # 创建一些基础数据
        default_status = get_or_create_status(session, "published")
        draft_status = get_or_create_status(session, "draft")
        
        print("数据库初始化完成！")
        print(f"默认状态: {default_status}")
        print(f"草稿状态: {draft_status}")

    # 示例用法
    table_ops = TableOperations()
    table_ops.create_tables()
    
    # 获取统计信息
    stats = table_ops.get_statistics()
    print("数据库统计信息:")
    for key, value in stats.items():
        print(f"{key}: {value}")