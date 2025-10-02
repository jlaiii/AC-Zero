# AC-Zero

**Advanced Cleaning & Reset Tool v1.0**

A comprehensive Windows cleaning tool that resets games to fresh installation state by removing traces, configurations, and anti-cheat system files.

## What It Does

AC-Zero performs deep system cleaning to reset gaming environments by:

- **Process Termination**: Kills Steam, Rust, Epic Games, and anti-cheat processes
- **Steam Deep Clean**: Removes user data, configurations, cache, and logs
- **Rust Data Removal**: Cleans game data, configurations, and traces
- **Epic Games Cleanup**: Removes Epic Games Launcher and Fortnite data
- **Anti-Cheat System Cleanup**: Removes files from EAC, BattlEye, Vanguard, and more
- **Windows System Cleanup**: Cleans prefetch files and recycle bins
- **Registry Cleaning**: Removes gaming-related registry entries
- **Comprehensive Logging**: Detailed statistics and operation tracking

## Important Warnings

- **This tool performs PERMANENT deletions** - use with caution
- **Requires Administrator privileges** to function properly
- **Will terminate running games and launchers** without saving
- **Removes ALL user data** for supported games (saves, settings, etc.)
- **May trigger antivirus warnings** due to process termination and file deletion

## Supported Games & Platforms

### Games
- **Rust** (complete data removal)
- **Steam games** (user data and configurations)
- **Fortnite** (Epic Games data)

### Anti-Cheat Systems
- BattlEye Anti-Cheat
- Easy Anti-Cheat (EAC)
- Riot Vanguard
- EA Anti-Cheat
- PunkBuster
- GameGuard
- Xigncode3
- HackShield
- And many more...

## Usage

### Basic Usage
```bash
python ac-zero.py
```

### Command Line Options
```bash
python ac-zero.py --debug-tools    # Also terminate debugging tools
python ac-zero.py --help          # Show help information
```

## Requirements

- **Windows 10/11** (Administrator privileges required)
- **Python 3.6+**
- **Required Python packages**:
  - `psutil` - Process management
  - `pathlib` - Path handling (built-in)
  - `winreg` - Windows registry access (built-in)

### Install Dependencies
```bash
pip install psutil
```

## What Gets Cleaned

### Steam Data
- User data and profiles
- Configuration files
- Cache and logs
- Shader cache
- Download cache
- Registry entries

### Rust Game Data
- Game configurations
- User profiles
- Analytics data
- Anti-cheat files

### Epic Games Data
- Launcher data
- Fortnite configurations
- Unreal Engine cache
- Analytics data

### Anti-Cheat Systems
- Service files and drivers
- Configuration data
- Log files
- Registry entries

### Windows System
- Game-related prefetch files
- All recycle bins
- Temporary files
- Error reports

## Features

- **Real-time Logging**: See exactly what's being cleaned
- **Size Tracking**: Monitor how much space is being freed
- **Error Handling**: Graceful handling of locked files and permissions
- **Statistics**: Detailed cleanup summary with counts and sizes
- **Multi-method Cleaning**: Uses multiple approaches for thorough cleanup

## Safety Features

- **Graceful Process Termination**: Attempts clean shutdown before force killing
- **Error Recovery**: Continues operation even if some files can't be deleted
- **Detailed Logging**: Full audit trail of all operations
- **Permission Handling**: Skips files that can't be accessed rather than crashing

## Output Example

```
[12:34:56] Starting deep Steam cleanup...
[12:34:57] [+] Found Steam installation: C:\Program Files (x86)\Steam
[12:34:58] [DEL] Removed directory: userdata (245.3 MB)
[12:34:59] [DEL] Removed file: ClientRegistry.blob (2.1 KB)
[12:35:00] [+] Terminated 3 processes
[12:35:01] [+] Cleaned 2 recycle bins, freed 1.2 GB

=== CLEANUP STATISTICS ===
Total Runtime: 45.2 seconds
Processes Killed: 8
Files Deleted: 156
Directories Deleted: 23
Total Space Freed: 2.8 GB
Errors: 2
```

## Links

- **Project Website**: [https://jlaiii.github.io/AC-Zero/](https://jlaiii.github.io/AC-Zero/)
- **Issues & Support**: Create an issue on this repository
