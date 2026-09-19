# Multi-stage Dockerfile for React TypeScript Frontend

# Stage 1: Build static assets
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build production bundle
COPY . .
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build

# Stage 2: Serve with NGINX
FROM nginx:alpine AS runner
WORKDIR /usr/share/nginx/html

# Remove default NGINX static assets
RUN rm -rf ./*

# Copy built assets from builder stage
COPY --from=builder /app/dist .

# Copy custom NGINX default server configuration if needed
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
