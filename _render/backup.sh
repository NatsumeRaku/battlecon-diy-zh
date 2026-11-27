#!/bin/sh
# 每次提交后运行:备份.git到持久区+重建bundle
# Linux 环境沿用 /mnt/agents；Windows(Git Bash)无 /mnt，退化到仓库上级目录的 backup/
cd "$(dirname "$0")/.." || exit 1
if [ -d /mnt ]; then
  BACKUP_DIR=/mnt/agents/backup
  OUTPUT_DIR=/mnt/agents/output
else
  PARENT_DIR="$(cd .. && pwd)"
  BACKUP_DIR="$PARENT_DIR/backup"
  OUTPUT_DIR="$PARENT_DIR/backup"
fi
mkdir -p "$BACKUP_DIR" "$OUTPUT_DIR" || exit 1
tar czf "$BACKUP_DIR/battlecon-diy-zh.git.tar.gz" .git || exit 1
rm -f "$OUTPUT_DIR/battlecon-diy-zh.bundle"
git bundle create "$OUTPUT_DIR/battlecon-diy-zh.bundle" --all || exit 1
echo "backup done: $(git rev-parse --short HEAD) -> $BACKUP_DIR"
