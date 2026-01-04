FROM pandoc/latex:latest

# 安装 Node.js（alpine 系镜像常用 apk；如果将来你发现该镜像不是 alpine，再告诉我我给你换成 apt-get 版本）
RUN apk add --no-cache nodejs npm

WORKDIR /app

COPY package.json .
RUN npm install --omit=dev

COPY server.js .

# Zeabur 需要暴露端口
EXPOSE 3000

CMD ["node", "server.js"]
