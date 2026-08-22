// Somatic CSI serial line-format reference (Arduino-ESP32).
//
// This sketch prints one JSON line per fake CSI frame on USB serial so the
// host forwarder can UDP it to 127.0.0.1:53721. Replace `emit_demo_frame`
// with your real CSI callback from Espressif esp-csi or ESP32-CSI-Tool.
//
// It is not a complete CSI driver. Live capture against a physical board is
// still: sandbox-verified; needs a real ESP32 to validate live.
//
// Flash with Arduino-ESP32 + esptool. Baud 115200.

void emit_demo_frame(unsigned long seq) {
  // Derived amplitudes only. Do not print raw IQ to the network.
  Serial.print("{\"v\":1,\"ts\":");
  Serial.print(millis() / 1000.0, 3);
  Serial.print(",\"unit_id\":\"esp32-a\",\"rssi\":-48,\"amp\":[");
  for (int i = 0; i < 16; i++) {
    if (i) Serial.print(",");
    float value = 0.35 + 0.2 * sin((seq / 10.0) + i * 0.4);
    Serial.print(value, 4);
  }
  Serial.println("]}");
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("# somatic-csi-serial-reference");
}

void loop() {
  static unsigned long seq = 0;
  emit_demo_frame(seq++);
  delay(100);
}
