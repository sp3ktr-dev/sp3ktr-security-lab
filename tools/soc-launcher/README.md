# SOC Launcher

A tmux-based infrastructure launcher for quickly accessing core SOC and lab systems from a single terminal session.

---

## Purpose

SOC Launcher reduces the friction of manually opening multiple terminal tabs and SSH sessions by:

- reading hosts from a config file
- checking host reachability
- checking SSH availability
- creating a tmux session
- opening one tmux window per host
- automatically connecting with SSH

---

## Files

- launcher.sh - main launcher script  
- hosts.conf.example - sanitized example config  
- hosts.conf - local real config file (NOT committed)

---

## Host Config Format

Copy the example file:

```bash
cp hosts.conf.example hosts.conf
```

Then edit `hosts.conf` with your real values.

Each line uses this format:

```
name|ip|user
```

Example:

```
wazuh|192.168.1.10|analyst
elk|192.168.1.11|analyst
soar|192.168.1.12|analyst
dev|192.168.1.20|developer
```

---

## Usage

Make the launcher executable:

```bash
chmod +x launcher.sh
```

Run it:

```bash
./launcher.sh
```

The launcher will:

1. read `hosts.conf`
2. check ping and SSH status
3. create a tmux session named `soc`
4. open one tmux window per host
5. attempt to SSH into each host

---

## tmux Quick Reference

List windows:
```
Ctrl+b, then w
```

Next window:
```
Ctrl+b, then n
```

Previous window:
```
Ctrl+b, then p
```

Detach from session:
```
Ctrl+b, then d
```

Kill current window:
```
Ctrl+b, then &
```

Show tmux sessions:
```bash
tmux ls
```

Attach to SOC session:
```bash
tmux attach-session -t soc
```

Kill SOC session:
```bash
tmux kill-session -t soc
```

Kill all tmux sessions:
```bash
tmux kill-server
```

---

## Notes

- Real infrastructure IPs and usernames should stay in `hosts.conf`
- `hosts.conf` is ignored by Git
- Password prompts will still appear unless SSH keys are configured
- This tool is intended for authorized lab and infrastructure administration only

---

## Future Improvements

- remote CPU, RAM, disk checks  
- colorized status output  
- skip unreachable hosts automatically  
- status-only mode  
- custom SSH ports  
- per-host startup commands  
