````
# Project Name: Muse - Team 1

## Database Design

### Overview
Brief description of your data model and why it supports your application.

### Entity Relationship Diagram
![ER Diagram](./docs/er-diagram.png)

### Tables Description
- **profiles**: Stores user profile information
  - `id` (UUID): Primary key
  - `email` (TEXT): Unique user email
  - ...

### Security Model
Explanation of your RLS policies and access control strategy.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Supabase account
- pip (Python package manager)
- Relevant libraries:
  - `supabase` - Supabase Python client
  - `python-dotenv` - Environment variable management
  - `httpx` - HTTP client for API requests

### Installation

1. Install required packages:
```bash
pip install supabase python-dotenv httpx
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Update `.env` with your Supabase credentials:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Test user credentials (for authenticated testing)
TEST_USER_EMAIL=your-test-email@example.com
TEST_USER_PASSWORD=your-test-password
```

### Running the test scripts

Run the connection test:
```bash
python3 test_connection.py
```

When prompted, choose:
- `y` to run authenticated tests (uses credentials from `.env`)
- `n` to run anonymous tests only

```

```
