# ========================================
# Builder stage for compiling the Next.js application
# ========================================
FROM node:18-alpine AS builder

WORKDIR /app

# Set environment to production for optimized build
ENV NODE_ENV=production

# Install dependencies required for Node.js
RUN apk add --no-cache libc6-compat

# Copy dependency definitions
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy application source code
COPY . .

# Build the Next.js application
RUN yarn build

# Prune development dependencies to reduce size
RUN yarn install --production --ignore-scripts --prefer-offline

# ========================================
# Development stage for local development with hot reloading
# ========================================
FROM node:18-alpine AS development

WORKDIR /app

# Set environment to development for enhanced debugging
ENV NODE_ENV=development

# Install dependencies required for Node.js
RUN apk add --no-cache libc6-compat

# Copy dependency definitions
COPY package.json yarn.lock ./

# Install all dependencies including development packages
RUN yarn install

# Copy application source
COPY . .

# Expose port for development server
EXPOSE 3000

# Start development server with hot reloading
CMD ["yarn", "dev"]

# ========================================
# Production stage optimized for serving the application
# ========================================
FROM nginx:alpine AS production

# Create Nginx configuration inline
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 3000;
    server_name _;

    root /usr/share/nginx/html;

    # Next.js static files
    location /_next/static {
        alias /usr/share/nginx/html/_next/static;
        expires 365d;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # Public assets
    location /public {
        alias /usr/share/nginx/html/public;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Handle other static assets
    location / {
        try_files $uri $uri.html $uri/index.html =404;
        expires 1d;
        add_header Cache-Control "public, max-age=86400";
    }

    # Error handling
    error_page 404 /404.html;
    location = /404.html {
        internal;
    }

    # Enable gzip compression
    gzip on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Copy built application from builder stage
COPY --from=builder /app/.next /usr/share/nginx/html
COPY --from=builder /app/public /usr/share/nginx/html/public

# Expose port for Nginx server
EXPOSE 3000

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]