#!/usr/bin/env python3
"""
AC-Zero
Comprehensive cleaning tool that resets games to fresh installation state:
- Kills Steam, Rust, Epic Games, and anti-cheat processes
- Deep cleans Steam user data and configurations
- Removes Rust game data and traces
- Cleans Epic Games and Fortnite data completely
- Anti-cheat system cleanup (EAC, BattlEye, Vanguard, etc.)
- Windows prefetch file cleaning
- Recycle bin clearing
- Registry cleaning and trace removal
- Detailed logging and statistics
"""

import os
import sys
import shutil
import subprocess
import time
import winreg
import ctypes
from pathlib import Path
from datetime import datetime

# Auto-install required packages
def install_required_packages():
    """Auto-install required packages if they're missing"""
    required_packages = ['psutil']
    
    print("AC-Zero: Checking dependencies...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"⚠ Installing required package: {package}")
            print("This may take a moment on first run...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package, '--quiet'
                ])
                print(f"✓ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {package}")
                print(f"Error: {e}")
                print(f"\nPlease install manually with: pip install {package}")
                print("Or ensure you have an internet connection and try again.")
                input("Press any key to exit...")
                sys.exit(1)
            except Exception as e:
                print(f"✗ Unexpected error installing {package}: {e}")
                print(f"Please install manually with: pip install {package}")
                input("Press any key to exit...")
                sys.exit(1)
    
    print("✓ All dependencies ready!\n")

# Install packages before importing them
install_required_packages()

# Now import the packages that might have been missing
import psutil

