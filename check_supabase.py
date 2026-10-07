from supabase_client import supabase
try:
        supabase.auth.get_user("not-a-real-token")
except Exception as e:
        print(type(e).__name__, "-", e)