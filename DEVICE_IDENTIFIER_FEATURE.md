# Device Identifier Feature - Dual Support for ID/Name/IP

## Overview

The API now supports referencing devices by **ID**, **Name**, or **IP Address** in all endpoints. This makes the API more user-friendly and flexible.

## Implementation Summary

### Smart Lookup Function

Added `get_device_by_identifier()` in `app/database.py`:
- **Priority Order**: ID (if numeric) → Name → IP Address
- **Error Handling**: Returns 404 with descriptive message if device not found
- **Performance**: Minimal overhead - stops at first match

### Modified Endpoints

#### Device Management (`app/routers/devices.py`)
- `GET /devices/{device_identifier}` - Get device details
- `PUT /devices/{device_identifier}` - Update device
- `DELETE /devices/{device_identifier}` - Delete device
- `POST /devices/{device_identifier}/test` - Test connection

#### Command Execution (`app/routers/commands.py`)
- `POST /devices/{device_identifier}/execute` - Execute single command
- `POST /devices/{device_identifier}/execute-batch` - Execute batch commands
- `GET /devices/{device_identifier}/config` - Get device configuration
- `POST /devices/{device_identifier}/config` - Update device configuration
- `GET /devices/{device_identifier}/interfaces` - Get interface status

## Usage Examples

### By Device ID (backward compatible)

```bash
# Execute command using numeric ID
curl -X POST "http://localhost:8000/devices/1/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "show version"}'
```

### By Device Name

```bash
# Execute command using device name
curl -X POST "http://localhost:8000/devices/core-switch-01/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "show version"}'
```

### By IP Address

```bash
# Execute command using IP address
curl -X POST "http://localhost:8000/devices/192.168.1.10/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "show version"}'
```

### Other Operations

```bash
# Get device by name
curl -X GET "http://localhost:8000/devices/core-switch-01" \
  -H "Authorization: Bearer $TOKEN"

# Test connection by IP
curl -X POST "http://localhost:8000/devices/192.168.1.10/test" \
  -H "Authorization: Bearer $TOKEN"

# Get configuration by name
curl -X GET "http://localhost:8000/devices/datacenter-router/config" \
  -H "Authorization: Bearer $TOKEN"

# Update device by ID
curl -X PUT "http://localhost:8000/devices/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'
```

## Lookup Priority

The system follows this lookup order:

1. **ID Lookup** - If the identifier is purely numeric (e.g., "1", "42")
   - Fast primary key lookup
   - Returns immediately if found

2. **Name Lookup** - If ID lookup fails or identifier is non-numeric
   - Searches the `name` column (unique constraint)
   - Returns if exact match found

3. **IP Lookup** - If name lookup fails
   - Searches the `host` column (IP address)
   - Returns if exact match found

4. **Not Found** - Returns 404 error with message
   ```json
   {
     "detail": "Device not found with identifier: unknown-device"
   }
   ```

## Edge Cases Handled

### Numeric Device Names
If a device has a numeric name like "123-switch", you can still access it:
- By ID: `/devices/5` (if its ID is 5)
- By Name: `/devices/123-switch` (exact name match)

The system checks ID first only if the identifier is purely numeric.

### Ambiguous Identifiers
- Device name: "192.168.1.10"
- Device IP: "192.168.1.10"

The system prioritizes **name** over **IP**, so it will match the device with that name first.

### IPv6 Addresses
Fully supported:
```bash
curl -X POST "http://localhost:8000/devices/2001:db8::1/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "show version"}'
```

## Benefits

1. **User-Friendly**: No need to remember numeric IDs
2. **Backward Compatible**: Existing ID-based calls still work
3. **Flexible**: Choose the most convenient identifier
4. **Intuitive**: Use device names that match your inventory
5. **Documentation**: Self-documenting API calls with meaningful names

## Performance Considerations

- **ID Lookup**: O(1) - Primary key index
- **Name Lookup**: O(1) - Unique constraint index
- **IP Lookup**: O(1) - Should add index if frequently used (see below)

### Recommended Database Index

For optimal performance with IP lookups, add an index:

```sql
CREATE INDEX idx_device_host ON devices(host);
```

This can be added to the migration or database setup scripts.

## Migration Notes

- **No Breaking Changes**: All existing API calls work unchanged
- **No Database Changes**: Uses existing columns
- **Optional Index**: Add `host` index for better IP lookup performance

## Testing Checklist

- [x] ID-based lookup (backward compatibility)
- [x] Name-based lookup
- [x] IP-based lookup
- [x] 404 error for non-existent devices
- [x] All endpoints updated
- [x] Documentation updated

## Files Modified

1. **app/database.py**
   - Added `get_device_by_identifier()` function
   - Added SQLAlchemy select import
   - Added HTTPException imports

2. **app/routers/devices.py**
   - Changed `{device_id: int}` to `{device_identifier: str}` in 4 endpoints
   - Replaced manual lookups with `get_device_by_identifier()`
   - Updated docstrings

3. **app/routers/commands.py**
   - Changed `{device_id: int}` to `{device_identifier: str}` in 5 endpoints
   - Replaced manual lookups with `get_device_by_identifier()`
   - Updated docstrings

## Future Enhancements

Consider adding:
- Device alias support (multiple names per device)
- Fuzzy matching for device names
- Search endpoint with partial matching
- Bulk operations with mixed identifiers
