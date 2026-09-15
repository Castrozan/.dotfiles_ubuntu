#!/usr/bin/env bash
is_running() {
	pgrep -f "$1" >/dev/null 2>&1
}

detect_v4l2_device() {
	for sysdir in /sys/class/video4linux/video*; do
		[ -d "$sysdir" ] || continue
		local deviceName
		deviceName=$(cat "$sysdir/name" 2>/dev/null || true)
		if echo "$deviceName" | grep -qi -e "avatar" -e "v4l2loopback"; then
			echo "/dev/$(basename "$sysdir")"
			return
		fi
	done
	echo "/dev/video10"
}

wait_for_port() {
	local port=$1
	local timeout=30
	local elapsed=0

	echo -n "  Waiting for port $port to be available..."
	while ! ss -tlnp 2>/dev/null | grep -q ":$port " && [ $elapsed -lt $timeout ]; do
		sleep 1
		elapsed=$((elapsed + 1))
	done

	if [ $elapsed -ge $timeout ]; then
		echo -e " ${RED}TIMEOUT${NC}"
		return 1
	else
		echo -e " ${GREEN}OK${NC}"
		return 0
	fi
}

create_virtual_sink() {
	local name=$1 description=$2 media_class=$3
	if pactl list sinks short 2>/dev/null | grep -q "$name" || pactl list sources short 2>/dev/null | grep -q "$name"; then
		echo -e "  ${YELLOW}⚠${NC}  $name already exists"
	else
		pactl load-module module-null-sink sink_name="$name" sink_properties=device.description="$description" media.class="$media_class" channel_map=front-left,front-right >/dev/null
		echo -e "  ${GREEN}✓${NC} $name created"
	fi
}
