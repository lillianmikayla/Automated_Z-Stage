// CL5760T Closed Loop Stepper Driver — Arduino Mega 2560
// Wiring:
//   Pin 9  → PULS+    (PULS− → GND)
//   Pin 8  → DIR+     (DIR−  → GND)
//   Pin 7  → ENA+     (ENA−  → GND)

#define PULSE_PIN   9
#define DIR_PIN     8
#define ENABLE_PIN  7

#define ENABLE_ACTIVE LOW

#define STEPS_PER_REV 5000
#define STEP_DELAY 500
#define MM_PER_REV 5.0
#define STEPS_PER_MM 1000
#define PULSE_WIDTH_US 10

String lineBuffer = "";

void setup() {
  Serial.begin(115200);

  pinMode(PULSE_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  digitalWrite(ENABLE_PIN, ENABLE_ACTIVE);
  delay(100);
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

// Sends 'steps' pulses at the given speed
void moveStepper(long steps, int stepDelayUs, bool direction) {
  digitalWrite(DIR_PIN, direction ? HIGH : LOW);
  delayMicroseconds(5);

  for (long i = 0; i < steps; i++) {
    digitalWrite(PULSE_PIN, HIGH);
    delayMicroseconds(PULSE_WIDTH_US);
    digitalWrite(PULSE_PIN, LOW);
    delayMicroseconds(stepDelayUs - PULSE_WIDTH_US);
  }
}

// Move by a specified distance in millimeters
void moveMM(float distanceMM, int stepDelayUs) {
  bool direction = (distanceMM > 0);
  long stepsToMove = (long)(abs(distanceMM) * STEPS_PER_MM + 0.5);

  Serial.print("Moving ");
  Serial.print(distanceMM);
  Serial.print(" mm = ");
  Serial.print(stepsToMove);
  Serial.print(" steps - ");
  Serial.println(direction);

  moveStepper(stepsToMove, stepDelayUs, direction);
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
  float zValue;

  if (zIndex == -1) {
    zValue = 2.0;
    Serial.println("Command parsed:");
    Serial.println("Move default: 2.0 mm");
  } else {
    zValue = line.substring(zIndex + 1).toFloat();

    Serial.println("Command parsed:");
    Serial.print("Relative Z move: ");
    Serial.print(zValue);
    Serial.println(" mm");
  }

  moveMM(zValue, STEP_DELAY);
  delay (1000);
  Serial.println("ok");
}
