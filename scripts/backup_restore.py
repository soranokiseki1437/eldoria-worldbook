# -*- coding: utf-8 -*-
"""
backup_restore.py — Eldoria 世界书版本备份管理脚本
====================================================
提供 Eldoria.json 的版本备份、列表、恢复、清理功能。

用法：
    python backup_restore.py backup              # 创建一次手动备份
    python backup_restore.py list                # 列出所有备份
    python backup_restore.py list -n 10          # 列出最近10条备份
    python backup_restore.py restore <文件名>     # 从指定备份恢复
    python backup_restore.py restore --latest    # 从最新备份恢复
    python backup_restore.py clean --keep 5      # 仅保留最近5条备份，删除其余
    python backup_restore.py clean --days 30     # 删除30天前的备份
    python backup_restore.py clean --dry-run     # 预览将被删除的备份（不实际删除）
    python backup_restore.py info <文件名>        # 查看指定备份的详细信息

依赖：Python 3.7+（仅标准库）
"""

import json
import os
import sys
import shutil
import re
from datetime import datetime, timedelta

# ─── 路径配置 ───────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)   # 脚本在 scripts/ 下，上级为项目根
OUTPUT_DIR  = os.path.join(PROJECT_DIR, "output")
BACKUP_DIR  = os.path.join(PROJECT_DIR, "backup")
JSON_PATH   = os.path.join(OUTPUT_DIR, "Eldoria_V4.3.json")

# 备份文件名格式: Eldoria_YYYYMMDD_HHMMSS.json
BACKUP_PATTERN = re.compile(r'^Eldoria_(\d{8})_(\d{6})\.json$')


# ─── 工具函数 ───────────────────────────────────────────
def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def get_backup_list(sort_by_time=True):
    """获取所有备份文件列表。
    
    Args:
        sort_by_time: 是否按时间排序（最新在前）
    
    Returns:
        list[dict]: 每个元素包含 name, path, timestamp, size, entry_count
    """
    if not os.path.exists(BACKUP_DIR):
        return []

    backups = []
    for fname in os.listdir(BACKUP_DIR):
        m = BACKUP_PATTERN.match(fname)
        if not m:
            continue

        fpath = os.path.join(BACKUP_DIR, fname)
        date_str = m.group(1)  # YYYYMMDD
        time_str = m.group(2)  # HHMMSS

        # 解析时间戳
        try:
            ts = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        except ValueError:
            continue

        size = os.path.getsize(fpath)
        entry_count = _count_entries(fpath)

        backups.append({
            "name": fname,
            "path": fpath,
            "timestamp": ts,
            "size": size,
            "entry_count": entry_count,
        })

    if sort_by_time:
        backups.sort(key=lambda b: b["timestamp"], reverse=True)

    return backups


def _count_entries(filepath):
    """快速统计 JSON 文件中的条目数（不完整解析，只数 entries 数组内 uid 的个数）"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        # 统计 "uid": 的出现次数作为条目数估算
        count = 0
        for match in re.finditer(r'"uid"\s*:\s*\d+', text):
            count += 1
        return count
    except Exception:
        return -1


def format_size(size_bytes):
    """将字节数格式化为人类可读的字符串"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ─── 核心功能 ───────────────────────────────────────────
