# WealthKernel API Research

> Scraped from the Stoplight-hosted docs at `docs.wealthkernel.com` via their internal
> project API (`/api/v1/projects/cHJqOjc4Nzg2/nodes/{nodeId}`). The docs are entirely
> JS-rendered so standard HTTP fetches return an empty shell — this data was extracted
> from the Stoplight node API directly.

## General API Conventions

| Item | Value |
|------|-------|
| Sandbox base URL | `https://api.sandbox.wealthkernel.io` |
| Production base URL | `https://api.wealthkernel.io` |
| Version header | `Accept-Version: 2021-05-17` (required on every request) |
| Auth | `Authorization: Bearer {token}` — OAuth2 client credentials flow |
| Content type | `application/json` |

### Pagination

All list endpoints use **cursor-based pagination** with two parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max results per page. Default **20**. Capped at an endpoint-specific max. |
| `after` | string | Opaque cursor token from the previous response. |

The cursor is returned in the **`Pagination-Last` response header**. If the header is
present, there are more pages — pass its value as `after` on the next request. If the
header is absent, you've reached the last page.

```
# Page 1
GET /accounts?limit=20
← Pagination-Last: abc123

# Page 2
GET /accounts?limit=20&after=abc123
← Pagination-Last: def456

# Page 3 (last)
GET /accounts?limit=20&after=def456
← (no Pagination-Last header)
```

> **Important**: The cursor value is opaque. Do not parse, interpret, or store it
> long-term. It is only valid for the next request in the same pagination sequence.

---

## Endpoint Reference

### Accounts

#### GET /accounts — List accounts

Returns a JSON array of account objects. **No server-side date filter exists.**

##### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max results per page (default 20) |
| `after` | string | No | Pagination cursor |
| `accountId` | string | No | Filter by account ID |
| `clientReference` | string | No | Filter by your client reference |
| `type` | string | No | `GIA`, `ISA`, `JISA`, `SIA`, `SIPP` |
| `status` | string | No | `Pending`, `Active`, `Suspended`, `Closing`, `Closed` |
| `productId` | string | No | Filter by product ID |
| `owner` | string | No | Owner party ID (ISAs, GIAs, SIAs) |
| `registeredContact` | string | No | Registered contact party ID (JISAs only) |
| `child` | string | No | Child party ID (JISAs only) |
| `beneficiary` | string | No | Beneficiary party ID (SIAs only) |

##### Response — 200 OK

Array of account objects. The shape varies by `type` (polymorphic via `oneOf`):

**Base fields (all account types):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | e.g. `acc-34gbczz4624t32` |
| `clientReference` | string | Your reference |
| `name` | string | Account name |
| `type` | string | `GIA`, `ISA`, `JISA`, `SIA`, `SIPP` |
| `status` | string | `Pending`, `Active`, `Suspended`, `Closing`, `Closed` |
| `currency` | string | ISO 4217 — `GBP`, `EUR`, `USD` |
| `addedAt` | string | ISO 8601 timestamp, e.g. `2021-03-13T16:41:16.4237925Z` |

**Type-specific fields:**

| Type | Extra Fields |
|------|-------------|
| GIA | `productId`, `owner` |
| ISA | `productId`, `owner` |
| JISA | `productId`, `registeredContact`, `child` |
| SIA | `productId`, `owner`, `beneficiary` (currency locked to EUR) |
| SIPP | `productId`, `member`, `parentOrGuardian` |

##### Example Response

```json
[
  {
    "id": "acc-33xifz3ii25yac",
    "clientReference": "5g94j5gnknv9",
    "name": "Nicola's GIA",
    "type": "GIA",
    "status": "Active",
    "productId": "prd-gia",
    "addedAt": "2021-03-13T16:41:16.4237925Z",
    "owner": "pty-33xig43bj24vza",
    "currency": "GBP"
  },
  {
    "id": "acc-33xka66xp2fsbw",
    "clientReference": "ds8bu84nwn",
    "name": "Tom's ISA",
    "type": "ISA",
    "status": "Active",
    "productId": "prd-isa",
    "addedAt": "2021-02-13T16:41:16.4237925Z",
    "owner": "pty-33xig43bj24vza",
    "currency": "GBP"
  }
]
```

##### Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

### Parties

#### GET /parties — List parties

**No date filters.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `clientReference` | string | Filter by client reference |
| `emailAddress` | string | Filter by email |
| `surname` | string | Filter by surname |
| `type` | string | Party type |
| `organizationType` | string | Organization type |
| `name` | string | Filter by name |

---

### Addresses

#### GET /addresses — List addresses

**No date filters.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `partyId` | string | Filter by party ID |

---

### Bank Accounts

#### GET /bank-accounts — List bank accounts

**No date filters.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `partyId` | string | Filter by party ID |
| `clientReference` | string | Filter by client reference |
| `accountNumber` | string | Filter by account number |
| `sortCode` | string | Filter by sort code |

---

### Portfolios

#### GET /portfolios — List portfolios

**No date filters.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `accountId` | string | Filter by account ID |
| `clientReference` | string | Filter by client reference |
| `currency` | string | Filter by currency |
| `status` | string | Filter by status |

---

### Transactions

#### GET /transactions — List transactions

**Has date filters: `startDate`, `endDate`, `updatedSince`.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `startDate` | string | Start date filter on the `timestamp` field |
| `endDate` | string | End date filter on the `timestamp` field |
| `updatedSince` | string | Only return records updated since this time |
| `isin` | string | Filter by ISIN |
| `type` | string | Filter by transaction type |
| `status` | string | Filter by status |
| `settledOn` | string | Filter by settlement date |

> `updatedSince` is ideal for incremental sync — it catches both new and modified
> transactions since your last poll.

---

### Orders

#### GET /orders — List orders

**Has date filters: `receivedAfter`, `receivedBefore`.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `clientReference` | string | Filter by client reference |
| `side` | string | Buy/Sell |
| `status` | string | Filter by status |
| `receivedAfter` | string | Orders received after this timestamp |
| `receivedBefore` | string | Orders received before this timestamp |

---

### Deposits

#### GET /deposits — List deposits

**Has date filters: `startDate`, `endDate`.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `reference` | string | Filter by reference |
| `startDate` | string | Deposits created on or after this date |
| `endDate` | string | Deposits created on or before this date |
| `status` | string | Filter by status |

---

### Withdrawals

#### GET /withdrawals — List withdrawals

**No date filters.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `type` | string | Withdrawal type |
| `reference` | string | Filter by reference |
| `status` | string | Filter by status |

---

### Valuations

#### GET /valuations — List valuations

**Has date filters: `startDate`, `endDate`, `updatedSince`.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `startDate` | string | Start date |
| `endDate` | string | End date |
| `updatedSince` | string | Only return records updated since this time |

---

### Fees

#### GET /fees — List fees

**Has date filters: `requestedAfter`, `requestedBefore`.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `status` | string | Filter by status |
| `requestedAfter` | string | Fees requested after this timestamp |
| `requestedBefore` | string | Fees requested before this timestamp |

---

### Charges

#### GET /charges — List charges

**No date filters.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Default 20 |
| `after` | string | Pagination cursor |
| `portfolioId` | string | Filter by portfolio ID |
| `clientReference` | string | Filter by client reference |
| `status` | string | Filter by status |

---

### Other Endpoints (not detailed above)

