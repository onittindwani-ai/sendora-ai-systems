#!/bin/zsh
# Start, stop or inspect the seven demo systems on this computer. Demo mode only: nothing leaves your machine.
#
#   tools/demo_all.sh start [system ...]    install what is missing, build if needed, start api and web
#   tools/demo_all.sh stop [system ...]     stop them
#   tools/demo_all.sh restart [system ...]  stop, delete the web build, start again (use after a code change)
#   tools/demo_all.sh status                show which ones answer
#
# Ports: pipecairn 3001/8001, ringlark 3002/8002, booklantern 3003/8003, deskfern 3004/8004,
# lorefern 3005/8005, penlark 3006/8006, slatehire 3007/8007. Web: http://<system>.localhost:<port>
# Sign in with owner@example.test and demo-password-1 (demo data, not real).
# Needs: uv (or python3.12), pnpm and Node 22 or newer. Folder of the system repos: SYSTEMS_ROOT
# (default: the folder that holds this hub). Logs and pids: DEMO_LOG_DIR (default: <hub>/.demo-logs).
set -u
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
HUB="${0:A:h:h}"
ROOT="${SYSTEMS_ROOT:-${HUB:h}}"
LOG="${DEMO_LOG_DIR:-$HUB/.demo-logs}"
ALL=(pipecairn ringlark booklantern deskfern lorefern penlark slatehire)
mkdir -p "$LOG"

port() { local i=1; for s in $ALL; do [ "$s" = "$1" ] && { echo $i; return; }; i=$((i+1)); done; echo 0; }

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing $1. $2"; exit 2; }; }

make_venv() {
  if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e packages/core-py -e "apps/api[dev]"
  elif command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv .venv && .venv/bin/pip install -e packages/core-py -e "apps/api[dev]"
  else
    echo "Neither uv nor python3.12 found. Install uv (https://docs.astral.sh/uv/) or Python 3.12."; return 1
  fi
}

stop_one() {
  local r="$1" f
  for f in "$LOG/$r-api.pid" "$LOG/$r-web.pid"; do
    [ -f "$f" ] && { kill "$(cat "$f")" 2>/dev/null; rm -f "$f"; }
  done
  local n; n=$(port "$r")
  # next start leaves a child process holding the port
  lsof -ti tcp:300$n 2>/dev/null | xargs -r kill 2>/dev/null
  lsof -ti tcp:800$n 2>/dev/null | xargs -r kill 2>/dev/null
  echo "stopped $r"
}

start_one() {
  local r="$1" n; n=$(port "$r")
  local d="$ROOT/$r"
  [ -d "$d" ] || { echo "$r: folder $d not found"; return 1; }
  cd "$d" || return 1
  [ -x .venv/bin/python ] || make_venv || return 3
  [ -d node_modules ] || nice -n 15 pnpm install || return 4
  [ -d apps/web/.next ] || NEXT_PUBLIC_DEMO_HINT=1 nice -n 15 pnpm build || return 5
  local mode=draft extra=""
  case "$r" in pipecairn|ringlark|booklantern) mode=live;; esac
  [ "$r" = "deskfern" ] && extra="SEED_DIR=./data"
  env DEMO_MODE=true MODE=$mode INSECURE_COOKIES=1 SESSION_SECRET=demo-secret-not-for-real-use-1234 DATABASE_URL=sqlite:///./demo.sqlite3 $extra \
    nohup .venv/bin/python -m uvicorn $r.api.app:app_from_env --factory --host 127.0.0.1 --port 800$n --proxy-headers > "$LOG/$r-api.log" 2>&1 &
  echo $! > "$LOG/$r-api.pid"
  ( cd apps/web && env API_BASE_URL=http://127.0.0.1:800$n INSECURE_COOKIES=1 NEXT_PUBLIC_DEMO_HINT=1 PORT=300$n \
      nohup pnpm exec next start -p 300$n -H 127.0.0.1 > "$LOG/$r-web.log" 2>&1 & echo $! > "$LOG/$r-web.pid" )
  sleep 5
  status_one "$r"
}

status_one() {
  local r="$1" n; n=$(port "$r")
  local a w
  a=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:800$n/health" 2>/dev/null)
  w=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:300$n/login" 2>/dev/null)
  echo "$r  api 800$n: ${a:-down}  web http://$r.localhost:300$n : ${w:-down}"
}

cmd="${1:-status}"; shift 2>/dev/null
targets=("$@"); [ ${#targets[@]} -eq 0 ] && targets=($ALL)
case "$cmd" in
  start)   need pnpm "Install it with: corepack enable (Node 22 or newer) or npm i -g pnpm"
           for r in $targets; do start_one "$r"; done ;;
  stop)    for r in $targets; do stop_one "$r"; done ;;
  restart) for r in $targets; do stop_one "$r"; rm -r -- "$ROOT/$r/apps/web/.next" 2>/dev/null; start_one "$r"; done ;;
  status)  for r in $targets; do status_one "$r"; done ;;
  *) echo "usage: $0 start|stop|restart|status [system ...]"; exit 1 ;;
esac
