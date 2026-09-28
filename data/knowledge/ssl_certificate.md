# SSL Certificate Failure

TLS/SSL validation fails because a certificate is invalid, expired, or incorrectly configured.

Common Causes:
- Expired certificate
- Wrong certificate
- Missing CA
- Incorrect hostname

Evidence:
- Certificate expired
- SSL certificate error
- TLS handshake failure
- certificate verify failed

Diagnostics:
- Check certificate expiry
- Verify hostname
- Check certificate chain

Remediation:
Renew or correctly configure the certificate.

Prevention:
Automated certificate expiry monitoring.