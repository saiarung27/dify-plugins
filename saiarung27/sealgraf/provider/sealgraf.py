import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dify_plugin import ToolProvider
from dify_plugin.entities.credential import CredentialCheckResult
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from sealgraf_client import SealgrafApiError, SealgrafError, client_from_credentials


class SealgrafProvider(ToolProvider):
    def _validate_credentials(
        self, credentials: dict[str, Any]
    ) -> CredentialCheckResult | None:
        """Validate credentials through the Sealgraf setup endpoint.

        Older self-hosted versions use the client's read-only fallback.
        A successful validation records setup separately from purchase checks.
        """
        try:
            client = client_from_credentials(credentials)
        except SealgrafError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
        try:
            client.validate_key()
        except SealgrafApiError as exc:
            if exc.status_code in (401, 403):
                raise ToolProviderCredentialValidationError(
                    "Sealgraf rejected these credentials "
                    f"(HTTP {exc.status_code}): {exc.detail} "
                    "Check that the API key is an agent-scope Sealgraf key "
                    "and that the base URL points at the right deployment."
                ) from exc
            raise ToolProviderCredentialValidationError(
                f"Sealgraf credential check failed (HTTP {exc.status_code}): "
                f"{exc.detail}"
            ) from exc
        except SealgrafError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
        return CredentialCheckResult(
            status="valid", reason_code=None, retryable=False
        )
