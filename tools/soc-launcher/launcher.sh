#!/usr/bin/env bash

CONFIG_FILE="hosts.conf"

check_ping() {
    local host="$1"
    if ping -c 1 -W 1 "$host" >/dev/null 2>&1; then
        echo "UP"
    else
        echo "DOWN"
    fi
}

check_ssh() {
    local host="$1"
    if timeout 2 bash -c "</dev/tcp/$host/22" >/dev/null 2>&1; then
        echo "OPEN"
    else
        echo "CLOSED"
    fi
}

launch_tmux_session() {
    local session_name="soc"

    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo
        echo "[*] tmux session '$session_name' already exists. Attaching..."
        tmux attach-session -t "$session_name"
        exit 0
    fi

    tmux new-session -d -s "$session_name" -n "overview"

    local first_window=true

    while IFS="|" read -r name host user; do
        [[ -z "$name" ]] && continue

        if $first_window; then
            tmux rename-window -t "$session_name:0" "$name"
            tmux send-keys -t "$session_name:$name" "ssh ${user}@${host}" C-m
            first_window=false
        else
            tmux new-window -t "$session_name" -n "$name"
            tmux send-keys -t "$session_name:$name" "ssh ${user}@${host}" C-m
        fi
    done < "$CONFIG_FILE"

    echo
    echo "[+] tmux session '$session_name' created."
    echo "[*] Attaching now..."
    tmux attach-session -t "$session_name"
}


echo "=== Spektr Security Lab - SOC Launcher v1 ==="
echo

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "[-] Config file not found: $CONFIG_FILE"
    exit 1
fi

printf "%-12s %-16s %-12s %-10s %-10s\n" "NAME" "HOST" "USER" "PING" "SSH"
printf "%-12s %-16s %-12s %-10s %-10s\n" "------------" "----------------" "------------" "----------" "----------"

while IFS="|" read -r name host user; do
    [[ -z "$name" ]] && continue

    ping_status=$(check_ping "$host")
    ssh_status=$(check_ssh "$host")

    printf "%-12s %-16s %-12s %-10s %-10s\n" "$name" "$host" "$user" "$ping_status" "$ssh_status"
done < "$CONFIG_FILE"

launch_tmux_session
