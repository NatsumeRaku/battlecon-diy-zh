#!/bin/sh
# 每次提交后运行:备份.git到持久区+重建bundle
cd "$(dirname "$0")/.." || exit 1
mkdir -p /mnt/agents/backup
tar czf /mnt/agents/backup/battlecon-diy-zh.git.tar.gz .git
rm -f /mnt/agents/output/battlecon-diy-zh.bundle
git bundle create /mnt/agents/output/battlecon-diy-zh.bundle --all
echo "backup done: $(git rev-parse --short HEAD)"
