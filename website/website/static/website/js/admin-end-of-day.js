/*
 * Adds an "End of day" (23:59) shortcut to the time picker of the admin
 * datetime fields, next to Django's "Now", "Midnight", "6 a.m." etc.
 * Midnight is the start of a day, so a registration deadline "at midnight"
 * on a date closed before that date started (#276).
 *
 * This file is loaded before Django's DateTimeShortcuts.js, which builds the
 * time pickers on the window load event. DOMContentLoaded fires before that,
 * so the shortcut is added in time.
 */
(function () {
  "use strict";
  const label = document.currentScript.dataset.label || "End of day";
  const END_OF_DAY = "end-of-day";

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof DateTimeShortcuts === "undefined") {
      return;
    }
    DateTimeShortcuts.clockHours.default_.push([label, END_OF_DAY]);

    const handleClockQuicklink = DateTimeShortcuts.handleClockQuicklink;
    DateTimeShortcuts.handleClockQuicklink = function (num, val) {
      if (val !== END_OF_DAY) {
        return handleClockQuicklink.call(this, num, val);
      }
      const endOfDay = new Date(1970, 1, 1, 23, 59, 0, 0);
      const input = DateTimeShortcuts.clockInputs[num];
      input.value = endOfDay.strftime(get_format("TIME_INPUT_FORMATS")[0]);
      input.focus();
      DateTimeShortcuts.dismissClock(num);
    };
  });
})();
