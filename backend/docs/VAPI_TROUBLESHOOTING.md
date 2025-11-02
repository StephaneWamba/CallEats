# Vapi API Troubleshooting Guide

This document outlines known issues encountered when integrating with the Vapi API and their solutions.

> **Note:** Some of these issues may be mitigated with further study of the Vapi API documentation and features. The solutions presented here are based on our current understanding and testing. As the Vapi API evolves or as we gain deeper insights into its capabilities, some problems may have better solutions or workarounds.

## 1. Webhook Reliability Issues

### Problem

**Vapi webhooks are unreliable** - the final "ended" webhook events often never arrive, causing incomplete call history data to be captured.

**Symptoms:**

- Call records missing transcripts, durations, or costs
- No data in database after call ends
- Incomplete call history

**Root Cause:**
Vapi's webhook delivery is not guaranteed. The `end-of-call-report` webhook may fail to deliver, leaving call data incomplete.

### Solution

**Implemented Fallback Mechanism:**

The system automatically schedules an API fetch 30 seconds after detecting a call, regardless of whether webhooks arrive. This ensures complete call data is captured.

**How it works:**

1. When a call starts (`status-update: ringing`), the system schedules a background API fetch after 30 seconds
2. When `end-of-call-report` webhook arrives, it also schedules an API fetch
3. The fetch uses Vapi's API directly to retrieve complete call data (transcript, duration, cost)
4. Duplicate prevention ensures only one fetch per call ID

**Implementation:**

- See: `backend/src/services/vapi/server.py` - `_schedule_fallback_fetch()`
- See: `backend/src/services/calls/fetch.py` - `fetch_and_store_call_from_vapi()`

**Note:** The 30-second delay allows the call to fully complete and be processed by Vapi's backend before fetching.

---

## 2. Assistant Silence Issues

### Problem

When `first_message` and `request_start` are set to `null` in `prompts.yaml`, the assistant may be completely silent:

- No greeting when call starts
- No acknowledgment when looking up information
- No response to customer questions

**Symptoms:**

- Silent calls with no assistant responses
- Customer hears nothing after speaking

**Root Cause:**
Setting these values to `null` completely disables the messages, causing the assistant to not generate any response in some cases.

### Solution

**Keep default values** even when you want natural variation:

```yaml
# backend/vapi/config/prompts.yaml
prompts:
  first_message: "Hi! Thanks for calling. How can I help you today?"

  tool_messages:
    request_start: "One moment."
```

**Best Practice:**

- The system prompt already instructs the assistant to vary responses naturally
- Keeping these fallback messages ensures the assistant always speaks
- The assistant will still vary its language throughout the call based on the system prompt

**Implementation Note:**

The backend code conditionally includes these messages only if they're explicitly set (not `null`):

- See: `backend/src/services/vapi/manager.py` - `build_tool_config()` and `create_assistant()`

---

## 3. Phone Number Assignment Failures

### Problem

Phone number assignment can fail in several scenarios:

**Symptoms:**

- `assign_phone_to_restaurant()` returns `None`
- Phone not mapped to restaurant
- Assistant not receiving calls

**Common Failure Scenarios:**

#### 3.1 Missing Assistant

**Error:** `"No shared assistant found for phone assignment"`

**Cause:** No assistant named "Restaurant Voice Assistant" exists in Vapi account.

**Solution:**

- Run `python scripts/setup_vapi.py` to create the assistant
- Verify assistant exists: Check Vapi dashboard or use `list_assistants()` API

#### 3.2 Twilio Number Not Accessible

**Error:** `"Twilio number not accessible in Vapi"` or `"not found"` / `"number not found"`

**Cause:**

- Twilio number was purchased but Vapi API cannot find it
- Number was deleted or never properly created in Vapi

**Solution:**

- Verify number exists in Twilio dashboard
- Try recreating the number in Vapi manually or via API
- Check Twilio credentials are correct

#### 3.3 No Available Phones

**Error:** No error, but function returns `None`

**Cause:**

