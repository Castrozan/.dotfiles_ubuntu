function shorten(description) {
  if (description.indexOf("SBC-XQ") !== -1) return "SBC-XQ";
  if (description.indexOf("SBC") !== -1) return "SBC";
  if (description.indexOf("AAC") !== -1) return "AAC";
  if (description.indexOf("mSBC") !== -1) return "mSBC";
  if (description.indexOf("CVSD") !== -1) return "CVSD";
  if (description.indexOf("LDAC") !== -1) return "LDAC";
  if (description.indexOf("aptX HD") !== -1) return "aptX HD";
  if (description.indexOf("aptX") !== -1) return "aptX";
  if (description.indexOf("A2DP") !== -1) return "A2DP";
  if (description.indexOf("HSP") !== -1 || description.indexOf("HFP") !== -1)
    return "HSP/HFP";
  if (description.indexOf("Headset Head Unit") !== -1) return "Headset";
  if (description.indexOf("High Fidelity") !== -1) return "HiFi";
  return description.length > 12
    ? description.substring(0, 10) + "…"
    : description;
}
