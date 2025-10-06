# Project Name: Muse - Team 1

## Database Design

### Overview
Brief description of your data model and why it supports your application.

### Entity Relationship Diagram
![ER Diagram](./docs/er-diagram.png)

### Tables Description

user_profiles: Stores information about each registered user.
user_id (UUID, PK): Unique identifier for the user.
subscription_tier (TEXT): User’s subscription plan (free or pro).
created_at (TIMESTAMPTZ): Timestamp when the profile was created.
updated_at (TIMESTAMPTZ): Auto-updated timestamp when the row is modified.

creator_profiles: Represents external creators that users can follow.
creator_id (BIGINT, PK, identity): Unique identifier for the creator.
profile_url (TEXT): Profile link of the creator (must start with http:// or https://).
platform (TEXT): The platform the creator is on (e.g., Instagram, TikTok).
created_at, updated_at: Lifecycle timestamps.

creator_content: Stores content/posts from creators.
content_id (BIGINT, PK, identity): Unique identifier for the content.
creator_id (BIGINT, FK): References creator_profiles(creator_id).
post_url (TEXT): Link to the creator’s content.
post_raw (TEXT, nullable): Raw content text.
created_at, updated_at: Lifecycle timestamps.

user_posts: Posts created by users on the platform.
post_id (UUID, PK, default gen_random_uuid()): Unique post identifier.
user_id (UUID, FK): References user_profiles(user_id).
raw_text (TEXT, nullable): Text of the post.
created_at, updated_at: Lifecycle timestamps.

user_media: Media attached to user posts.
user_media_id (UUID, PK): Unique identifier for media.
post_id (UUID, FK): References user_posts(post_id).
media_url (TEXT): Link to the media file.
media_type (TEXT, nullable): Type of media (image, video, etc.)
created_at, updated_at: Lifecycle timestamps.

user_follows: Tracks which creators a user follows.
id (UUID, PK, default gen_random_uuid()): Unique identifier.
user_id (UUID, FK): References user_profiles(user_id).
creator_id (BIGINT, FK): References creator_profiles(creator_id).
created_at: Follow timestamp.

post_inspirations: Links user posts to creator content they were inspired by.
id (BIGINT, PK, identity): Unique identifier.
post_id (UUID, FK): References user_posts(post_id).
content_id (BIGINT, FK): References creator_content(content_id).
created_at, updated_at: Lifecycle timestamps.
  
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
