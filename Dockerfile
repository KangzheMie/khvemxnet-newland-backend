# ---- Builder Stage ----
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 配置Alpine镜像源为阿里云镜像（提高下载速度）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 更新包索引并安装系统依赖（分步骤安装以提高成功率）
RUN apk update && \
    apk add --no-cache --timeout=300 \
    build-base \
    musl-dev && \
    apk add --no-cache --timeout=300 \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    giflib-dev \
    pixman-dev \
    pangomm-dev \
    libjpeg-turbo-dev \
    freetype-dev

# 复制package.json和package-lock.json
COPY backend/package*.json ./

# 配置npm使用淘宝镜像源（提高下载速度）
RUN npm config set registry https://registry.npmmirror.com

# 安装所有依赖
RUN npm install --production=false

# 复制源代码（只复制backend目录内容）
COPY backend/ .

# 构建应用
ENV NODE_OPTIONS=--max-old-space-size=4096
RUN npm run build

# 编译TypeScript配置文件为JavaScript
RUN npx tsc config/admin.ts --outDir dist/config --module commonjs --target es2019 --esModuleInterop --skipLibCheck || true
RUN npx tsc config/api.ts --outDir dist/config --module commonjs --target es2019 --esModuleInterop --skipLibCheck || true
RUN npx tsc config/database.ts --outDir dist/config --module commonjs --target es2019 --esModuleInterop --skipLibCheck || true
RUN npx tsc config/middlewares.ts --outDir dist/config --module commonjs --target es2019 --esModuleInterop --skipLibCheck || true
RUN npx tsc config/plugins.ts --outDir dist/config --module commonjs --target es2019 --esModuleInterop --skipLibCheck || true
RUN npx tsc config/server.ts --outDir dist/config --module commonjs --target es2019 --esModuleInterop --skipLibCheck || true

# ---- Production Stage ----
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 配置Alpine镜像源为阿里云镜像
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 安装生产环境系统依赖（分步骤安装）
RUN apk update && \
    apk add --no-cache --timeout=300 \
    cairo \
    jpeg \
    pango \
    giflib \
    pixman \
    pangomm \
    libjpeg-turbo \
    freetype \
    curl

# 关键修复：从builder阶段复制依赖清单
COPY --from=builder /app/package*.json ./

# 关键修复：从builder阶段复制整个node_modules
COPY --from=builder /app/node_modules ./node_modules

# 从builder阶段复制构建产物
COPY --from=builder /app/dist ./dist
# 复制编译后的JavaScript配置文件
COPY --from=builder /app/dist/config ./config
COPY --from=builder /app/database ./database
COPY --from=builder /app/public ./public
COPY --from=builder /app/src ./src

# Strapi 5.x需要JavaScript配置文件，已在构建阶段编译

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S strapi -u 1001

# 设置文件权限 (确保在USER切换前完成)
RUN chown -R strapi:nodejs /app
USER strapi

EXPOSE 1337

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:1337/_health || exit 1

CMD ["npm", "start"]