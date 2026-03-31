# ── Build stage ──────────────────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
# Crée le dossier fiches s'il n'existe pas (build sans fiches possible)
RUN mkdir -p public/fiches
RUN npm run build

# ── Production stage ─────────────────────────────────────────
FROM node:20-slim AS runner

WORKDIR /app

RUN npm install -g http-server

COPY --from=builder /app/dist ./dist

EXPOSE 4321

CMD ["http-server", "dist", "-p", "4321", "--cors", "-c-1", "--index", "index.html"]
