# Session Logs Directory

This directory stores SSH session logs for debugging and auditing purposes.

## Contents

Session log files are created when devices have `session_log` enabled:

- `{device_name}.log` - SSH session transcript for each device

## Important Notes

- This directory is **excluded from git** (see `.gitignore`)
- Logs are created only when `session_log: true` in device configuration
- Logs contain sensitive information (commands, outputs)
- Files grow over time and should be rotated/archived regularly

## Security Considerations

⚠️ **Session logs may contain sensitive information:**
- Commands executed
- Device outputs
- Configuration data
- Credentials (if shown in output)

**Best Practices:**
- Limit access to this directory
- Regularly archive and delete old logs
- Consider encryption for long-term storage
- Review logs for sensitive data before sharing

## Log Rotation

Example log rotation script:

```bash
#!/bin/bash
# Compress logs older than 7 days
find session_logs/ -name "*.log" -mtime +7 -exec gzip {} \;

# Delete compressed logs older than 30 days
find session_logs/ -name "*.log.gz" -mtime +30 -delete
```

See [DEPLOYMENT.md](../DEPLOYMENT.md) for production log management.
