import time
import digitalio

class RotaryEncoder:
    """
    Optimized rotary encoder driver.
    """

    def __init__(self, pin_a, pin_b, *, pull=digitalio.Pull.UP, debounce_ms=1, pulses_per_detent=2):
        # -------------------------------
        # Pin initialization
        # -------------------------------
        # Create pin A and set as input with pull-up
        self._a = digitalio.DigitalInOut(pin_a)
        self._a.switch_to_input(pull=pull)

        # Create pin B and set as input with pull-up
        self._b = digitalio.DigitalInOut(pin_b)
        self._b.switch_to_input(pull=pull)

        # Pulses per detent (your encoder typically outputs 2 pulses per detent)
        self._pulses_per_detent = max(1, int(pulses_per_detent))

        # Debounce time in milliseconds
        self._debounce_ms = max(0, int(debounce_ms))

        # Save last values of A/B to detect changes
        self._last_a = self._a.value
        self._last_b = self._b.value

        # Timestamp of last valid change (ms)
        self._last_change_time = time.monotonic() * 1000.0

        # ----------------------------------
        # Encoder position tracking variables
        # ----------------------------------
        self._position_raw = 0      # Raw pulse count
        self._position = 0          # Position in detents
        self._delta_accum = 0       # Accumulated delta

    def update(self):
        """
        Update encoder state, return True if detent position changed.
        """

        # Read current A/B pin states
        a = self._a.value
        b = self._b.value

        # ------------------------
        # Only process when A changes
        # -------------------------
        if a != self._last_a:
            now = time.monotonic() * 1000.0

            # -------------------------
            # Simple debounce
            # -------------------------
            if (now - self._last_change_time) >= self._debounce_ms:

                # ============================================================
                # A falling edge: A goes from HIGH → LOW
                # ============================================================
                if not a:
                    # If B is high → clockwise; else counterclockwise
                    if b:
                        self._position_raw += 1
                    else:
                        self._position_raw -= 1

                # ============================================================
                # A rising edge: A goes from LOW → HIGH
                # ============================================================
                else:
                    # Direction reversed on rising edge
                    if b:
                        self._position_raw -= 1
                    else:
                        self._position_raw += 1

                # Update timestamp
                self._last_change_time = now

                # -------------------------------------------------------）
                # Convert raw pulses into detents (integer steps)
                # -------------------------------------------------------
                new_pos = self._position_raw // self._pulses_per_detent

                # If detent changed, update position and accumulated delta
                if new_pos != self._position:
                    delta = new_pos - self._position
                    self._position = new_pos
                    self._delta_accum += delta

                    # Save last A/B values
                    self._last_a = a
                    self._last_b = b

                    return True

        # Update last A/B even if no detent change
        self._last_a = a
        self._last_b = b
        return False

    # ---------------------------
    # Current position in detents
    # ---------------------------
    @property
    def position(self):
        return self._position

    # ---------------------------
    # Raw pulse count (for debugging)
    # ---------------------------
    @property
    def position_raw(self):
        return self._position_raw

    # ---------------------------
    # Get accumulated change since last call
    # ---------------------------
    def get_delta(self):
        d = self._delta_accum
        self._delta_accum = 0
        return d

    # ---------------------------
    # Reset encoder to zero or specific detent
    # ---------------------------
    def reset(self, *, to_detent=None):
        if to_detent is None:
            # Reset to zero
            self._position_raw = 0
            self._position = 0
        else:
            # Set to specific detent value
            self._position = int(to_detent)
            self._position_raw = self._position * self._pulses_per_detent

        self._delta_accum = 0
