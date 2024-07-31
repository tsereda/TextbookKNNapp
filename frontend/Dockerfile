FROM node:14

WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Debug: List contents after copying all files
RUN ls -la

# Debug: Check if rollup.config.js exists
RUN if [ -f rollup.config.js ]; then echo "rollup.config.js exists"; else echo "rollup.config.js does not exist"; fi

# Debug: Print the contents of rollup.config.js if it exists
RUN if [ -f rollup.config.js ]; then cat rollup.config.js; else echo "Cannot print rollup.config.js because it does not exist"; fi

# Build the application
RUN npm run build

EXPOSE 5000

CMD [ "npm", "run", "start" ]