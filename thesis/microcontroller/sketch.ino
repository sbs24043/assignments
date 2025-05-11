*
  Tiny-ML image-classifier over Serial ­– ArduTFLite version
  ---------------------------------------------------------
  - Board: any Mbed-based Nano 33 BLE / ESP32-Nano / Portenta / GIGA R1, etc.
  - Library dependencies (via Library-Manager):
        • ArduTFLite  ≥ 1.0.2
        • Chirale_TensorFlowLite (pulled in automatically)
  - Model: supply your converted model as `model_data.h`
           it must expose a symbol called `model`:

              extern const unsigned char model[];

  Protocol on the wire
  --------------------
   PC/host sends, at 115 200 baud:
       1) a single ASCII 'I' (0x49) synchronisation byte
       2) a 4-byte little-endian uint32_t with the image length   (should equal IMG_BYTES)
       3) IMG_BYTES raw 8-bit pixels (row-major, 0-255)

   The sketch answers with:
       - one line per output neuron:  "<index>\t<score>"
       - a terminating line "---end---"
*/

#include <ArduTFLite.h>
#include "model_data.h"

// ---------- EDIT THESE FIVE DEFINES TO MATCH YOUR MODEL -----------------
#define IMG_WIDTH        28        // pixels
#define IMG_HEIGHT       28
#define IMG_CHANNELS     1         // 1 = grayscale, 3 = RGB
#define NUM_CLASSES      10         // how many outputs does your model have?
#define ARENA_SIZE       80 * 1024 // adjust until modelInit() succeeds
// ------------------------------------------------------------------------

constexpr size_t IMG_BYTES = IMG_WIDTH * IMG_HEIGHT * IMG_CHANNELS;
alignas(16) uint8_t tensorArena[ARENA_SIZE];
uint8_t           rxBuffer[IMG_BYTES];

void waitSync() {
  // Wait for ASCII 'I' from the host to resynchronise streams
  while (Serial.read() != 'I') { /* spin */ }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  Serial.println(F("\n=== ArduTFLite Serial Image Classifier ==="));

  if (!modelInit(int_quant_model_state_acc_0_848_round_2_tflite, tensorArena, ARENA_SIZE)) {              // :contentReference[oaicite:0]{index=0}
    Serial.println(F("FATAL: modelInit() failed – enlarge ARENA_SIZE"));
    while (true) {}
  }
  Serial.println(F("Model ready. Waiting for images…"));
}

void loop() {
  waitSync();

  // read 4-byte length first  (little-endian)
  uint32_t incomingLen = 0;
  Serial.readBytes(reinterpret_cast<char *>(&incomingLen), 4);
  if (incomingLen != IMG_BYTES) {
    Serial.println(F("Length mismatch – discarding frame"));
    return;
  }

  // read the image itself
  size_t got = Serial.readBytes(reinterpret_cast<char *>(rxBuffer), IMG_BYTES);
  if (got != IMG_BYTES) return;   // timeout – restart sync

  // copy/normalise pixels into the input tensor
  for (uint32_t i = 0; i < IMG_BYTES; ++i) {
    modelSetInput(static_cast<float>(rxBuffer[i]) / 255.0f, i);   // :contentReference[oaicite:1]{index=1}
  }

  // run inference
  if (!modelRunInference()) {                                   // :contentReference[oaicite:2]{index=2}
    Serial.println(F("modelRunInference() failed"));
    return;
  }

  // output scores
  for (int i = 0; i < NUM_CLASSES; ++i) {
    float v = modelGetOutput(i);                                // :contentReference[oaicite:3]{index=3}
    Serial.print(i);
    Serial.print('\t');
    Serial.println(v, 6);
  }
  Serial.println(F("---end---"));
}