| Endpoint | Date Filters | Notes |
|----------|-------------|-------|
| `GET /isa-subscriptions` | None | Filter by accountId, taxYear |
| `GET /isa-declarations` | None | Filter by accountId, partyId, taxYear, isaType |
| `GET /balances/totals` | None | Filter by portfolioId |
| `GET /balances/cash` | — | Not fully researched |
| `GET /balances/holdings` | — | Not fully researched |
| `GET /performance` | — | Not fully researched |
| `GET /transfers/inbound` | — | Not fully researched |
| `GET /transfers/outbound` | — | Not fully researched |
| `GET /transfers/internal` | — | Not fully researched |
| `GET /due-diligence/updates/person` | — | Not fully researched |
| `GET /pension-income-payments` | — | Not fully researched |
| `GET /bonuses` | — | Not fully researched |
| `GET /w8bens` | — | Not fully researched |
| `GET /sipp/illustrations/accumulation` | — | Not fully researched |

---

## Webhooks

WealthKernel supports **real-time push notifications** via HTTPS POST webhooks.

### Webhook Shape

```json
{
  "eventId": "a1db5d50-f783-456c-973e-d9a39c7fd874",
  "eventType": {
    "name": "webhooks.test",
    "version": 1
  },
  "payload": { ... },
  "occurredAt": "2019-10-08T13:55:4237925Z"
}
```

### Known Event Types (from TOC)

| Event | Description |
|-------|-------------|
| `account.created.v1` | Account was created |
| `account.activated.v1` | Account was activated |
| `account.suspended.v1` | Account was suspended |
| `account.unsuspended.v1` | Account was unsuspended |
| `account.closing.v1` | Account is closing |
| `account.closed.v1` | Account was closed |
| `account.closure-cancelled.v1` | Account closure was cancelled |
| `bank-account.activated.v1` | Bank account activated |
| `bank-account.deactivated.v1` | Bank account deactivated |
| `bank-account.suspended.v1` | Bank account suspended |
| `deposit.created.v1` | Deposit created |
| `order.matched.v1` | Order matched |

> Full event list is in the Stoplight docs under Schemas > Webhooks. Additional events
> exist for deposits, withdrawals, orders, transactions, transfers, etc. Fetch from
> the TOC node for the complete list.

### Setup

1. Create a webhook secret via the WealthKernel portal
2. Create an HTTPS endpoint that accepts JSON and returns `2xx`
3. Subscribe to event types in the portal
4. Verify requests using the `Webhook-Signature` header (HMAC SHA-256)

---

## Connector Strategy: Incremental Sync

### The Problem

Not all endpoints support date-based filtering. This table summarizes what's available:

| Resource | Incremental Filter | Best Sync Strategy |
|----------|-------------------|--------------------|
| Transactions | `updatedSince` | Poll with last sync timestamp |
| Orders | `receivedAfter` | Poll with last sync timestamp |
| Deposits | `startDate` | Poll with last sync date |
| Valuations | `updatedSince` | Poll with last sync timestamp |
| Fees | `requestedAfter` | Poll with last sync timestamp |
| **Accounts** | **None** | Webhook or full scan + diff |
| **Parties** | **None** | Webhook or full scan + diff |
| **Portfolios** | **None** | Webhook or full scan + diff |
| **Addresses** | **None** | Full scan + diff |
| **Bank Accounts** | **None** | Webhook or full scan + diff |
| **Withdrawals** | **None** | Full scan + diff |
| **Charges** | **None** | Full scan + diff |

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONNECTOR SERVICE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WEBHOOK RECEIVER (real-time)                               │
│  ├── account.created/activated/closed → upsert accounts     │
│  ├── deposit.created → upsert deposits                      │
│  ├── order.matched → upsert orders                          │
│  └── ... other events                                       │
│                                                             │
│  INCREMENTAL POLLER (every 15 min)                          │
│  ├── GET /transactions?updatedSince={last_sync}             │
│  ├── GET /orders?receivedAfter={last_sync}                  │
│  ├── GET /deposits?startDate={last_sync_date}               │
│  ├── GET /valuations?updatedSince={last_sync}               │
│  └── GET /fees?requestedAfter={last_sync}                   │
│                                                             │
│  FULL SCAN RECONCILER (every 1-6 hours)                     │
│  ├── GET /accounts (all pages) → diff by id + addedAt       │
│  ├── GET /parties (all pages) → diff by id                  │
│  ├── GET /portfolios (all pages) → diff by id               │
│  ├── GET /withdrawals (all pages) → diff by id              │
│  └── GET /bank-accounts (all pages) → diff by id            │
│                                                             │
│  STATE STORE                                                │
│  ├── last_sync_timestamp per resource type                  │
│  ├── known entity IDs + hashes for diffing                  │
│  └── Pagination-Last cursors (transient, per-run only)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Notes for the Implementing Agent

