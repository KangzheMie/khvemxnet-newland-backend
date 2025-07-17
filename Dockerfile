# ---- Builder Stage ----
FROM node:20-alpine AS builder

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
    freetype-dev

# 复制package.json和package-lock.json
COPY backend/package*.json ./

# 安装所有依赖
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# ---- Production Stage ----
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 安装生产环境系统依赖
RUN apk add --no-cache \
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
COPY --from=builder /app/config ./config
COPY --from=builder /app/database ./database
COPY --from=builder /app/public ./public
COPY --from=builder /app/src ./src

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