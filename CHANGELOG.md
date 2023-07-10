# Changelog
Last updated: 2023-07-10 11:07 (KST; UTC+9)

## 0.3.2
**Committed 2023-07-10*
- Show skip progress for debug skips
- Enclose post IDs in brackets (`[1a4f6zs]`)
- 
## 0.3.1
**Committed 2023-07-10**
- Hotfix for exceptions killing download loop
- Print Post ID (e.g. `1a4f6zs`) in main loop
- Add debug feature to skip first N saved posts

## 0.3.0
**Committed 2023-07-04**
- Added country detection to warn user of internet censorship

## 0.2.0
**Committed 2023-06-02**
- Now skips file names that already exist on disk
- Tries to clean up unfinished current file upon premature exit (e.g. via Ctrl+C)