import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn="https://4465443c7756d19300022e0d12f400e2@o4510289261887488.ingest.us.sentry.io/4510322463670272",
    send_default_pii=True,
)

# Send a tagged error to identify the project
sentry_sdk.set_tag("project_identifier", "BACKEND_API_PROJECT")
sentry_sdk.set_context(
    "project_info",
    {"name": "Backend API", "environment": "development", "timestamp": "2024"},
)

try:
    raise Exception("BACKEND API PROJECT IDENTIFICATION ERROR")
except Exception as e:
    sentry_sdk.capture_exception(e)
    print("Tagged error sent! Check which Sentry project shows this error with tag 'BACKEND_API_PROJECT'")
