import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn="https://4465443c7756d19300022e0d12f400e2@o4510289261887488.ingest.us.sentry.io/4510322463670272",
    send_default_pii=True,
)

# Trigger a test error
try:
    1 / 0
except Exception as e:
    sentry_sdk.capture_exception(e)
    print("Test error sent to Sentry!")

print("Check your Sentry dashboard now!")