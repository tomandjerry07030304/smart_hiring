"""
Security Module - Enhanced Security Features
Includes RBAC, rate limiting, encryption

NOTE: TwoFactorAuth was REMOVED on 2026-01-06 because it was dead code.
      The implementation existed but was NEVER integrated into auth flows.
      Dead security code is worse than no security code - it's deceptive.
      
      To re-enable 2FA:
      1. Uncomment the import below
      2. Add 2FA routes to auth_routes.py (/api/auth/2fa/setup, /api/auth/2fa/verify)
      3. Add user schema fields (two_factor_enabled, two_factor_secret)
      4. Enforce 2FA check in login flow
"""

# REMOVED: from .two_factor_auth import TwoFactorAuth  # Dead code - not integrated
from .rbac import RBACManager, require_permission
from .rate_limiter import RateLimiter
from .encryption import EncryptionManager

__all__ = ['RBACManager', 'require_permission', 'RateLimiter', 'EncryptionManager']
# NOTE: TwoFactorAuth intentionally excluded - see comment above
