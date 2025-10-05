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
- For testing you should use ckn9573@nyu.edu for the username and password if you want to try an authenticated session

### Prerequisites
- Python 3.10+
- Supabase account
- pip (Python package manager)
- Relevant libraries:
  - `supabase` - Supabase Python client
  - `python-dotenv` - Environment variable management
  - `httpx` - HTTP client for API requests

### Installation
Install required packages:
```bash
pip install supabase python-dotenv httpx
```

### Running the test scripts

```bash
python3 test_connection.py
```

```

```