- All existing phone numbers are already assigned
- Twilio credentials not configured (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`)
- Twilio trial account limits (cannot purchase new numbers)

**Solution:**

- Configure Twilio credentials in `.env`
- Purchase Twilio number manually and add to Vapi
- Use existing unassigned phone number if available

#### 3.4 Phone Mapping Creation Failure

**Error:** `"Failed to save phone mapping"`

**Cause:** Database insert failed for `restaurant_phone_mappings` table.

**Solution:**

- Check database connection
- Verify `restaurant_phone_mappings` table exists
- Check database permissions

**Implementation:**

- See: `backend/src/services/phones/service.py` - `assign_phone_to_restaurant()`
- See: `backend/src/services/phones/twilio.py` - `create_and_assign_twilio_phone()`

---

## 4. Phone Number Extraction Issues

### Problem

Phone numbers may not be extracted correctly from Vapi webhook payloads.

**Symptoms:**

- Call records missing phone numbers
- Cannot map calls to restaurants
- `get_restaurant_id_from_phone()` returns `None`

**Root Cause:**
Vapi webhook structure varies:

- Sometimes `phoneNumber` is at `message.phoneNumber`
- Sometimes at `message.call.phoneNumber`
- Structure may be a dict with `"number"` field or a string

### Solution

**Multi-level Fallback Extraction:**

The system tries multiple locations and formats:

1. `message.phoneNumber` (dict or string)
2. `message.call.phoneNumber` (dict or string)
3. From Vapi API call data if webhook lacks phone number
4. From phone number ID via API lookup

**Implementation:**

- See: `backend/src/services/vapi/server.py` - `_extract_phone_number()`
- See: `backend/src/services/calls/fetch.py` - Phone number fallback logic

---

## 5. Webhook Configuration Issues

### Problem

Webhooks not being received by backend.

**Symptoms:**

- No webhook logs in backend
- Calls not being processed
- Call history not captured

**Common Causes:**

#### 5.1 Incorrect Server URL

**Cause:** `PUBLIC_BACKEND_URL` not set correctly or not publicly accessible.

**Solution:**

- Verify `PUBLIC_BACKEND_URL` is reachable from internet (use Cloudflare Tunnel, ngrok, or production URL)
- Test webhook endpoint: `POST {PUBLIC_BACKEND_URL}/api/vapi/server`
- Check Vapi assistant configuration has correct server URL

#### 5.2 Missing Webhook Events

**Cause:** Assistant not configured with required webhook events.

**Solution:**

- Ensure assistant has `serverMessages: ["status-update", "end-of-call-report"]`
- See: `backend/src/services/vapi/manager.py` - `create_assistant()`

#### 5.3 HMAC Verification Failure

**Cause:** `VAPI_SECRET_KEY` mismatch or missing.

**Solution:**

- Verify `VAPI_SECRET_KEY` matches Vapi dashboard webhook secret
- Check HMAC verification is enabled in middleware
- See: `backend/src/core/middleware/auth.py`

---

## 6. API Rate Limiting

### Problem

Vapi API rate limits may be hit during bulk operations.

**Symptoms:**

- `429 Too Many Requests` errors
- Operations timing out
- Partial failures

**Solution:**

- Add delays between API calls for bulk operations
- Implement retry logic with exponential backoff
- Consider using webhooks instead of polling when possible

**Note:** The fallback API fetch mechanism (see Issue #1) may hit rate limits if many calls end simultaneously. Consider adding rate limiting or queuing.

---

## 7. Call Status Not Updated

### Problem

Fetched call data shows incorrect status (e.g., "ringing" when call has ended).

**Symptoms:**

- API fetch returns but call not stored
- Logs show "Call not ended yet (status=...)"

**Root Cause:**
30-second delay may be too short for very long calls, or Vapi backend hasn't processed the call yet.

**Solution:**

- Increase delay in `_schedule_fallback_fetch()` if needed
- Implement retry logic for calls that are still in-progress
- Consider polling until status is "ended"

**Implementation:**

- See: `backend/src/services/calls/fetch.py` - Status check before storing
- See: `backend/src/services/vapi/server.py` - `_schedule_fallback_fetch()`

---

## General Troubleshooting Tips

1. **Check Logs:** Enable debug logging to see detailed webhook and API call information
2. **Verify Configuration:** Ensure all environment variables are set correctly
3. **Test Webhooks:** Use Vapi dashboard to manually trigger webhooks or test endpoints
4. **API Testing:** Use Vapi API directly to verify phone numbers, assistants, and calls exist
5. **Database State:** Verify phone mappings, call records, and restaurant data in database

## Related Documentation

- [API Documentation](API.md) - Endpoint details
- [Setup Guide](SETUP.md) - Initial configuration
- [Architecture](ARCHITECTURE.md) - System design and fallback mechanisms
- [Phone Number Automation](PHONE_NUMBER_AUTOMATION.md) - Phone assignment flow
