# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email security concerns to: [Your Email]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

Response time: Within 48 hours

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Keep dependencies updated** - Run `pip list --outdated` regularly
3. **Use HTTPS only** - Enforce in production
4. **Rate limit APIs** - Prevent abuse
5. **Validate all inputs** - Prevent injection attacks
6. **Use latest Python** - Security patches matter
7. **Monitor logs** - Watch for suspicious activity

## Known Security Considerations

- JWT tokens don't expire (TODO: Add expiration)
- No rate limiting on API endpoints (TODO: Add)
- CORS currently open to all origins (TODO: Restrict in production)
- No 2FA support (TODO: Add for admin accounts)

## Security Updates

Check CHANGELOG.md for security-related updates.
