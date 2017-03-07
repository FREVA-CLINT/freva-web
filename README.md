

# React / Webpack usage:

Install dependencies:

    npm install

Build project:

    npm run build
    npm run build-production   # optimized production build

Development:

    npm run dev   # starts webpack-dev-server including hot-reloading

# Deploy a new version:

    git pull
    python manage.py collectstatic  # get new js files
