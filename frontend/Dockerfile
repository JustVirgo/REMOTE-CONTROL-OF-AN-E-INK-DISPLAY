FROM node:18-alpine

WORKDIR /app

# Copy only package files first, install deps
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the source
COPY . ./

# Match the port in vite.config.js
EXPOSE 8080

ENV NODE_ENV=production

CMD ["npm", "run", "dev", "--", "--host"]