def create_backup(silent=False):
    """创建一次手动备份。
    
    Args:
        silent: 如果为 True，不打印信息（用于脚本调用）
    
    Returns:
        str: 备份文件路径，如果源文件不存在则返回 None
    """
    if not os.path.exists(JSON_PATH):
        print("[error] Eldoria.json 不存在，无法备份")
        return None

    ensure_dir(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"Eldoria_{timestamp}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    shutil.copy2(JSON_PATH, backup_path)

    size = format_size(os.path.getsize(backup_path))
    if not silent:
        print(f"[backup] 已创建备份: {backup_name} ({size})")

    return backup_path


def list_backups(limit=None):
    """列出所有备份及其信息。
    
    Args:
        limit: 最多显示条数（None = 全部）
    """
    backups = get_backup_list()
    if not backups:
        print("暂无备份")
        return

    if limit:
        backups = backups[:limit]

    # 计算列宽
    max_name_len = max(len(b["name"]) for b in backups)
    name_col = max(max_name_len, 28)

    print(f"\n{'#':>4}  {'备份文件':<{name_col}}  {'时间':<19}  {'大小':>8}  {'条目':>5}")
    print("-" * (4 + 1 + name_col + 1 + 19 + 1 + 8 + 1 + 5))

    for i, b in enumerate(backups, 1):
        ts_str = b["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        size_str = format_size(b["size"])
        entry_str = str(b["entry_count"]) if b["entry_count"] >= 0 else "?"
        print(f"{i:>4}  {b['name']:<{name_col}}  {ts_str}  {size_str:>8}  {entry_str:>5}")

    total_size = sum(b["size"] for b in backups)
    print("-" * (4 + 1 + name_col + 1 + 19 + 1 + 8 + 1 + 5))
    print(f"共 {len(backups)} 条备份，总占用 {format_size(total_size)}")

    if limit and limit < len(get_backup_list()):
        print(f"(仅显示最近 {limit} 条，使用 list 查看全部)")


def restore_backup(backup_name=None, use_latest=False, force=False):
    """从指定备份恢复 Eldoria.json。
    
    Args:
        backup_name: 备份文件名
        use_latest: 使用最新备份
        force: 跳过确认提示（用于脚本调用）
    """
    if use_latest:
        backups = get_backup_list()
        if not backups:
            print("[error] 没有可用的备份")
            return False
        backup_name = backups[0]["name"]
        print(f"[restore] 使用最新备份: {backup_name}")

    if not backup_name:
        print("[error] 请指定备份文件名，或使用 --latest")
        return False

    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        print(f"[error] 备份文件不存在: {backup_name}")
        return False

    # 验证备份文件是否是合法的 JSON
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        print(f"[error] 备份文件 JSON 格式无效: {e}")
        return False

    # 确认
    if not force:
        size = format_size(os.path.getsize(backup_path))
        m = BACKUP_PATTERN.match(backup_name)
        ts_info = ""
        if m:
            ts = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y%m%d_%H%M%S")
            ts_info = ts.strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n即将从以下备份恢复 Eldoria.json:")
        print(f"  文件: {backup_name}")
        if ts_info:
            print(f"  时间: {ts_info}")
        print(f"  大小: {size}")
        print(f"\n当前 Eldoria.json 将被覆盖。")

        confirm = input("确认恢复? (y/N): ").strip().lower()
        if confirm not in ('y', 'yes'):
            print("[restore] 已取消")
            return False

    # 先备份当前文件（如果存在）
    if os.path.exists(JSON_PATH):
        create_backup(silent=True)

    # 执行恢复
    shutil.copy2(backup_path, JSON_PATH)
    print(f"[restore] 已从 {backup_name} 恢复 Eldoria.json")
    return True


def clean_backups(keep=None, days=None, dry_run=False):
    """清理旧备份。
    
    Args:
        keep: 保留最近 N 条备份
        days: 删除 N 天前的备份
        dry_run: 仅预览，不实际删除
    """
    backups = get_backup_list()

    if not backups:
        print("没有可清理的备份")
        return

    to_delete = []

    if keep is not None:
        if keep <= 0:
            print("[error] --keep 必须大于 0")
            return
        to_delete = backups[keep:]  # 前 keep 条保留

    elif days is not None:
        if days <= 0:
            print("[error] --days 必须大于 0")
            return
        cutoff = datetime.now() - timedelta(days=days)
        to_delete = [b for b in backups if b["timestamp"] < cutoff]

    else:
        print("[error] 请指定 --keep N 或 --days N")
        return

    if not to_delete:
        print("没有需要清理的备份")
        return

    # 显示将被删除的备份
    total_del_size = sum(b["size"] for b in to_delete)
    print(f"\n{'#':>4}  {'备份文件':<30}  {'时间':<19}  {'大小':>8}")
    print("-" * (4 + 1 + 30 + 1 + 19 + 1 + 8))
    for i, b in enumerate(to_delete, 1):
        ts_str = b["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        size_str = format_size(b["size"])
        print(f"{i:>4}  {b['name']:<30}  {ts_str}  {size_str:>8}")
    print("-" * (4 + 1 + 30 + 1 + 19 + 1 + 8))
    print(f"将删除 {len(to_delete)} 条备份，释放 {format_size(total_del_size)}")

    if dry_run:
        print("[dry-run] 预览模式，未实际删除")
        return

    # 确认
    confirm = input("\n确认删除? (y/N): ").strip().lower()
    if confirm not in ('y', 'yes'):
        print("[clean] 已取消")
        return

    # 执行删除
    for b in to_delete:
        os.remove(b["path"])
        print(f"  已删除: {b['name']}")

    print(f"[clean] 清理完成，已删除 {len(to_delete)} 条备份，释放 {format_size(total_del_size)}")


def show_info(backup_name):
    """显示指定备份的详细信息。
    
    Args:
        backup_name: 备份文件名
    """
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        # 尝试用编号查找
        backups = get_backup_list()
        try:
            idx = int(backup_name) - 1
            if 0 <= idx < len(backups):
                backup_path = backups[idx]["path"]
                backup_name = backups[idx]["name"]
            else:
                print(f"[error] 无效的索引: {backup_name}")
                return
        except ValueError:
            print(f"[error] 备份文件不存在: {backup_name}")
            return

    # 基本信息
    m = BACKUP_PATTERN.match(backup_name)
    stat = os.stat(backup_path)

    print(f"\n备份文件: {backup_name}")
    print(f"路径:     {backup_path}")
    print(f"大小:     {format_size(stat.st_size)}")

    if m:
        ts = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y%m%d_%H%M%S")
        print(f"时间:     {ts.strftime('%Y-%m-%d %H:%M:%S')}")
        ago = datetime.now() - ts
        print(f"距今:     {_format_timedelta(ago)}")

    # JSON 内容概览
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\n[warning] JSON 解析失败: {e}")
        return

    char = data.get("character", {})
    wb = char.get("world_book", {})
    entries = wb.get("entries", [])

    print(f"\n世界书名称: {wb.get('name', '(未命名)')}")
    print(f"条目数量:   {len(entries)}")

    if entries:
        uids = sorted(e.get("uid", -1) for e in entries)
        print(f"UID 范围:   {uids[0]} - {uids[-1]}")

        # 分组统计
        groups = {}
        for e in entries:
            g = e.get("group", "") or "(无分组)"
            groups[g] = groups.get(g, 0) + 1
        if groups:
            print("分组统计:")
            for g, cnt in sorted(groups.items()):
                print(f"  {g}: {cnt} 条")

    print(f"\n角色名称: {char.get('name', '(无)')}")
    print(f"规范版本: {data.get('spec_version', '(无)')}")


def _format_timedelta(td):
    """将 timedelta 格式化为人类可读的字符串"""
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}天")
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if not parts:
        return "不到1分钟"
    return "".join(parts)


# ─── 命令行解析 ─────────────────────────────────────────
def print_usage():
    """打印使用说明"""
    print(__doc__)
    # 同时打印当前备份统计
    backups = get_backup_list()
    if backups:
        total_size = sum(b["size"] for b in backups)
        print(f"\n当前状态: {len(backups)} 条备份, 总占用 {format_size(total_size)}")
    else:
        print("\n当前状态: 暂无备份")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    cmd = sys.argv[1].lower()

    if cmd == "backup":
        create_backup()

    elif cmd == "list":
        limit = None
        # 解析 -n
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == "-n" and i + 1 < len(sys.argv):
                try:
                    limit = int(sys.argv[i + 1])
                except ValueError:
                    print(f"[error] -n 参数必须是数字: {sys.argv[i + 1]}")
                    return
                break
        list_backups(limit=limit)

    elif cmd == "restore":
        if "--latest" in sys.argv:
            restore_backup(use_latest=True)
        elif len(sys.argv) >= 3:
            restore_backup(backup_name=sys.argv[2])
        else:
            # 交互式选择
            backups = get_backup_list()
            if not backups:
                print("没有可用的备份")
                return
            list_backups(limit=10)
            choice = input("\n请输入要恢复的备份编号 (输入 q 取消): ").strip()
            if choice.lower() in ('q', 'quit', ''):
                print("[restore] 已取消")
                return
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(backups):
                    restore_backup(backup_name=backups[idx]["name"])
                else:
                    print(f"[error] 无效的编号: {choice}")
            except ValueError:
                # 当作文件名处理
                restore_backup(backup_name=choice)

    elif cmd == "clean":
        keep = None
        days = None
        dry_run = "--dry-run" in sys.argv

        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == "--keep" and i + 1 < len(sys.argv):
                try:
                    keep = int(sys.argv[i + 1])
                except ValueError:
                    print(f"[error] --keep 参数必须是数字: {sys.argv[i + 1]}")
                    return
            elif arg == "--days" and i + 1 < len(sys.argv):
                try:
                    days = int(sys.argv[i + 1])
                except ValueError:
                    print(f"[error] --days 参数必须是数字: {sys.argv[i + 1]}")
                    return

        if keep is None and days is None:
            print("[error] 请指定 --keep N 或 --days N")
            print("示例: python backup_restore.py clean --keep 5")
            print("示例: python backup_restore.py clean --days 30 --dry-run")
            return

        clean_backups(keep=keep, days=days, dry_run=dry_run)

    elif cmd == "info":
        if len(sys.argv) < 3:
            # 交互式选择
            backups = get_backup_list()
            if not backups:
                print("没有可用的备份")
                return
            list_backups(limit=10)
            choice = input("\n请输入要查看的备份编号 (输入 q 取消): ").strip()
            if choice.lower() in ('q', 'quit', ''):
                print("[info] 已取消")
                return
            show_info(choice)
        else:
            show_info(sys.argv[2])

    elif cmd in ("help", "-h", "--help"):
        print_usage()

    else:
        print(f"[error] 未知命令: {cmd}")
        print_usage()


if __name__ == "__main__":
    main()