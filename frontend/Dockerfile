# Development Dockerfile - Optimized for fast rebuilds
FROM node:20.0.0-alpine AS base

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache libc6-compat bash curl

# Install dependencies based on the preferred package manager
FROM base AS deps
COPY package.json package-lock.json* ./
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Development image
FROM base AS dev
WORKDIR /app

# Create user for development
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy node_modules with proper ownership
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

# Ensure nextjs user owns the app directory
RUN chown -R nextjs:nodejs /app

# Switch to nextjs user
USER nextjs

# Expose port for the development server
EXPOSE 3000

# Set environment to development
ENV NODE_ENV development
ENV NEXT_TELEMETRY_DISABLED 1

# Run the development server with polling for Docker
CMD ["npm", "run", "dev"]
