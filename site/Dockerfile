# ── Build stage ──────────────────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN mkdir -p public/fiches

ARG SITE_BASE=""
ENV SITE_BASE=$SITE_BASE

RUN npm run build

# ── Production stage ─────────────────────────────────────────
FROM node:20-slim AS runner

WORKDIR /app

RUN npm install -g http-server

COPY --from=builder /app/dist ./dist

EXPOSE 4321

CMD ["http-server", "dist", "-p", "4321", "--cors", "-c-1", "--index", "index.html"]
