// CL5760T Closed Loop Stepper Driver — Arduino Mega 2560
// Wiring:
//   Pin 9  → PULS+    (PULS− → GND)
//   Pin 8  → DIR+     (DIR−  → GND)
//   Pin 7  → ENA+     (ENA−  → GND)

#define PULSE_PIN   9
#define DIR_PIN     8
#define ENABLE_PIN  7

// CL5760T: LOW on ENA+ enables the driver (opto off = enabled)
#define ENABLE_ACTIVE LOW

// Adjust to match driver's microstep setting based on dip switch (default is often 1600 steps/rev)
#define STEPS_PER_REV 5000
#define MM_PER_REV 5.0 // moves 5mm per revolution 
#define STEP_DELAY 500
#define STEPS_PER_MM 1000 // (STEPS_PER_REV / MM_PER_REV)

// Pulse width in microseconds — CL5760T minimum is ~2.5µs, 10µs is safe
#define PULSE_WIDTH_US 10

String lineBuffer = "";

void setup() {
  Serial.begin(115200);
  pinMode(PULSE_PIN,  OUTPUT);
  pinMode(DIR_PIN,    OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  // Enable the driver
  digitalWrite(ENABLE_PIN, ENABLE_ACTIVE);

  // Small delay after enable before sending pulses
  delay(100);
}

// Sends 'steps' pulses at the given speed (microseconds between pulses)
// Direction: HIGH or LOW
void moveStepper(long steps, int stepDelayUs, bool direction) {
  digitalWrite(DIR_PIN, direction ? HIGH : LOW);
  delayMicroseconds(5); // DIR setup time before pulsing

  for (long i = 0; i < steps; i++) {

    digitalWrite(PULSE_PIN, HIGH);
    delayMicroseconds(PULSE_WIDTH_US);
    digitalWrite(PULSE_PIN, LOW);
    delayMicroseconds(stepDelayUs - PULSE_WIDTH_US);
  }
}

// Move by a specified distance in millimeters
void moveMM(float distanceMM, int stepDelayUs) {
  bool direction = distanceMM > 0;
  long steps = (long)(fabs(distanceMM) * STEPS_PER_MM + 0.5);

  Serial.print("Steps: ");
  Serial.println(steps);
  Serial.println(direction);

  moveStepper(steps, stepDelayUs, direction);
}

void loop() {

  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {

      if (lineBuffer.length() > 0) {

        float distance = lineBuffer.toFloat();

        Serial.print("Move command: ");
        Serial.println(distance);

        moveMM(distance, STEP_DELAY);

        lineBuffer = "";
      }

    } else {
      lineBuffer += c;
    }
  }
}
