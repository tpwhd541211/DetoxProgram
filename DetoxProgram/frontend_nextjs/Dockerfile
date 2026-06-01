FROM node:18-alpine

WORKDIR /app

# Install dependencies first (to leverage Docker caching)
COPY package*.json ./
RUN npm install

# Copy application source
COPY . .

# Expose Next.js default port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]
