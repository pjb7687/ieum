FROM node:23 AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

COPY package.json /app/
RUN pnpm install

COPY . /app/

# Accept build argument and set as environment variable for Vite build
ARG GOOGLE_MAPS_API_KEY
ENV GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY

RUN pnpm run build

CMD ["bash", "run_server.sh"]