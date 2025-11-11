import requests

# Test Sentry connection
try:
    # This will trigger a 404 error that Sentry should capture
    response = requests.get("http://localhost:8000/test-sentry-error")
    print("Response:", response.status_code)
except Exception as e:
    print("Error:", e)

print("Check your Sentry dashboard for the error!")
