void setup() {
  Serial.begin(115200);
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (lineBuffer.length() > 0) {
        parseCommand(lineBuffer);
        lineBuffer = "";
      }
    } else {
      lineBuffer += c;
    }
  }
}

void parseCommand(String line) {
  line.trim();
  line.toUpperCase();

  Serial.print("Received: ");
  Serial.println(line);

  if (!(line.startsWith("G0") || line.startsWith("G1"))) {
    Serial.println("Invalid command");
    return;
  }

  int zIndex = line.indexOf('Z');

  if (zIndex == -1) {
    Serial.println("Command parsed:");
    Serial.println("Move default: 2.0 mm");
    return;
  }

  float zValue = line.substring(zIndex + 1).toFloat();

  Serial.println("Command parsed:");
  Serial.print("Relative Z move: ");
  Serial.print(zValue);
  Serial.println(" mm");
}