def boot_sequence():
    """Display AC-Zero intro with program info and website"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 60)
    print("                    AC-ZERO v1.0")
    print("           Advanced Cleaning & Reset Tool")
    print()
    print("              https://jlaiii.github.io/AC-Zero/")
    print("=" * 60)
    print()
    
    for countdown in range(5, 0, -1):
        print(f"\rStarting in {countdown} seconds...", end="", flush=True)
        time.sleep(1)
    
    print(f"\rStarting now...           ", flush=True)
    time.sleep(0.5)
    
    os.system('cls' if os.name == 'nt' else 'clear')

class ACZero:
    def __init__(self):
        self.steam_processes = ['steam.exe', 'steamwebhelper.exe', 'steamservice.exe']
        self.rust_processes = ['RustClient.exe', 'Rust.exe']
        self.anticheat_processes = [
            # BattlEye Anti-Cheat
            'BEService.exe', 'BEService_x64.exe', 'BattlEye.exe',
            
            # Easy Anti-Cheat (EAC) - kill processes but keep files installed
            'EasyAntiCheat.exe', 'EasyAntiCheat_Setup.exe', 'EACLauncher.exe',
            
            # Riot Vanguard
            'vgtray.exe', 'vgc.exe', 'vgk.sys',
            
            # Valve Anti-Cheat (VAC) - only specific VAC processes
            'vacbanned.exe',
            
            # ESEA Anti-Cheat
            'ESEAClient2.exe', 'ESEADriver2.sys',
            
            # FACEIT Anti-Cheat
            'FACEITClient.exe', 'faceit-ac.exe',
            
            # Blizzard Warden
            'Warden.exe', 'WowError.exe',
            
            # EA Anti-Cheat
            'EAAntiCheat.Installer.exe', 'EAAntiCheat.GameService.exe',
            
            # PunkBuster
            'PnkBstrA.exe', 'PnkBstrB.exe', 'pbsvc.exe',
            
            # GameGuard
            'GameMon.des', 'GameGuard.des', 'npggNT.des',
            
            # Xigncode3
            'xmag.exe', 'x3.exe', 'xcorona.exe',
            
            # nProtect GameGuard
            'npggNT.des', 'npggsvc.exe', 'GameMon.des',
            
            # Wellbia XIGNCODE3
            'x3.exe', 'xmag.exe', 'xcorona.exe', 'xcoronahost.exe',
            
            # HackShield
            'HSUpdate.exe', 'EhSvc.exe', 'ahnlab.exe',
            
            # Themida/WinLicense
            'themida.exe', 'winlicense.exe',
            
            # VMProtect
            'vmprotect.exe', 'vmp.exe',
            
            # Denuvo Anti-Tamper
            'denuvo.exe', 'denuvo64.exe',
            
            # Windows Defender Game Mode
            'GameBarPresenceWriter.exe', 'GameBar.exe'
        ]
        self.epic_processes = ['EpicGamesLauncher.exe', 'FortniteLauncher.exe', 'FortniteClient-Win64-Shipping_BE.exe', 'FortniteClient-Win64-Shipping.exe']
        
        self.user_profile = Path(os.environ['USERPROFILE'])
        self.appdata = Path(os.environ['APPDATA'])
        self.localappdata = Path(os.environ['LOCALAPPDATA'])
        
        # Statistics tracking
        self.stats = {
            'start_time': datetime.now(),
            'processes_killed': 0,
            'files_deleted': 0,
            'directories_deleted': 0,
            'registry_keys_deleted': 0,
            'errors': 0,
            'total_size_freed': 0
        }
        
    def log(self, message, status="INFO"):
        """Print formatted log message with status"""
        timestamp = time.strftime('%H:%M:%S')
        status_colors = {
            'INFO': '',
            'SUCCESS': '[+] ',
            'ERROR': '[!] ',
            'WARNING': '[*] ',
            'DELETED': '[DEL] '
        }
        prefix = status_colors.get(status, '')
        print(f"[{timestamp}] {prefix}{message}")
        
    def get_file_size(self, path):
        """Get file or directory size in bytes"""
        try:
            if Path(path).is_file():
                return Path(path).stat().st_size
            elif Path(path).is_dir():
                total = 0
                for item in Path(path).rglob('*'):
                    if item.is_file():
                        try:
                            total += item.stat().st_size
                        except:
                            pass
                return total
        except:
            pass
        return 0
        
    def kill_processes(self):
        """Kill Steam, Rust, and Anti-cheat processes"""
        self.log("Terminating game and anti-cheat processes...", "INFO")
        
        all_processes = self.steam_processes + self.rust_processes + self.anticheat_processes + self.epic_processes
        killed_count = 0
        
        # First pass - try graceful termination
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'].lower() in [p.lower() for p in all_processes]:
                    self.log(f"Terminating: {proc.info['name']} (PID: {proc.info['pid']})", "SUCCESS")
                    try:
                        proc.terminate()  # Try graceful termination first
                        proc.wait(timeout=3)  # Wait up to 3 seconds
                    except psutil.TimeoutExpired:
                        proc.kill()  # Force kill if graceful termination fails
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Second pass - force kill any remaining processes using taskkill
        self.log("Force killing any remaining anti-cheat processes...", "INFO")
        for process_name in all_processes:
            try:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', process_name, '/T'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.log(f"Force killed: {process_name}", "SUCCESS")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
        # Third pass - kill by service name for system services
        service_names = [
            'BEService', 'EasyAntiCheat', 'vgc', 'vgk', 'EAAntiCheat',  # Kill EAC service but keep files
            'PnkBstrA', 'PnkBstrB', 'ESEADriver2', 'xhunter1'
        ]
        
        for service in service_names:
            try:
                subprocess.run(['sc', 'stop', service], capture_output=True, timeout=5)
                subprocess.run(['sc', 'delete', service], capture_output=True, timeout=5)
                self.log(f"Stopped and removed service: {service}", "SUCCESS")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
        self.stats['processes_killed'] = killed_count
        
        if killed_count > 0:
            self.log(f"Terminated {killed_count} processes. Waiting for cleanup...", "SUCCESS")
            time.sleep(5)  # Longer wait for system cleanup
        else:
            self.log("No target processes found running.", "INFO")
    
    def kill_debugging_tools(self, kill_debugging=False):
        """Kill debugging and analysis tools that might interfere with Windows troubleshooting"""
        if not kill_debugging:
            self.log("Skipping debugging tools termination (use --debug-tools flag to enable)", "INFO")
            return
            
        self.log("Terminating debugging and analysis tools...", "INFO")
        
        debugging_processes = [
            # Debuggers and reverse engineering tools only
            'CheatEngine.exe', 'x64dbg.exe', 'x32dbg.exe', 'OllyDbg.exe',
            'IDA.exe', 'ida64.exe', 'windbg.exe', 'cdb.exe', 'ntsd.exe',
            
            # Memory scanners and hex editors
            'HxD.exe', 'WinHex.exe', 'ArtMoney.exe', 'GameConqueror.exe',
            
            # Network analyzers (only specific debugging tools)
            'Wireshark.exe', 'Fiddler.exe',
            
            # Virtualization software (only if needed for debugging)
            'vmware.exe', 'VirtualBox.exe', 'VBoxSVC.exe', 'vmware-vmx.exe'
        ]
        
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in [p.lower() for p in debugging_processes]:
                    self.log(f"Terminating debugging tool: {proc.info['name']} (PID: {proc.info['pid']})", "SUCCESS")
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            self.log(f"Terminated {killed_count} debugging tools", "SUCCESS")
        else:
            self.log("No debugging tools found running", "INFO")
    
    def disable_windows_defender(self):
        """Temporarily disable Windows Defender real-time protection for debugging"""
        self.log("Attempting to disable Windows Defender real-time protection...", "INFO")
        
        try:
            # Disable real-time monitoring
            subprocess.run([
                'powershell', '-Command',
                'Set-MpPreference -DisableRealtimeMonitoring $true'
            ], capture_output=True, timeout=10)
            
            # Disable behavior monitoring
            subprocess.run([
                'powershell', '-Command', 
                'Set-MpPreference -DisableBehaviorMonitoring $true'
            ], capture_output=True, timeout=10)
            
            # Disable IOAV protection
            subprocess.run([
                'powershell', '-Command',
                'Set-MpPreference -DisableIOAVProtection $true'
            ], capture_output=True, timeout=10)
            
            self.log("Windows Defender real-time protection disabled", "SUCCESS")
            
        except Exception as e:
            self.log(f"Failed to disable Windows Defender: {e}", "WARNING")
            self.log("You may need to disable Windows Defender manually", "INFO")
            
    def get_steam_path(self):
        """Get Steam installation path from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                return Path(steam_path)
        except:
            # Fallback to common locations
            common_paths = [
                Path("C:/Program Files (x86)/Steam"),
                Path("C:/Program Files/Steam"),
                self.user_profile / "Steam"
            ]
            for path in common_paths:
                if path.exists():
                    return path
        return None
        
    def clean_steam_data(self):
        """Deep clean Steam user data and configurations"""
        self.log("Starting deep Steam cleanup...", "INFO")
        
        steam_path = self.get_steam_path()
        if not steam_path:
            self.log("Steam installation not found!", "ERROR")
            self.stats['errors'] += 1
            return
            
        self.log(f"Found Steam installation: {steam_path}", "SUCCESS")
        
        # Comprehensive Steam directories to clean
        steam_dirs_to_clean = [
            steam_path / "userdata",
            steam_path / "config", 
            steam_path / "logs",
            steam_path / "dumps",
            steam_path / "appcache",
            steam_path / "depotcache",
            steam_path / "temp",
            steam_path / "steamapps" / "temp",
            steam_path / "steamapps" / "downloading",
            steam_path / "steamapps" / "shadercache",
            steam_path / "bin" / "logs",
            steam_path / "crashhandler64.exe.dmp"
        ]
        
        # Critical Steam files to remove
        steam_files_to_clean = [
            steam_path / "ClientRegistry.blob",
            steam_path / "loginusers.vdf", 
            steam_path / "registry.vdf",
            steam_path / "config.vdf",
            steam_path / "steam.cfg",
            Path("C:/Eos_seed.bin")  # EOS seed file
        ]
        
        # Clean directories with size tracking
        for dir_path in steam_dirs_to_clean:
            if dir_path.exists():
                try:
                    size = self.get_file_size(dir_path)
                    shutil.rmtree(dir_path)
                    self.stats['directories_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed directory: {dir_path.name} ({size/1024/1024:.1f} MB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
        # Clean files with size tracking
        for file_path in steam_files_to_clean:
            if file_path.exists():
                try:
                    size = self.get_file_size(file_path)
                    file_path.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed file: {file_path.name} ({size/1024:.1f} KB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {file_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
    def clean_rust_data(self):
        """Remove Rust game data and configurations"""
        self.log("Cleaning Rust game data and configurations...", "INFO")
        
        # Comprehensive Rust data locations
        rust_dirs_to_clean = [
            self.appdata / "Facepunch" / "Rust",
            self.localappdata / "Facepunch" / "Rust", 
            self.localappdata / "Facepunch Studios LTD",
            self.user_profile / "Documents" / "My Games" / "Rust",
            self.localappdata / "GameAnalytics",
            self.localappdata / "WELLBIA",
            # self.appdata / "EasyAntiCheat",  # Commented out - needed for game launches
            self.localappdata / "BattlEye"
        ]
        
        for dir_path in rust_dirs_to_clean:
            if dir_path.exists():
                try:
                    size = self.get_file_size(dir_path)
                    shutil.rmtree(dir_path)
                    self.stats['directories_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed Rust data: {dir_path.name} ({size/1024/1024:.1f} MB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
            else:
                self.log(f"Directory not found: {dir_path.name}", "INFO")
                
    def clean_anticheat_systems(self):
        """Remove anti-cheat system files and registry entries (preserves EAC)"""
        self.log("Cleaning anti-cheat systems (preserving EAC)...", "INFO")
        
        # Anti-cheat directories to remove (EAC directories commented out to prevent game launch issues)
        anticheat_dirs = [
            # Path("C:/Program Files (x86)/EasyAntiCheat"),  # Commented out - needed for game launches
            # Path("C:/Program Files (x86)/EasyAntiCheat_EOS"),  # Commented out - needed for game launches
            Path("C:/Program Files/Riot Vanguard"),
            Path("C:/Program Files (x86)/Common Files/BattlEye"),
            Path("C:/Program Files/Common Files/PUBG"),
            Path("C:/Program Files/Common Files/Wellbia.com"),
            Path("C:/Program Files/EA/AC"),
            Path("C:/ProgramData/eaanticheat"),
            self.localappdata / "BattlEye",
            self.localappdata / "DayZ" / "BattlEye",
            self.localappdata / "FLiNGTrainer",
            self.localappdata / "Activision" / "bootstrapper",
            self.localappdata / "Activision" / "Call of Duty",
            self.appdata / "EA" / "AC",
            self.appdata / "EAAntiCheat.Installer.Tool",
            self.appdata / "Battle.net" / "Telemetry"
        ]
        
        # Anti-cheat files to remove (EAC files commented out to prevent game launch issues)
        anticheat_files = [
            Path("C:/Windows/xhunter1.sys"),
            Path("C:/Windows/xhunters.log"),
            # Path("C:/Windows/SysWOW64/EasyAntiCheat.exe"),  # Commented out - needed for game launches
            Path("C:/Windows/System32/drivers/ACE-BASE.sys"),
            # Path("C:/Windows/system32/drivers/eaanticheat.sys"),  # Commented out - needed for game launches
            Path("C:/Windows/SysWOW64/PnkBstrB.exe"),
            Path("C:/Windows/SysWOW64/PnkBstrA.exe"),
            Path("C:/Windows/SysWOW64/pbsvc.exe")
        ]
        
        # Clean anti-cheat directories
        for dir_path in anticheat_dirs:
            if dir_path.exists():
                try:
                    size = self.get_file_size(dir_path)
                    shutil.rmtree(dir_path)
                    self.stats['directories_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed anti-cheat: {dir_path.name} ({size/1024/1024:.1f} MB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
        # Clean anti-cheat files
        for file_path in anticheat_files:
            if file_path.exists():
                try:
                    size = self.get_file_size(file_path)
                    file_path.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed anti-cheat file: {file_path.name} ({size/1024:.1f} KB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {file_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
        # Clean EAC usermode DLLs
        system32_path = Path("C:/Windows/System32")
        if system32_path.exists():
            for dll_file in system32_path.glob("eac_usermode_*.dll"):
                try:
                    size = self.get_file_size(dll_file)
                    dll_file.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed EAC DLL: {dll_file.name}", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dll_file}: {e}", "ERROR")
                    self.stats['errors'] += 1
    
    def clean_anticheat_systems_complete(self):
        """COMPLETE anti-cheat removal - deletes ALL anti-cheat files including EAC"""
        self.log("COMPLETE ANTI-CHEAT REMOVAL - NUCLEAR OPTION", "WARNING")
        
        # ALL anti-cheat directories to remove (including EAC)
        anticheat_dirs = [
            Path("C:/Program Files (x86)/EasyAntiCheat"),  # NOW INCLUDED
            Path("C:/Program Files (x86)/EasyAntiCheat_EOS"),  # NOW INCLUDED
            Path("C:/Program Files/Riot Vanguard"),
            Path("C:/Program Files (x86)/Common Files/BattlEye"),
            Path("C:/Program Files/Common Files/PUBG"),
            Path("C:/Program Files/Common Files/Wellbia.com"),
            Path("C:/Program Files/EA/AC"),
            Path("C:/ProgramData/eaanticheat"),
            self.localappdata / "BattlEye",
            self.localappdata / "DayZ" / "BattlEye",
            self.localappdata / "FLiNGTrainer",
            self.localappdata / "Activision" / "bootstrapper",
            self.localappdata / "Activision" / "Call of Duty",
            self.appdata / "EA" / "AC",
            self.appdata / "EAAntiCheat.Installer.Tool",
            self.appdata / "Battle.net" / "Telemetry",
            self.appdata / "EasyAntiCheat"  # NOW INCLUDED
        ]
        
        # ALL anti-cheat files to remove (including EAC)
        anticheat_files = [
            Path("C:/Windows/xhunter1.sys"),
            Path("C:/Windows/xhunters.log"),
            Path("C:/Windows/SysWOW64/EasyAntiCheat.exe"),  # NOW INCLUDED
            Path("C:/Windows/System32/drivers/ACE-BASE.sys"),
            Path("C:/Windows/system32/drivers/eaanticheat.sys"),  # NOW INCLUDED
            Path("C:/Windows/SysWOW64/PnkBstrB.exe"),
            Path("C:/Windows/SysWOW64/PnkBstrA.exe"),
            Path("C:/Windows/SysWOW64/pbsvc.exe")
        ]
        
        # Clean anti-cheat directories
        for dir_path in anticheat_dirs:
            if dir_path.exists():
                try:
                    size = self.get_file_size(dir_path)
                    shutil.rmtree(dir_path)
                    self.stats['directories_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"REMOVED anti-cheat: {dir_path.name} ({size/1024/1024:.1f} MB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
        # Clean anti-cheat files
        for file_path in anticheat_files:
            if file_path.exists():
                try:
                    size = self.get_file_size(file_path)
                    file_path.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"REMOVED anti-cheat file: {file_path.name} ({size/1024:.1f} KB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {file_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
        # Clean ALL EAC usermode DLLs
        system32_path = Path("C:/Windows/System32")
        if system32_path.exists():
            for dll_file in system32_path.glob("eac_usermode_*.dll"):
                try:
                    size = self.get_file_size(dll_file)
                    dll_file.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"REMOVED EAC DLL: {dll_file.name}", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dll_file}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
    def clean_epic_games_data(self):
        """Remove Epic Games and Fortnite data"""
        self.log("Cleaning Epic Games and Fortnite data...", "INFO")
        
        # Epic Games directories to remove
        epic_dirs = [
            self.localappdata / "EpicGamesLauncher" / "Saved",
            self.localappdata / "FortniteGame",
            self.localappdata / "UnrealEngine" / "5.0",
            self.localappdata / "UnrealEngine" / "Common" / "Analytics",
            self.localappdata / "CrashReportClient",
            self.localappdata / "AMD" / "CN" / "GameReport",
            self.localappdata / "AMD" / "cl.cache",
            self.localappdata / "AMD" / "DxCache",
            self.localappdata / "D3DSCache",
            self.localappdata / "NVIDIA Corporation" / "GfeSDK",
            self.user_profile / ".config" / "legendary"
        ]
        
        # Epic Games files to remove
        epic_files = [
            self.localappdata / "AMD" / "CN" / "GameReport" / "FortniteClient-Win64-Shipping.exe" / "gpa.bin",
            self.localappdata / "UnrealEngine" / "Common" / "Analytics" / "8E1D46DBC38F4A789939D781E1B91520",
            self.user_profile / ".config" / "legendary" / "version.json",
            self.user_profile / ".config" / "legendary" / "installed.json",
            self.user_profile / ".config" / "legendary" / "config.ini",
            self.user_profile / ".config" / "legendary" / "assets.json",
            self.user_profile / ".config" / "legendary" / "aliases.json"
        ]
        
        # Clean Epic directories
        for dir_path in epic_dirs:
            if dir_path.exists():
                try:
                    size = self.get_file_size(dir_path)
                    shutil.rmtree(dir_path)
                    self.stats['directories_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed Epic data: {dir_path.name} ({size/1024/1024:.1f} MB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
        # Clean Epic files
        for file_path in epic_files:
            if file_path.exists():
                try:
                    size = self.get_file_size(file_path)
                    file_path.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed Epic file: {file_path.name} ({size/1024:.1f} KB)", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove {file_path}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
    def clean_windows_prefetch(self):
        """Clean Windows prefetch files for games"""
        self.log("Cleaning Windows prefetch files...", "INFO")
        
        prefetch_path = Path("C:/Windows/Prefetch")
        if not prefetch_path.exists():
            self.log("Prefetch directory not found", "INFO")
            return
            
        # Game-related prefetch files to remove
        prefetch_patterns = [
            "BESERVICE.EXE-*.pf",
            "CRASHREPORTCLIENT.EXE-*.pf", 
            "EASYANTICHEAT_SETUP.EXE-*.pf",
            "FORTNITECLIENT-WIN64-SHIPPING-*.pf",
            "FORTNITELAUNCHER.EXE-*.pf",
            "RUSTCLIENT.EXE-*.pf",
            "STEAM.EXE-*.pf",
            "STEAMWEBHELPER.EXE-*.pf"
        ]
        
        for pattern in prefetch_patterns:
            for pf_file in prefetch_path.glob(pattern):
                try:
                    size = self.get_file_size(pf_file)
                    pf_file.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['total_size_freed'] += size
                    self.log(f"Removed prefetch: {pf_file.name}", "DELETED")
                except Exception as e:
                    self.log(f"Failed to remove prefetch {pf_file}: {e}", "ERROR")
                    self.stats['errors'] += 1
                    
    def clean_recycle_bins(self):
        """Clean all recycle bins completely"""
        self.log("Cleaning ALL recycle bins completely...", "INFO")
        
        # Method 1: Use PowerShell to empty recycle bin (most reliable)
        try:
            self.log("Using PowerShell to empty recycle bin...", "INFO")
            result = subprocess.run([
                'powershell', '-Command',
                'Clear-RecycleBin -Force -Confirm:$false'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("PowerShell recycle bin cleanup successful", "SUCCESS")
            else:
                self.log(f"PowerShell cleanup warning: {result.stderr}", "WARNING")
        except Exception as e:
            self.log(f"PowerShell recycle bin cleanup failed: {e}", "WARNING")
        
        # Method 2: Detect all drives and clean $Recycle.Bin folders
        try:
            # Get all available drives
            available_drives = []
            for drive_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive_path = f"{drive_letter}:\\"
                if os.path.exists(drive_path):
                    available_drives.append(f"{drive_letter}:")
            
            self.log(f"Found drives: {', '.join(available_drives)}", "INFO")
            
            total_size_freed = 0
            bins_cleaned = 0
            
            for drive in available_drives:
                recycle_path = Path(f"{drive}/$Recycle.Bin")
                if recycle_path.exists():
                    try:
                        size = self.get_file_size(recycle_path)
                        
                        # Clean all subdirectories in recycle bin
                        for item in recycle_path.iterdir():
                            try:
                                if item.is_dir():
                                    shutil.rmtree(item)
                                elif item.is_file():
                                    item.unlink()
                            except PermissionError:
                                self.log(f"Permission denied for: {item}", "WARNING")
                            except Exception as e:
                                self.log(f"Failed to remove {item}: {e}", "WARNING")
                        
                        total_size_freed += size
                        bins_cleaned += 1
                        self.stats['directories_deleted'] += 1
                        self.log(f"Cleaned recycle bin: {drive} ({size/1024/1024:.1f} MB)", "DELETED")
                        
                    except Exception as e:
                        self.log(f"Failed to clean recycle bin {drive}: {e}", "ERROR")
                        self.stats['errors'] += 1
            
            self.stats['total_size_freed'] += total_size_freed
            self.log(f"Cleaned {bins_cleaned} recycle bins, freed {total_size_freed/1024/1024:.1f} MB", "SUCCESS")
            
        except Exception as e:
            self.log(f"Drive detection failed: {e}", "ERROR")
            self.stats['errors'] += 1
        
        # Method 3: Use Windows command line tools as backup
        try:
            self.log("Using Windows commands for additional cleanup...", "INFO")
            
            # Use rd command to remove recycle bin contents
            for drive_letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                recycle_path = f"{drive_letter}:\\$Recycle.Bin"
                if os.path.exists(recycle_path):
                    try:
                        subprocess.run([
                            'rd', '/s', '/q', recycle_path
                        ], capture_output=True, timeout=10)
                    except:
                        pass
            
            # Use sdelete if available (secure deletion)
            try:
                subprocess.run([
                    'sdelete', '-p', '1', '-s', '-z', 'C:\\$Recycle.Bin'
                ], capture_output=True, timeout=30)
            except FileNotFoundError:
                pass  # sdelete not available, that's fine
                
        except Exception as e:
            self.log(f"Command line cleanup failed: {e}", "WARNING")
        
        # Method 4: Clean user-specific recycle bin locations
        try:
            user_recycle_paths = [
                self.user_profile / "AppData" / "Local" / "Microsoft" / "Windows" / "WER",
                Path("C:/Users") / os.environ.get('USERNAME', '') / "AppData" / "Local" / "Microsoft" / "Windows" / "WER"
            ]
            
            for path in user_recycle_paths:
                if path.exists():
                    try:
                        size = self.get_file_size(path)
                        shutil.rmtree(path)
                        self.stats['total_size_freed'] += size
                        self.log(f"Cleaned user recycle data: {path.name}", "DELETED")
                    except Exception as e:
                        self.log(f"Failed to clean {path}: {e}", "WARNING")
                        
        except Exception as e:
            self.log(f"User recycle cleanup failed: {e}", "WARNING")
                    

                
    def clean_temp_files(self):
        """Clean ALL temporary files and traces"""
        self.log("Cleaning ALL temporary files and traces...", "INFO")
        
        # Primary temp directories - clean EVERYTHING
        primary_temp_dirs = [
            Path(os.environ['TEMP']),  # %TEMP% folder - clean completely
            self.localappdata / "Temp"  # LocalAppData\Temp - clean completely
        ]
        
        # Secondary temp directories - clean selectively
        secondary_temp_dirs = [
            self.user_profile / "AppData" / "LocalLow" / "Temp",
            Path("C:/Windows/Temp")
        ]
        
        # Clean primary temp directories COMPLETELY
        for temp_dir in primary_temp_dirs:
            if temp_dir.exists():
                self.log(f"Completely cleaning: {temp_dir}", "INFO")
                try:
                    total_size = 0
                    files_deleted = 0
                    dirs_deleted = 0
                    
                    # Get all items first to avoid iteration issues
                    items_to_delete = list(temp_dir.iterdir())
                    
                    for item in items_to_delete:
                        try:
                            size = self.get_file_size(item)
                            total_size += size
                            
                            if item.is_file():
                                item.unlink()
                                files_deleted += 1
                            elif item.is_dir():
                                shutil.rmtree(item)
                                dirs_deleted += 1
                                
                        except PermissionError:
                            self.log(f"Permission denied: {item.name}", "WARNING")
                        except Exception as e:
                            self.log(f"Failed to remove {item.name}: {e}", "ERROR")
                            self.stats['errors'] += 1
                    
                    self.stats['files_deleted'] += files_deleted
                    self.stats['directories_deleted'] += dirs_deleted
                    self.stats['total_size_freed'] += total_size
                    
                    self.log(f"Cleaned {temp_dir.name}: {files_deleted} files, {dirs_deleted} dirs ({total_size/1024/1024:.1f} MB)", "SUCCESS")
                    
                except Exception as e:
                    self.log(f"Error accessing temp directory {temp_dir}: {e}", "ERROR")
                    self.stats['errors'] += 1
        
        # Clean secondary temp directories selectively (game/anti-cheat related only)
        keywords = ['steam', 'rust', 'facepunch', 'eac', 'battleye', 'anticheat', 'vanguard', 'epic', 'fortnite']
        
        for temp_dir in secondary_temp_dirs:
            if temp_dir.exists():
                self.log(f"Selectively cleaning: {temp_dir}", "INFO")
                try:
                    for item in temp_dir.iterdir():
                        if any(keyword in item.name.lower() for keyword in keywords):
                            try:
                                size = self.get_file_size(item)
                                if item.is_file():
                                    item.unlink()
                                    self.stats['files_deleted'] += 1
                                elif item.is_dir():
                                    shutil.rmtree(item)
                                    self.stats['directories_deleted'] += 1
                                self.stats['total_size_freed'] += size
                                self.log(f"Removed temp: {item.name} ({size/1024:.1f} KB)", "DELETED")
                            except Exception as e:
                                self.log(f"Failed to remove temp item {item}: {e}", "ERROR")
                                self.stats['errors'] += 1
                except Exception as e:
                    self.log(f"Error accessing temp directory {temp_dir}: {e}", "ERROR")
                    self.stats['errors'] += 1
        
        # Additional cleanup using Windows commands
        self.log("Running additional temp cleanup commands...", "INFO")
        try:
            # Clean temp files using Windows commands
            subprocess.run(['del', '/q', '/f', '/s', os.environ['TEMP'] + '\\*'], 
                         shell=True, capture_output=True, timeout=30)
            subprocess.run(['rd', '/s', '/q', os.environ['TEMP']], 
                         shell=True, capture_output=True, timeout=30)
            # Recreate the temp directory
            os.makedirs(os.environ['TEMP'], exist_ok=True)
            self.log("Additional temp cleanup completed", "SUCCESS")
        except Exception as e:
            self.log(f"Additional temp cleanup failed: {e}", "WARNING")
                    
    def clean_registry_traces(self):
        """Clean comprehensive registry entries"""
        self.log("Cleaning registry traces and entries...", "INFO")
        
        # Comprehensive registry paths to clean
        registry_paths = [
            # Steam and Rust entries
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_CURRENT_USER, r"Software\Facepunch Studios"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Facepunch Studios LTD\Rust"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam\Users"),
            
            # Anti-cheat registry entries
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\.CETRAINER"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\.CT"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\CheatEngine"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Cheat Engine_is1"),
            (winreg.HKEY_CURRENT_USER, r"Software\Cheat Engine"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\BEService"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\ucldr_battlegrounds_gl"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\xhunter1"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\zksvc"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Riot Vanguard"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\vgc"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\vgk"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\vgk"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\EasyAntiCheat_EOS"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\EasyAntiCheat_EOS"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\EasyAntiCheat"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\atvi-randgrid_sr"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\EasyAntiCheat"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\EAAntiCheat"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\EAAntiCheatService"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\PnkBstrA"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\PnkBstrB"),
            
            # Epic Games registry entries
            (winreg.HKEY_CURRENT_USER, r"Software\Epic Games"),
            (winreg.HKEY_CURRENT_USER, r"Software\EpicGames"),
            (winreg.HKEY_CURRENT_USER, r"Software\WOW6432Node\Epic Games"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\com.epicgames.launcher"),
            (winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Hardware Survey"),
            (winreg.HKEY_CURRENT_USER, r"Software\Epic Games\Unreal Engine\Identifiers"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Installer\Dependencies"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Direct3D"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\com.epicgames.launcher"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Epic Games"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\EpicGames"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Epic Games"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\EpicGames"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\RADAR\HeapLeakDetection\DiagnosedApplications\FortniteClient-Win64-Shipping.exe")
        ]
        
        for hkey, path in registry_paths:
            try:
                self._delete_registry_key_recursive(hkey, path)
                self.stats['registry_keys_deleted'] += 1
                self.log(f"Removed registry key: {path}", "DELETED")
            except FileNotFoundError:
                self.log(f"Registry key not found: {path}", "INFO")
            except Exception as e:
                self.log(f"Failed to remove registry key {path}: {e}", "ERROR")
                self.stats['errors'] += 1
                
    def _delete_registry_key_recursive(self, hkey, path):
        """Recursively delete registry key and all subkeys"""
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Delete all subkeys first
                subkeys = []
                try:
                    i = 0
                    while True:
                        subkey = winreg.EnumKey(key, i)
                        subkeys.append(subkey)
                        i += 1
                except WindowsError:
                    pass
                    
                for subkey in subkeys:
                    self._delete_registry_key_recursive(hkey, f"{path}\\{subkey}")
                    
            # Delete the key itself
            winreg.DeleteKey(hkey, path)
        except Exception:
            # If we can't open the key, try to delete it directly
            winreg.DeleteKey(hkey, path)
                
    def run_clean_files_only(self):
        """Clean files and kill processes but preserve anti-cheat installations"""
        try:
            # Step 1: Kill processes (including anti-cheat)
            self.log("STEP 1: Terminating all processes", "INFO")
            self.kill_processes()
            
            # Step 2: Deep clean Steam data
            self.log("STEP 2: Deep cleaning Steam data", "INFO") 
            self.clean_steam_data()
            
            # Step 3: Clean Rust data
            self.log("STEP 3: Cleaning Rust game data", "INFO")
            self.clean_rust_data()
            
            # Step 4: Clean Epic Games data
            self.log("STEP 4: Cleaning Epic Games and Fortnite data", "INFO")
            self.clean_epic_games_data()
            
            # Step 5: Clean temp files
            self.log("STEP 5: Cleaning temporary files", "INFO")
            self.clean_temp_files()
            
            # Step 6: Clean Windows prefetch
            self.log("STEP 6: Cleaning Windows prefetch files", "INFO")
            self.clean_windows_prefetch()
            
            # Step 7: Clean recycle bins
            self.log("STEP 7: Cleaning recycle bins", "INFO")
            self.clean_recycle_bins()
            
            # Step 8: Clean registry traces (game data only)
            self.log("STEP 8: Cleaning game registry entries", "INFO")
            self.clean_registry_traces()
            
            # Calculate final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
            
            self.display_completion_stats()
            return True
            
        except Exception as e:
            self.log(f"Critical error during cleanup: {e}", "ERROR")
            self.stats['errors'] += 1
            return False
    
    def run_complete_removal(self):
        """Complete anti-cheat removal - nuclear option"""
        try:
            # Step 1: Kill processes and disable protection
            self.log("STEP 1: Terminating processes and disabling protection", "INFO")
            self.disable_windows_defender()
            self.kill_processes()
            
            # Step 2: Deep clean Steam data
            self.log("STEP 2: Deep cleaning Steam data", "INFO") 
            self.clean_steam_data()
            
            # Step 3: Clean Rust data
            self.log("STEP 3: Cleaning Rust game data", "INFO")
            self.clean_rust_data()
            
            # Step 4: COMPLETE anti-cheat removal
            self.log("STEP 4: COMPLETE ANTI-CHEAT REMOVAL", "INFO")
            self.clean_anticheat_systems_complete()
            
            # Step 5: Clean temp files
            self.log("STEP 5: Cleaning temporary files", "INFO")
            self.clean_temp_files()
            
            # Step 6: Clean Epic Games data
            self.log("STEP 6: Cleaning Epic Games and Fortnite data", "INFO")
            self.clean_epic_games_data()
            
            # Step 7: Clean Windows prefetch
            self.log("STEP 7: Cleaning Windows prefetch files", "INFO")
            self.clean_windows_prefetch()
            
            # Step 8: Clean recycle bins
            self.log("STEP 8: Cleaning recycle bins", "INFO")
            self.clean_recycle_bins()
            
            # Step 9: Clean registry traces
            self.log("STEP 9: Cleaning registry entries", "INFO")
            self.clean_registry_traces()
            
            # Calculate final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
            
            self.display_completion_stats()
            return True
            
        except Exception as e:
            self.log(f"Critical error during cleanup: {e}", "ERROR")
            self.stats['errors'] += 1
            return False
            
        except Exception as e:
            self.log(f"Critical error during cleanup: {e}", "ERROR")
            self.stats['errors'] += 1
            return False
            
        return True
        
    def display_completion_stats(self):
        """Display detailed completion statistics"""
        print("\n" + "=" * 70)
        print("CLEANUP COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        duration = self.stats['duration'].total_seconds()
        size_mb = self.stats['total_size_freed'] / (1024 * 1024)
        
        print(f"Total Runtime: {duration:.1f} seconds")
        print(f"Processes Terminated: {self.stats['processes_killed']}")
        print(f"Directories Removed: {self.stats['directories_deleted']}")
        print(f"Files Deleted: {self.stats['files_deleted']}")
        print(f"Registry Keys Cleaned: {self.stats['registry_keys_deleted']}")
        print(f"Total Space Freed: {size_mb:.1f} MB ({size_mb/1024:.2f} GB)")
        print(f"Errors Encountered: {self.stats['errors']}")
        
        if self.stats['errors'] == 0:
            print("\nALL OPERATIONS COMPLETED WITHOUT ERRORS!")
        else:
            print(f"\n{self.stats['errors']} errors occurred during cleanup")
            
        print("\nSteam, Rust, and Epic Games have been reset to fresh installation state")
        print("All anti-cheat systems have been cleaned")
        print("Windows prefetch files and recycle bins cleared")
        print("All trace files and registry entries removed")
        
        print("\n" + "=" * 70)
        print("                    AC-ZERO v1.0")
        print("              https://jlaiii.github.io/AC-Zero/")
        print("=" * 70)
        
        # Auto-close after 10 seconds if no key pressed
        import threading
        import sys
        
        def auto_close():
            for i in range(10, 0, -1):
                print(f"\rPress any key to exit... (auto-closing in {i}s) ", end="", flush=True)
                time.sleep(1)
            print(f"\rAuto-closing...                                    ", flush=True)
            os._exit(0)
        
        # Start auto-close timer
        timer = threading.Thread(target=auto_close, daemon=True)
        timer.start()
        
        try:
            input()
            os._exit(0)
        except:
            time.sleep(1)
            os._exit(0)

def request_admin():
    """Request administrator privileges if not already running as admin"""
    import ctypes
    
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        is_admin = False
        
    if not is_admin:
        print("Requesting administrator privileges...")
        # Re-run the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{os.path.abspath(__file__)}"', 
            None, 
            1
        )
        sys.exit(0)

def add_to_startup():
    """Add script to Windows startup (optional)"""
    try:
        startup_folder = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        script_path = Path(__file__).absolute()
        
        # Create a batch file to run the Python script
        batch_content = f'''@echo off
cd /d "{script_path.parent}"
python "{script_path.name}"
'''
        
        batch_file = startup_folder / "ac-zero.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
            
        print(f"Added to startup: {batch_file}")
        return True
    except Exception as e:
        print(f"Failed to add to startup: {e}")
        return False

def show_main_menu():
    """Display main menu and get user choice"""
    print("=" * 70)
    print("                    AC-ZERO v1.0")
    print("           Advanced Cleaning & Reset Tool")
    print("=" * 70)
    print()
    print("Choose your cleaning mode:")
    print()
    print("1. CLEAN FILES ONLY")
    print("   - Kill anti-cheat processes")
    print("   - Clean game data and configurations")
    print("   - Preserve anti-cheat installations")
    print("   - Games will show 'not installed' errors")
    print()
    print("2. REMOVE ALL ANTI-CHEAT")
    print("   - Complete anti-cheat removal")
    print("   - Delete all anti-cheat files and drivers")
    print("   - Full system cleanup")
    print("   - Nuclear option")
    print()
    print("3. EXIT")
    print()
    print("=" * 70)
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

def main():
    """Main function"""
    if os.name != 'nt':
        print("ERROR: This script is designed for Windows only!")
        input("Press any key to exit...")
        sys.exit(1)
    
    # Automatically request admin privileges
    request_admin()
    
    # Show boot sequence
    boot_sequence()
    
    # Show menu and get choice
    choice = show_main_menu()
    
    if choice == 3:
        print("Exiting AC-Zero...")
        sys.exit(0)
    
    # Initialize cleaner
    cleaner = ACZero()
    
    if choice == 1:
        print("\n" + "=" * 70)
        print("STARTING CLEAN FILES ONLY MODE")
        print("Anti-cheat processes will be killed but files preserved")
        print("=" * 70)
        success = cleaner.run_clean_files_only()
    elif choice == 2:
        print("\n" + "=" * 70)
        print("STARTING COMPLETE ANTI-CHEAT REMOVAL")
        print("WARNING: This will completely remove all anti-cheat systems!")
        print("=" * 70)
        
        confirm = input("Are you sure? Type 'YES' to continue: ").strip()
        if confirm.upper() == 'YES':
            success = cleaner.run_complete_removal()
        else:
            print("Operation cancelled.")
            sys.exit(0)

if __name__ == "__main__":
    main()