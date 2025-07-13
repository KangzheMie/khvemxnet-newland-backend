# 使用官方Node.js 20 Alpine镜像作为基础镜像
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    build-base \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    musl-dev \
    giflib-dev \
    pixman-dev \
    pangomm-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    curl

# 复制package.json和package-lock.json
COPY package*.json ./

# 更新npm到最新版本并安装所有依赖
RUN npm install -g npm@latest && \
    npm install

# 复制源代码
COPY . .

# 创建上传目录
RUN mkdir -p public/uploads

# 构建应用并清理开发依赖
RUN npm run build && \
    npm ci --omit=dev && \
    npm cache clean --force

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S strapi -u 1001

# 设置文件权限
RUN chown -R strapi:nodejs /app
USER strapi

# 暴露端口
EXPOSE 1337

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:1337/_health || exit 1

# 启动应用
CMD ["npm", "start"]