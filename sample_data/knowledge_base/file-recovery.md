---
title: "File Recovery and Version History"
category: "storage_quota"
tags: ["recovery", "version-history", "trash", "deleted-files", "restore"]
summary: "Recover deleted files, restore previous versions, and understand retention policies."
---

# File Recovery and Version History

## Trash Recovery (All Plans)

### Restore from Trash
1. Navigate to Workspace → Trash
2. Find the file/folder
3. Click **Restore** → returns to original location
4. **Available for 30 days** after deletion

### Empty Trash
- **Manual**: Trash → Empty Trash (immediate, irreversible)
- **Auto**: Items auto-deleted after 30 days
- **API**: `POST /api/v1/workspaces/{id}/trash/empty`

### Bulk Restore
- Select multiple items → Restore
- Restores to original locations (creates folders if needed)

## Version History

### Viewing Versions
1. Open file → **Version History** (clock icon)
2. See all versions with: timestamp, author, size, changes
3. Click any version to preview
4. **Restore** to make that version current

### Version Retention by Plan

| Plan | Versions Kept | Retention Period |
|------|---------------|------------------|
| Free | 5 | 30 days |
| Pro | 25 | 90 days |
| Business | 100 | 1 year |
| Enterprise | Unlimited | Unlimited |

### Auto-Cleanup
- Enable: Admin → Workspace → Version Retention
- Configure: keep last N versions, delete older than X days
- Runs daily at 02:00 UTC

## Recovering "Disappeared" Files

### Common Scenarios

**1. Accidentally moved**
- Check parent folders and subfolders
- Use search: `name:"filename" type:file`
- Check audit log for move events

**2. Deleted by another member**
- Trash → filter by "Deleted by"
- Restore if within 30 days
- Check audit log for deletion events

**3. Sync/integration issue**
- Some integrations move files to `.sync-conflicts` folder
- Check: Workspace → `.sync-conflicts`
- Resolve conflicts manually

**4. Workspace storage limit hit**
- Files become read-only, not deleted
- Free up space → files accessible again
- No data loss from quota limits

### If File Not in Trash

1. **Search everywhere**: `GET /api/v1/workspaces/{id}/files/search?q=filename`
2. **Check audit log**: `GET /api/v1/audit?resource_type=file&action=delete`
3. **Contact support** with:
   - Approximate date/time
   - File name or partial name
   - Workspace name
   - Any collaborators who might have moved it

## Enterprise: Point-in-Time Recovery

Enterprise customers can request:
- Workspace restore to specific timestamp (up to 30 days back)
- Requires support ticket with business justification
- Creates new workspace with restored state
- Original workspace unaffected

## Best Practices

- **Name files clearly** — easier to search and recover
- **Use folders** — organized structure reduces accidental moves
- **Enable version retention** — auto-cleanup prevents quota waste
- **Train team on Trash** — 30-day window is generous but not infinite
- **Audit log alerts** — notify admins on bulk deletions

## Related Articles
- [Storage Quota Management](storage-quota.md)
- [Workspace Permissions](workspace-permissions.md)
- [Audit Log Guide](audit-log.md)
- [Backup and Recovery](backup-recovery.md)