1. **Rate limiting**: The API returns `429 Too Many Requests`. Implement exponential
   backoff. The exact rate limit values are not published — be conservative.

2. **Pagination cursors are ephemeral**: Never persist `Pagination-Last` values between
   runs. They are opaque, potentially non-deterministic, and only valid within a single
   pagination sequence.

3. **`updatedSince` vs `startDate`**: These filter on different things.
   - `updatedSince` catches modifications (status changes, corrections) — best for sync
   - `startDate`/`endDate` filter on creation/event date — useful but misses updates
   - Where both exist (transactions, valuations), prefer `updatedSince`

4. **Accounts have no date filter at all**: For a connector that needs "accounts created
   after X", you must fetch all accounts and filter client-side on the `addedAt` field.
   This is fine for low-volume resources like accounts.

5. **Webhook reliability**: Webhooks can fail or be missed. The full scan reconciler
   acts as a safety net. Run it less frequently (hourly or every few hours) to catch
   anything the webhook receiver missed.

6. **Idempotency**: The API supports idempotent requests via an idempotency key header.
   Use this when creating resources to avoid duplicates on retry.

7. **Eventual consistency**: The API docs explicitly mention eventual consistency.
   A resource created via POST may not appear immediately in a subsequent GET list call.
   Build in a small delay or handle gracefully.

8. **Auth token management**: Tokens come from OAuth2 client credentials flow. Cache
   the token and refresh before expiry. Do not request a new token on every API call.

9. **Date format**: All timestamps are ISO 8601 with high-precision fractional seconds
   and `Z` suffix, e.g. `2021-03-13T16:41:16.4237925Z`. Python's `datetime.fromisoformat`
   handles this in 3.11+ — for older versions, replace `Z` with `+00:00`.

10. **The `after` pagination param**: This is a cursor token, not a date or offset.
    You get it from the `Pagination-Last` response header of the previous call. First
    call omits `after`; subsequent calls pass the header value. Loop until the header
    is absent.

### How to Scrape More Endpoints

If you need details on endpoints not fully documented above, use this pattern:

```bash
# 1. Get the table of contents (finds node IDs)
curl -s "https://docs.wealthkernel.com/api/v1/projects/cHJqOjc4Nzg2/table-of-contents"

# 2. Fetch a specific node by ID (returns full OpenAPI operation data in the `data` field)
curl -s "https://docs.wealthkernel.com/api/v1/projects/cHJqOjc4Nzg2/nodes/{nodeId}"
```

The `data` field in the node response is a JSON string containing the full OpenAPI
operation spec — method, path, parameters, request/response schemas, and examples.

### Key Node IDs (for reference)

| Endpoint | Node ID |
|----------|---------|
| List accounts | `2741f60c63f5a` |
| List parties | `9d757633f6de7` |
| List portfolios | `6d550c973644f` |
| List transactions | `894693cb0c149` |
| List orders | `4dbde76852552` |
| List deposits | `40895cfea9889` |
| List withdrawals | `7cb8b5451d3e4` |
| List valuations | `7a95a1e412e83` |
| List fees | `2658b1c77b376` |
| List charges | `3ec0cdc9b27a4` |
| List bank accounts | `0d106a6ed6c61` |
| List addresses | `d29ebd35ee47f` |
| Pagination (article) | `62138d68ed43b` |
| Webhooks (article) | `b01ce29eab852` |
