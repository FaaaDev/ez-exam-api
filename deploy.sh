#!/bin/bash

# Learning Platform Deployment Script
# This script sets up the complete learning platform

set -e  # Exit on any error

echo "🚀 Learning Platform Deployment Script"
echo "======================================"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "📦 Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Start PostgreSQL service
echo "🔧 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user (ignore errors if they already exist)
echo "🗄️  Setting up database..."
sudo -u postgres createdb learning_platform 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER learning_user WITH PASSWORD 'learning_pass';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE learning_platform TO learning_user;" 2>/dev/null || echo "Privileges already granted"

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed the database
echo "🌱 Seeding database with initial data..."
python3 scripts/seed_data.py

# Run acceptance tests
echo "🧪 Running acceptance tests..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Run tests
python3 tests/test_acceptance.py

# Stop the test server
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the server: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "2. Visit: http://localhost:8000/docs for API documentation"
echo "3. Test endpoints: curl http://localhost:8000/api/lessons"
echo ""
echo "📊 Demo user credentials:"
echo "   User ID: 1"
echo "   Username: demo_user"
echo "   Email: demo@example.com"
echo ""

