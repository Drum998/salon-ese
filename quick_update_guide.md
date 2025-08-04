# 1. Get the latest version
git pull origin main

# 2. Rebuild the containers
docker-compose down
docker-compose build --no-cache

# 3. Start the application
docker-compose up -d

# 2. Run the migration
docker exec -it salon-ese-web-1 python migrate_salon_hours_integration.py

# 3. Test the integration
docker exec -it salon-ese-web-1 python test_salon_hours_integration.py

# 4. Access the application
# Open http://localhost:5010 and test the booking system