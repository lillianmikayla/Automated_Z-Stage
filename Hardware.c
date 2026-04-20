// CL57T Closed Loop Stepper Driver — Arduino Mega 2560
// -------------------------------------------------------
// Wiring:
//   Pin 9  → PULS+    (PULS− → GND)
//   Pin 8  → DIR+     (DIR−  → GND)
//   Pin 7  → ENA+     (ENA−  → GND)
//   Pin 5  → ALM+     (ALM−  → GND)  
//
// Encoder Y-split from motor:
//   Pin 3  → A+     
//   Pin 2  → B+      
//   A- and B- stay connected to CL57T only

#define PULSE_PIN     9
#define DIR_PIN       8
#define ENABLE_PIN    7
#define ALM_PIN       5
#define ENC_A_PIN     3   
#define ENC_B_PIN     2  

#define STEPS_PER_REV     5000
#define MM_PER_REV        20.0
#define STEPS_PER_MM      250.0

#define ENC_COUNTS_PER_REV  4000
#define ENC_COUNTS_PER_MM   100.0

#define PULSE_WIDTH_US        10
#define STEP_DELAY_US         500

// Position error threshold in mm before stall is declared
#define STALL_THRESHOLD_MM    0.05
#define MAX_CORRECTION_STEPS  10

volatile long encoderCounts = 0;  // real position from ISR
float positionMM = 0.0;           // commanded position tracked per step
bool isHomed = false;
bool motorEnabled = false;
String lineBuffer = "";

// Fires on every change of A+, reads B+ to determine direction
void encoderISR() {
  bool a = digitalRead(ENC_A_PIN);
  bool b = digitalRead(ENC_B_PIN);
  if (a == b) encoderCounts--;
  else        encoderCounts++;
}

// Motor Control 
void enableMotor() {
  digitalWrite(ENABLE_PIN, LOW);
  motorEnabled = true;
  delay(100);
}

void disableMotor() {
  digitalWrite(ENABLE_PIN, HIGH);
  motorEnabled = false;
}

// Issue one step and track commanded position in MM
void stepOnce(bool direction) {
  digitalWrite(DIR_PIN, direction ? HIGH : LOW);
  delayMicroseconds(5);
  digitalWrite(PULSE_PIN, HIGH);
  delayMicroseconds(PULSE_WIDTH_US);
  digitalWrite(PULSE_PIN, LOW);
  delayMicroseconds(STEP_DELAY_US - PULSE_WIDTH_US);

  if (direction) positionMM += (1.0 / STEPS_PER_MM);
  else           positionMM -= (1.0 / STEPS_PER_MM);
}

// Position 
// Returns real position from encoder counts
float encoderPositionMM() {
  return (float)encoderCounts / ENC_COUNTS_PER_MM;
}

// Send current encoder position to GUI 
void reportPosition() {
  Serial.print("Z:");
  Serial.println(encoderPositionMM(), 3);
}

// Stall Detection
// Compares encoder position to commanded position in MM
bool checkPositionError() {
  float error = encoderPositionMM() - positionMM;
  if (fabs(error) > STALL_THRESHOLD_MM) {
    Serial.print("ERROR:STALL_");
    Serial.println(error, 3);
    return false;
  }
  return true;
}

// Position Correction 
void correctPosition() {
  float error = positionMM - encoderPositionMM();
  int correctionSteps = constrain(
    (int)(error * STEPS_PER_MM / 2),
    -MAX_CORRECTION_STEPS,
    MAX_CORRECTION_STEPS);
  if (correctionSteps == 0) return;

  bool dir = correctionSteps > 0;
  int steps = abs(correctionSteps);
  for (int i = 0; i < steps; i++) {
    stepOnce(dir);
    delayMicroseconds(STEP_DELAY_US);
  }
}

// Move by Steps
void moveSteps(long steps, bool direction) {
  for (long i = 0; i < steps; i++) {
    if (digitalRead(ALM_PIN) == LOW) {
      disableMotor();
      Serial.println("ERROR:ALARM - Check driver LED");
      while (1);
    }
    stepOnce(direction);
  }
}

//  Move by MM 
void moveMM(float distanceMM) {
  if (!isHomed) {
    Serial.println("ERROR:NOT_HOMED");
    return;
  }

  Serial.println("BUSY");

  bool direction = distanceMM > 0;  // true = down, false = up
  long steps = (long)(fabs(distanceMM) * STEPS_PER_MM + 0.5);

  moveSteps(steps, direction);

  // Allow encoder to settle then check for stall
  delay(50);
  if (!checkPositionError()) {
    correctPosition();
    delay(50);
    checkPositionError();
  }

  reportPosition();
  Serial.println("IDLE");
}

// Zeros all tracking at current physical location
void setHome() {
  encoderCounts = 0;
  positionMM = 0.0;
  isHomed = true;

  Serial.println("HOMED");
  reportPosition();
  Serial.println("IDLE");
}

// Drives back to stored 0.000 mm home position
void rehome() {
  if (!isHomed) {
    Serial.println("ERROR:NOT_HOMED");
    return;
  }

  if (positionMM == 0.0) {
    reportPosition();
    Serial.println("IDLE");
    return;
  }

  Serial.println("BUSY");

  float returnDistance = -positionMM;
  bool direction = returnDistance > 0;
  long steps = (long)(fabs(returnDistance) * STEPS_PER_MM + 0.5);

  moveSteps(steps, direction);

  delay(50);
  if (!checkPositionError()) {
    correctPosition();
    delay(50);
    checkPositionError();
  }

  // Hard zero after rehome to prevent drift accumulation
  encoderCounts = 0;
  positionMM = 0.0;

  reportPosition();
  Serial.println("IDLE");
}

void setup() {
  Serial.begin(115200);

  pinMode(PULSE_PIN,   OUTPUT);
  pinMode(DIR_PIN,     OUTPUT);
  pinMode(ENABLE_PIN,  OUTPUT);
  pinMode(ALM_PIN,     INPUT_PULLUP);
  pinMode(ENC_A_PIN,   INPUT_PULLUP);
  pinMode(ENC_B_PIN,   INPUT_PULLUP);

  // Interrupt on A+ — fires on every edge, reads B+ for direction
  attachInterrupt(digitalPinToInterrupt(ENC_A_PIN), encoderISR, CHANGE);

  enableMotor();

  Serial.println("READY");
}

// Loop 
void loop() {
  if (digitalRead(ALM_PIN) == LOW) {
    disableMotor();
    Serial.println("ERROR:ALARM - Check driver LED");
    while (1);
  }

  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (lineBuffer.length() > 0) {
        lineBuffer.trim();
        String cmd = lineBuffer;
        lineBuffer = "";

        if (cmd == "SH" || cmd == "sh") {
          setHome();

        } else if (cmd == "RH" || cmd == "rh") {
          rehome();

        } else if (cmd == "P" || cmd == "p") {
          reportPosition();

        } else {
          float distance = cmd.toFloat();
          if (distance != 0.0) {
            moveMM(distance);
          } else {
            Serial.println("ERROR:UNKNOWN_CMD");
          }
        }
      }
    } else {
      lineBuffer += c;
    }
  }
}
