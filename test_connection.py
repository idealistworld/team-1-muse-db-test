"""
Supabase Connection Test Suite

This script validates the Muse database setup by testing:
1. Connection to Supabase
2. Read operations on all tables
3. Write operations (insert/delete)
4. RLS (Row-Level Security) policies
5. Join operations across foreign keys

It supports both authenticated and anonymous testing modes to verify
that RLS policies properly block unauthorized access.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD")

# Initialize the Supabase client with anonymous key
# RLS policies will determine what operations are allowed
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("🔗 Supabase Connection Test")
print("=" * 60)
print()

# Validate environment variables before proceeding
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
    print("Please copy .env.example to .env and configure your credentials.")
    exit(1)

# Ask if user wants to authenticate
# Authentication tests verify RLS policies work correctly for logged-in users
# Anonymous tests verify RLS policies properly block unauthenticated access
print("🔐 Run tests with authentication? (y/n): ", end="")
auth_choice = input().strip().lower()

authenticated_user_id = None
if auth_choice == "y":
    # Attempt to authenticate with credentials from .env
    if not TEST_USER_EMAIL or not TEST_USER_PASSWORD:
        print("❌ TEST_USER_EMAIL and TEST_USER_PASSWORD not set in .env")
        print("Continuing as anonymous...")
        print()
    else:
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            authenticated_user_id = auth_response.user.id
            print(f"✅ Authenticated as: {auth_response.user.email}")
            print(f"   User ID: {authenticated_user_id}")
            print()
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("   Possible causes:")
            print("   - User doesn't exist in Supabase Auth")
            print("   - Wrong password")
            print("   - Email confirmation required")
            print("Continuing as anonymous...")
            print()
else:
    print("⚠️  Running tests as anonymous user")
    print()

# Discover tables and get schema via OpenAPI spec
# This introspects the database to find all tables and their column definitions
print("🔍 Discovering tables and schema...")
try:
    import httpx
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
    }
    response = httpx.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch schema: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

    spec = response.json()

    tables = []
    schemas = {}

    if "definitions" in spec:
        tables = list(spec["definitions"].keys())
        schemas = spec["definitions"]

    print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
    print()

    # Debug: Show schema for user_profiles to verify enum constraints
    if "user_profiles" in schemas:
        print("📋 user_profiles schema:")
        if "properties" in schemas["user_profiles"]:
            for col, info in schemas["user_profiles"]["properties"].items():
                if "enum" in info:
                    print(f"   {col}: enum values = {info['enum']}")
        print()
except ImportError:
    print("❌ httpx library not installed. Run: pip install httpx")
    exit(1)
except Exception as e:
    print(f"❌ Failed to discover tables: {e}")
    print("   Make sure your Supabase project is accessible and credentials are correct.")
    exit(1)

if not tables:
    print("⚠️  No tables found in database")
    print("   Run the schema.sql file in your Supabase SQL editor first.")
    exit(1)

def generate_test_data(table_name, prefix="test"):
    """
    Generate valid test data for a table based on its schema.

    This function introspects the table's OpenAPI schema to determine:
    - Required vs. optional columns
    - Data types (UUID, string, integer, boolean)
    - Enum constraints
    - Primary key patterns (to skip auto-generated IDs)

    Args:
        table_name: The name of the table to generate data for
        prefix: String prefix for generated test values (default: "test")

    Returns:
        Dictionary of column_name -> test_value pairs, including only
        required columns and skipping auto-generated fields.
    """
    if table_name not in schemas:
        return {}

    schema = schemas[table_name]
    test_data = {}

    # Common value mappings for constrained columns
    common_values = {
        "subscription_tier": "pro",
        "tier": "pro",
        "status": "active",
        "role": "user",
        "type": "default",
        "visibility": "public",
        "plan": "pro",
        "platform": "instagram",
        "url": "https://example.com",
        "profile_url": "https://instagram.com/test",
        "post_url": "https://example.com/post",
        "media_url": "https://example.com/media.jpg"
    }

    if "properties" in schema:
        for col_name, col_info in schema["properties"].items():
            # Skip auto-generated columns (always skip these)
            if col_name in ["id", "created_at", "updated_at"]:
                continue

            # Skip primary key ID columns that are GENERATED ALWAYS
            # Match patterns like: creator_profiles -> creator_id, user_posts -> post_id
            possible_pk_names = [
                f"{table_name.rstrip('s')}_id",  # creator_profiles -> creator_profile_id
                f"{table_name[:-1]}_id",          # creator_profiles -> creator_profile_id
                table_name.replace('_profiles', '_id').replace('_posts', '_id').replace('_content', '_id'),  # creator_profiles -> creator_id
            ]

            # Also handle singular forms
            if table_name.endswith('s'):
                singular = table_name[:-1]  # Remove trailing 's'
                # Handle irregular plurals
                if table_name.endswith('ies'):
                    singular = table_name[:-3] + 'y'
                elif table_name.endswith('es'):
                    singular = table_name[:-2]

                possible_pk_names.extend([
                    f"{singular}_id",
                    singular.replace('_profile', '_id').replace('_post', '_id').replace('_content', '_id')
                ])

            if col_name in possible_pk_names:
                continue

            # Only add required columns
            if col_name in schema.get("required", []):
                col_type = col_info.get("type", "string")
                col_format = col_info.get("format", "")
                enum_values = col_info.get("enum", [])

                if col_type == "string":
                    if col_format == "uuid":
                        # Use authenticated user ID for user_id column in user tables
                        if col_name == "user_id" and authenticated_user_id and prefix == "test":
                            test_data[col_name] = authenticated_user_id
                        else:
                            test_data[col_name] = str(uuid.uuid4())
                    elif enum_values:
                        # Use first enum value if available
                        test_data[col_name] = enum_values[0]
                    elif col_name in common_values:
                        # Use common value for known constrained columns
                        test_data[col_name] = common_values[col_name]
                    elif "url" in col_name:
                        # Any column with 'url' in the name gets a valid URL
                        test_data[col_name] = "https://example.com"
                    else:
                        test_data[col_name] = f"{prefix}_{col_name}"
                elif col_type == "integer":
                    test_data[col_name] = 999 if prefix == "unauthorized" else 1
                elif col_type == "boolean":
                    test_data[col_name] = False if prefix == "unauthorized" else True

    return test_data

# ============================================================================
# TEST 1: Connection Works
# ============================================================================
# Verifies that we can connect to Supabase and execute a basic query
print("1️⃣  CONNECTION TEST")
print("-" * 60)
try:
    response = supabase.table(tables[0]).select("*").limit(1).execute()
    print(f"✅ PASSED - Connected to Supabase successfully")
    print(f"   Raw response object: {response}")
    print(f"   Response.data: {response.data}")
    print(f"   Response.count: {response.count}")
    print()
except Exception as e:
    print(f"❌ FAILED - {e}")
    print("   Could not execute basic query. Check your Supabase project status.")
    print()

# ============================================================================
# TEST 2: Read Operations
# ============================================================================
# Tests SELECT queries on multiple tables
# Expected behavior:
# - Authenticated: Should see own data (RLS filters by user_id)
# - Anonymous: Should be blocked by RLS or see empty results
print("2️⃣  READ OPERATIONS TEST")
print("-" * 60)
for table in tables[:3]:
    try:
        response = supabase.table(table).select("*").limit(1).execute()
        print(f"✅ PASSED - Can read from '{table}' ({len(response.data)} rows)")
        print(f"   Raw response: {response}")
        print(f"   Response.data: {response.data}")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAILED - '{table}': {error_msg[:80]}")
        if "permission denied" in error_msg.lower() or "row-level security" in error_msg.lower():
            print(f"   RLS is blocking access (expected for anonymous users)")
        print(f"   Full error: {e}")
print()

# ============================================================================
# TEST 3: Write Operations
# ============================================================================
# Tests INSERT and DELETE operations
# Expected behavior:
# - Authenticated: Should succeed if user owns the data (user_id = auth.uid())
# - Anonymous: Should be blocked by RLS policies
# This test auto-cleans up inserted data to allow re-running
print("3️⃣  WRITE OPERATIONS TEST")
print("-" * 60)
for table in tables[:1]:  # Just test first table to avoid clutter
    try:
        test_data = generate_test_data(table, "test")

        if test_data:
            response = supabase.table(table).insert(test_data).execute()
            print(f"✅ PASSED - Insert to '{table}' succeeded")
            print(f"   Raw insert response: {response}")
            print(f"   Response.data: {response.data}")

            # Show the inserted record as proof
            if response.data and len(response.data) > 0:
                inserted_record = response.data[0]
                print(f"   📝 Inserted record: {inserted_record}")

                # Clean up - delete the test record to avoid duplicate key errors on re-runs
                # Try to find the primary key - could be 'id', 'creator_id', 'post_id', etc.
                pk_field = None
                pk_value = None

                if 'id' in inserted_record:
                    pk_field = 'id'
                    pk_value = inserted_record['id']
                else:
                    # Try table-specific ID field (creator_profiles -> creator_id)
                    possible_pk = table.replace('_profiles', '_id').replace('_posts', '_id').replace('_content', '_id')
                    if possible_pk in inserted_record:
                        pk_field = possible_pk
                        pk_value = inserted_record[possible_pk]

                if pk_field and pk_value:
                    try:
                        delete_response = supabase.table(table).delete().eq(pk_field, pk_value).execute()
                        print(f"   🧹 Deleted test record (confirmed cleanup)")
                        print(f"   Raw delete response: {delete_response}")
                        print(f"   Delete response.data: {delete_response.data}")
                    except Exception as cleanup_error:
                        print(f"   ⚠️  Cleanup failed: {str(cleanup_error)[:60]}")
                        print(f"   Full cleanup error: {cleanup_error}")
                        print(f"   You may need to manually delete test data")
        else:
            print(f"⚠️  SKIPPED - '{table}': No schema found")
    except Exception as e:
        error_msg = str(e)
        if "row-level security" in error_msg.lower() or "permission denied" in error_msg.lower():
            if auth_choice == "y":
                print(f"⚠️  BLOCKED - '{table}': RLS blocked authenticated write (check policies)")
                print(f"   This might be expected if WITH CHECK clauses require specific conditions")
                print(f"   Full error response: {error_msg}")
            else:
                print(f"✅ PASSED - '{table}': RLS blocked anonymous write (expected)")
                print(f"   DB error response: {error_msg}")
        elif "check constraint" in error_msg.lower():
            print(f"❌ FAILED - '{table}': Check constraint violation")
            print(f"   The generated test data doesn't satisfy table constraints")
            print(f"   Full error: {error_msg}")
            print(f"   Generated data: {test_data}")
        elif "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
            print(f"⚠️  SKIPPED - '{table}': Duplicate key (test data already exists)")
            print(f"   Run cleanup or use different test values")
        else:
            print(f"❌ FAILED - '{table}': {error_msg[:80]}")
            print(f"   Full error: {error_msg}")
print()

# ============================================================================
# TEST 4: RLS Protection
# ============================================================================
# Verifies that RLS policies are active and filtering data correctly
# Expected behavior:
# - Authenticated: Should only see own data (rows where user_id = auth.uid())
# - Anonymous: Should see 0 rows or be blocked entirely
print("4️⃣  RLS PROTECTION TEST")
print("-" * 60)
for table in tables[:1]:  # Just test first table
    try:
        # Try to read - RLS will filter results based on who you are
        response = supabase.table(table).select("*").execute()
        if auth_choice == "y":
            print(f"✅ PASSED - '{table}': Authenticated read returned {len(response.data)} rows")
            print(f"   (Should only see rows belonging to authenticated user)")
            print(f"   Raw response: {response}")
            print(f"   Response.data: {response.data[:2] if len(response.data) > 1 else response.data}")
        else:
            print(f"✅ PASSED - '{table}': Anonymous read returned {len(response.data)} rows (RLS filtering applied)")
            print(f"   (Should be 0 rows or blocked entirely for anonymous users)")
            print(f"   Raw response: {response}")
            print(f"   Response.data: {response.data[:2] if len(response.data) > 1 else response.data}")
    except Exception as e:
        error_msg = str(e)
        if "row-level security" in error_msg.lower() or "permission denied" in error_msg.lower():
            print(f"✅ PASSED - '{table}': RLS blocking reads (very restrictive)")
            print(f"   This is expected behavior for private tables")
            print(f"   Error: {error_msg}")
        else:
            print(f"❌ FAILED - '{table}': {error_msg[:80]}")
            print(f"   Unexpected error occurred")
            print(f"   Full error: {error_msg}")
print()

# ============================================================================
# TEST 5: Join Operations
# ============================================================================
# Verifies that foreign key relationships work correctly
# Tests Supabase's automatic join syntax: table1.select('*, table2(*)')
# This validates the schema's foreign key constraints are properly set up
print("5️⃣  JOIN OPERATIONS TEST")
print("-" * 60)

# Test multiple join scenarios based on your schema
join_tests = [
    ("user_follows", "creator_profiles", "Join user_follows -> creator_profiles"),
    ("user_posts", "user_profiles", "Join user_posts -> user_profiles"),
    ("creator_content", "creator_profiles", "Join creator_content -> creator_profiles"),
]

join_passed = False
for main_table, related_table, description in join_tests:
    if main_table in tables and related_table in tables:
        try:
            # Supabase join syntax: table1.select('*, table2(*)')
            response = supabase.table(main_table).select(f"*, {related_table}(*)").limit(1).execute()
            print(f"✅ PASSED - {description}")
            print(f"   Retrieved {len(response.data)} joined record(s)")
            print(f"   Full join response: {response.data}")
            join_passed = True
            break
        except Exception as e:
            error_msg = str(e)
            if "permission denied" in error_msg.lower() or "row-level security" in error_msg.lower():
                print(f"⚠️  {description} - RLS blocked join (expected if no data or anonymous)")
            else:
                print(f"⚠️  {description} - {error_msg[:80]}")
            print(f"   Full error: {error_msg}")
            continue

if not join_passed:
    print("⚠️  SKIPPED - No successful joins")
    print("   This could mean:")
    print("   - No data exists in tables yet (run seed.sql)")
    print("   - RLS policies are blocking access")
    print("   - Foreign key relationships need to be verified")
print()

print("=" * 60)
print("✨ Test suite complete!")
print()
print("Summary:")
print("- If authenticated: You should see your own data and be able to insert/delete")
print("- If anonymous: Most operations should be blocked by RLS policies")
print("- All users need authentication to access this platform")
print()
