# Create an expense

**Status:** Proposed contract. `POST /api/expenses` is not implemented yet.
The application currently exposes only the status endpoint at `/`.

## Request

`POST /api/expenses`

Content-Type: `application/json` (an optional charset parameter is accepted).
The body must be a JSON object containing exactly these three required fields:

| Field | Type | Validation |
| --- | --- | --- |
| `amount` | string | A base-10 decimal string with an optional leading minus sign, at least one ASCII digit before the decimal point, and, if a decimal point is present, one or two ASCII digits after it. The entire string must match `-?[0-9]+(?:\.[0-9]{1,2})?`. |
| `category` | string | Must contain at least one non-whitespace character. Leading and trailing whitespace is removed before saving and returning the value; internal whitespace and letter case are preserved. |
| `date` | string | Exactly ten ASCII characters in `YYYY-MM-DD` format and a real Gregorian calendar date, with a year from `0001` through `9999`. Validate month lengths and leap years. |

Missing fields, `null`, and values of any other JSON type are invalid. Unknown
fields are rejected, including a client-supplied `id`; IDs belong to the server.

Amount examples:

- Valid: `"12"`, `"12.3"`, `"12.30"`, `"0"`, `"-12.30"`, `"0012.30"`.
- Invalid: the JSON number `12.30`, `""`, `" 12.30 "`, `"+12.30"`, `".50"`,
  `"12."`, `"12.345"`, `"1e2"`, `"12,30"`, `"NaN"`, `"Infinity"`.

Zero and negative amounts are allowed; this contract imposes no positive-only
restriction. Amounts must be handled and stored as exact decimal values, without
binary floating-point conversion or rounding. Responses use a canonical decimal
string with exactly two fractional digits and no redundant leading zeros:
`"0012.3"` becomes `"12.30"`, and negative zero becomes `"0.00"`.

Date examples: `"2024-02-29"` is valid; `"2025-02-29"`, `"2026-04-31"`,
`"2026-1-05"`, `"0000-01-01"`, surrounding whitespace, and timestamps are invalid.
Past, present, and future dates are accepted. No timezone conversion is applied.

Example request body:

```json
{
  "amount": "12.30",
  "category": "Groceries",
  "date": "2026-10-05"
}
```

## Successful response

Return **201 Created** with Content-Type `application/json` only after the expense
has been successfully persisted. The response is the saved expense object:

```json
{
  "id": "3d7fbcb6-cf52-4df4-9053-3ae6d294fcf5",
  "amount": "12.30",
  "category": "Groceries",
  "date": "2026-10-05"
}
```

`id` is a server-generated UUID v4 string in lowercase, hyphenated form. It is
unique, stable, and stored with the expense. The example ID is illustrative.
The returned values must match the persisted values after the normalization
described above.

Each successful request creates exactly one expense. Identical repeated requests
create separate expenses with different IDs; this endpoint does not provide
deduplication or idempotency guarantees.

## Error responses

All errors below return Content-Type `application/json` and this envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "fields": {
      "amount": "Must be a decimal string with at most two decimal places."
    }
  }
}
```

| Status | `error.code` | Condition | `error.message` |
| --- | --- | --- | --- |
| 400 | `invalid_request` | Missing or unsupported Content-Type, empty body, malformed JSON, or a top-level JSON value other than an object. | `Request must contain a JSON object with Content-Type application/json.` |
| 400 | `validation_error` | Missing required fields, invalid field types or values, or unknown fields. | `Request validation failed.` |
| 500 | `internal_error` | An unexpected server or persistence failure. | `The expense could not be saved.` |

For `validation_error`, `error.fields` maps every invalid or unknown field name
to a human-readable explanation. Missing required fields use `"This field is
required."`; unknown fields use `"Unknown field."`. Other field explanations
may vary; clients should rely on the status, code, and field names. Field order
is not significant. For `invalid_request` and `internal_error`, omit `fields`.
Do not expose internal exception or database details.

Request-level checks run before field validation. An unsupported media type is
deliberately a **400**, so all invalid requests follow the same status policy.

## Persistence guarantees

- Validate the entire request before saving anything. Every **400** response
  leaves the expense store unchanged, even when some fields are valid.
- Save the ID and all three fields atomically. If saving fails, roll back the
  write; never leave a partial expense or report **201** before the save commits.
- Persistence must survive application restarts. The storage technology and
  schema are implementation decisions deferred until endpoint development.

## Acceptance examples

| Request or condition | Expected result |
| --- | --- |
| All three fields valid | 201; one persisted expense with a generated UUID. |
| `amount: "12.3"`, otherwise valid | 201; amount stored and returned as `"12.30"`. |
| `category: "  Groceries  "`, otherwise valid | 201; category stored and returned as `"Groceries"`. |
| A required field missing or `null` | 400; no expense saved. |
| Numeric amount or more than two decimal places | 400; no expense saved. |
| Empty or whitespace-only category | 400; no expense saved. |
| Invalid calendar date or date format | 400; no expense saved. |
| Extra field, including `id` | 400; no expense saved. |
| Empty body, malformed JSON, array, or missing/unsupported Content-Type | 400; no expense saved. |
| Multiple invalid fields | 400; all field errors reported; no expense saved. |
| Persistence transaction fails | 500; no expense committed. |

These are requirements for future implementation and tests, not claims about
the current application's behavior.
