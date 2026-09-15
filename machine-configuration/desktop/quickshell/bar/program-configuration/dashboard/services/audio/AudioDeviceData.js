function audioDeviceListsAreEqual(oldList, newList) {
  if (oldList.length !== newList.length) return false;
  for (let i = 0; i < oldList.length; i++) {
    const oldItem = oldList[i];
    const newItem = newList[i];
    if (
      oldItem.name !== newItem.name ||
      oldItem.volume !== newItem.volume ||
      oldItem.mute !== newItem.mute ||
      oldItem.state !== newItem.state ||
      oldItem.description !== newItem.description
    )
      return false;
  }
  return true;
}

function extractVolumePercent(volumeObject) {
  if (!volumeObject) return 0;
  for (const channel in volumeObject) {
    const percentString = volumeObject[channel].value_percent ?? "0%";
    return parseInt(percentString) || 0;
  }
  return 0;
}

function extractPortType(ports, activePortName) {
  if (!ports || !activePortName) return "";
  for (let i = 0; i < ports.length; i++)
    if (ports[i].name === activePortName) return ports[i].type ?? "";
  return "";
}
