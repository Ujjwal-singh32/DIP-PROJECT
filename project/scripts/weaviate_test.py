"""
scripts/test_weaviate.py
─────────────────────────
Tests Weaviate connection and prints detailed diagnostics.

Run:
    python scripts/test_weaviate.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import weaviate
from backend.config import settings


def test_connection():
    print("\n" + "═" * 55)
    print("  Weaviate Connection Test")
    print("═" * 55)

    # ── Show current config ───────────────────────────────────────
    print(f"\n  URL     : {settings.weaviate_url}")
    key = settings.weaviate_api_key
    if key:
        masked = key[:6] + "*" * (len(key) - 10) + key[-4:]
        print(f"  API Key : {masked}")
    else:
        print(f"  API Key : ❌ EMPTY — this is likely the problem!")

    print()

    # ── Attempt connection ────────────────────────────────────────
    try:
        print("  Connecting …")

        is_local = "localhost" in settings.weaviate_url or "127.0.0.1" in settings.weaviate_url

        if is_local:
            client = weaviate.connect_to_local(
                host="localhost",
                port=8080,
                grpc_port=50051,
            )
        else:
            if not settings.weaviate_api_key:
                print("\n  ❌ WEAVIATE_API_KEY is empty in your .env!")
                print("     Go to https://console.weaviate.cloud")
                print("     → Click your cluster → API Keys → Copy Admin key")
                print("     → Add to .env: WEAVIATE_API_KEY=WVCxxxxxxxxxxxx\n")
                sys.exit(1)

            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=settings.weaviate_url,
                auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key),
            )

        # ── Check if ready ────────────────────────────────────────
        is_ready = client.is_ready()
        print(f"  is_ready : {is_ready}")

        if not is_ready:
            print("  ❌ Weaviate is reachable but not ready yet.")
            client.close()
            sys.exit(1)

        # ── Get server info ───────────────────────────────────────
        meta = client.get_meta()
        print(f"  Version  : {meta.get('version', 'unknown')}")
        print(f"  Hostname : {meta.get('hostname', 'unknown')}")

        # ── List existing collections ─────────────────────────────
        collections = client.collections.list_all()
        if collections:
            print(f"\n  Existing collections:")
            for name, col in collections.items():
                count = client.collections.get(name).aggregate.over_all(total_count=True).total_count
                print(f"    📁 {name}  →  {count} objects")
        else:
            print(f"\n  No collections yet (fresh cluster)")

        client.close()

        print("\n  ✅ Weaviate connection SUCCESSFUL!")
        print("  Run: python scripts/build_vector_index.py\n")
        print("═" * 55 + "\n")

    except weaviate.exceptions.WeaviateConnectionError as e:
        print(f"\n  ❌ Connection failed: {e}")
        print("\n  Possible causes:")
        print("  1. Wrong WEAVIATE_URL in .env")
        print("  2. Wrong or missing WEAVIATE_API_KEY in .env")
        print("  3. Cluster is paused → go to console.weaviate.cloud and Resume it")
        print("  4. No internet connection\n")
        print("═" * 55 + "\n")
        sys.exit(1)

    except weaviate.exceptions.AuthenticationFailedError as e:
        print(f"\n  ❌ Authentication failed: {e}")
        print("\n  Your API key is wrong or expired.")
        print("  Go to https://console.weaviate.cloud")
        print("  → Click your cluster → API Keys → Copy Admin key")
        print("  → Update WEAVIATE_API_KEY in your .env\n")
        print("═" * 55 + "\n")
        sys.exit(1)

    except Exception as e:
        print(f"\n  ❌ Unexpected error: {type(e).__name__}: {e}\n")
        print("═" * 55 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()