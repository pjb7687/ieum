FROM node:23 AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

COPY package.json /app/
RUN pnpm install

COPY . /app/
RUN pnpm run build

CMD ["bash", "run_server.sh"]