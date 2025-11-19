# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL for the Saleeth backend Django application.

## Prerequisites

- Python 3.x installed
- PostgreSQL installed on your system
- Virtual environment activated (if using one)

## Step 1: Install PostgreSQL

### Windows

1. Download PostgreSQL from [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` superuser
4. PostgreSQL will be installed on port `5432` by default

### macOS

```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 2: Create PostgreSQL Database

### Using psql (Command Line)

1. Open a terminal/command prompt
2. Connect to PostgreSQL:
   ```bash
   psql -U postgres
   ```
   (Enter your PostgreSQL password when prompted)

3. Create the database:
   ```sql
   CREATE DATABASE saleeth_db;
   ```

4. Create a dedicated user (optional but recommended):
   ```sql
   CREATE USER saleeth_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE saleeth_db TO saleeth_user;
   ALTER USER saleeth_user CREATEDB;
   ```

5. Exit psql:
   ```sql
   \q
   ```

### Using pgAdmin (GUI)

1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Enter database name: `saleeth_db`
5. Click "Save"

## Step 3: Install Python Dependencies

Make sure you have all required packages installed:

```bash
pip install -r requirements.txt
```

The key dependencies for PostgreSQL are:
- `psycopg2-binary` - PostgreSQL adapter for Python
- `python-dotenv` - Environment variable management

## Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your database credentials:
   ```env
   # Database Configuration
   DB_NAME=saleeth_db
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   DB_HOST=localhost
   DB_PORT=5432

   # Django Configuration
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

   **Important:** Replace `your_postgres_password` with your actual PostgreSQL password.

   If you created a dedicated user, use those credentials instead:
   ```env
   DB_USER=saleeth_user
   DB_PASSWORD=your_secure_password
   ```

## Step 5: Run Database Migrations

After configuring your database, run Django migrations to create the database schema:

```bash
python manage.py migrate
```

This will create all the necessary tables in your PostgreSQL database.

## Step 6: Create a Superuser (Optional)

Create a Django admin superuser to access the admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin account.

## Step 7: Verify the Setup

Test your database connection by running:

```bash
python manage.py dbshell
```

If you can connect successfully, you should see the PostgreSQL prompt. Type `\q` to exit.

Alternatively, start the Django development server:

```bash
python manage.py runserver
```

If the server starts without database errors, your PostgreSQL setup is complete!

## Troubleshooting

### Connection Refused Error

- Ensure PostgreSQL service is running:
  - Windows: Check Services app or run `pg_ctl status`
  - macOS: `brew services list`
  - Linux: `sudo systemctl status postgresql`

### Authentication Failed

- Verify your database credentials in `.env`
- Check if the user has proper permissions
- Ensure the password doesn't contain special characters that need escaping

### Database Does Not Exist

- Create the database using the steps in Step 2
- Verify the database name in `.env` matches the created database

### Port Already in Use

- Check if another PostgreSQL instance is running on port 5432
- Change the port in `.env` if needed, or stop the conflicting service

## Migration from SQLite (Optional)

If you have existing data in SQLite and want to migrate it:

1. **Export data from SQLite:**
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Update settings.py to use PostgreSQL** (already done)

3. **Create fresh database and run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Load data into PostgreSQL:**
   ```bash
   python manage.py loaddata data.json
   ```

## Production Considerations

For production environments:

1. **Use a strong SECRET_KEY** - Generate a new one:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Set DEBUG=False** in `.env`

3. **Use environment-specific database credentials**

4. **Set up proper database backups**

5. **Configure connection pooling** if needed

6. **Use SSL connections** for remote databases

## Additional Resources

- [Django Database Documentation](https://docs.djangoproject.com/en/stable/ref/databases/)
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

