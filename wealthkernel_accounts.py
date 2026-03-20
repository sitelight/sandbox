"""
WealthKernel API client for listing and paginating through accounts.

API Reference: https://docs.wealthkernel.com/docs/api/2021-05-17/operations/list-accounts
Pagination:    https://docs.wealthkernel.com/docs/api/pagination

IMPORTANT: The WealthKernel List Accounts endpoint (GET /accounts) does NOT support
filtering by creation date (there is no createdAfter, createdFrom, or similar parameter).
The available filters are: accountId, clientReference, type, status, productId, owner,
registeredContact, child, and beneficiary.

To get accounts created after a given date, you must fetch all accounts (with optional
filters) and filter client-side by the `addedAt` timestamp field.
"""

from datetime import datetime, timezone
from typing import Any, Generator, Optional

import requests


API_VERSION = "2021-05-17"
SANDBOX_BASE_URL = "https://api.sandbox.wealthkernel.io"
PRODUCTION_BASE_URL = "https://api.wealthkernel.io"

DEFAULT_LIMIT = 20


def list_accounts_page(
    token: str,
    *,
    base_url: str = SANDBOX_BASE_URL,
    limit: int = DEFAULT_LIMIT,
    after: Optional[str] = None,
    account_type: Optional[str] = None,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    product_id: Optional[str] = None,
    client_reference: Optional[str] = None,
) -> tuple[list[dict[str, Any]], Optional[str]]:
    """
    Fetch a single page of accounts from the WealthKernel API.

    Args:
        token: Bearer token for authentication.
        base_url: API base URL (sandbox or production).
        limit: Max number of accounts per page (default 20).
        after: Pagination cursor from previous response's Pagination-Last header.
        account_type: Filter by type: GIA, ISA, JISA, SIA, SIPP.
        status: Filter by status: Pending, Active, Suspended, Closing, Closed.
        owner: Filter by owner party ID (ISAs, GIAs, SIAs).
        product_id: Filter by product ID.
        client_reference: Filter by client reference.

    Returns:
        Tuple of (list of account dicts, next_cursor or None if no more pages).
    """
    params: dict[str, Any] = {"limit": limit}
    if after is not None:
        params["after"] = after
    if account_type is not None:
        params["type"] = account_type
    if status is not None:
        params["status"] = status
    if owner is not None:
        params["owner"] = owner
    if product_id is not None:
        params["productId"] = product_id
    if client_reference is not None:
        params["clientReference"] = client_reference

    resp = requests.get(
        f"{base_url}/accounts",
        params=params,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept-Version": API_VERSION,
            "Accept": "application/json",
        },
    )
    resp.raise_for_status()

    accounts = resp.json()
    next_cursor = resp.headers.get("Pagination-Last")
    return accounts, next_cursor


def list_all_accounts(
    token: str,
    *,
    base_url: str = SANDBOX_BASE_URL,
    limit: int = DEFAULT_LIMIT,
    account_type: Optional[str] = None,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    product_id: Optional[str] = None,
    client_reference: Optional[str] = None,
) -> Generator[dict[str, Any], None, None]:
    """
    Paginate through all accounts, yielding each account dict.

    Accepts the same filters as list_accounts_page.
    """
    cursor = None
    while True:
        accounts, next_cursor = list_accounts_page(
            token,
            base_url=base_url,
            limit=limit,
            after=cursor,
            account_type=account_type,
            status=status,
            owner=owner,
            product_id=product_id,
            client_reference=client_reference,
        )
        yield from accounts
        if next_cursor is None:
            break
        cursor = next_cursor


def list_accounts_created_after(
    token: str,
    created_after: datetime,
    *,
    base_url: str = SANDBOX_BASE_URL,
    limit: int = DEFAULT_LIMIT,
    account_type: Optional[str] = None,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    product_id: Optional[str] = None,
    client_reference: Optional[str] = None,
) -> Generator[dict[str, Any], None, None]:
    """
    Paginate through all accounts and yield only those created after the given date.

    NOTE: The WealthKernel API does not support server-side date filtering on the
    List Accounts endpoint. This function fetches all accounts matching the other
    filters and performs client-side filtering on the `addedAt` field.

    Args:
        token: Bearer token for authentication.
        created_after: Only yield accounts with addedAt after this datetime.
                       Should be timezone-aware (UTC recommended).
        base_url: API base URL.
        limit: Page size.
        account_type: Filter by type: GIA, ISA, JISA, SIA, SIPP.
        status: Filter by status: Pending, Active, Suspended, Closing, Closed.
        owner: Filter by owner party ID.
        product_id: Filter by product ID.
        client_reference: Filter by client reference.

    Yields:
        Account dicts where addedAt > created_after.
    """
    if created_after.tzinfo is None:
        created_after = created_after.replace(tzinfo=timezone.utc)

    for account in list_all_accounts(
        token,
        base_url=base_url,
        limit=limit,
        account_type=account_type,
        status=status,
        owner=owner,
        product_id=product_id,
        client_reference=client_reference,
    ):
        added_at_str = account.get("addedAt")
        if added_at_str is None:
            continue
        # WealthKernel timestamps look like "2021-03-13T16:41:16.4237925Z"
        # Python's fromisoformat handles this in 3.11+; for older versions
        # we strip trailing Z and treat as UTC.
        added_at = datetime.fromisoformat(
            added_at_str.replace("Z", "+00:00")
        )
        if added_at > created_after:
            yield account


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    bearer_token = os.environ["WEALTHKERNEL_TOKEN"]

    cutoff = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for acct in list_accounts_created_after(bearer_token, cutoff):
        print(f"{acct['id']}  {acct.get('name')}  {acct.get('addedAt')}")
