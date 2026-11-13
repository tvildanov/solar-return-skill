# Birth-time uncertainty and optional rectification

Rectification here is an exploratory astrological ranking, not a scientifically validated way to recover a historical fact. Minute-by-minute search resolution is **not minute-level accuracy**. A higher score is not a probability or a confidence interval. Checking a record is more direct evidence than matching a chart to a biography.

## Ask gently, without imposing a time

- **Time known from a record:** use the stated time, still checking the historical zone and repeated/nonexistent local hours. Do not ask to upload the record.
- **Approximate time:** ask where it comes from and what interval the person considers plausible, for example “between 09:00 and 10:00”. Do not assume ±60 minutes without asking. Explain that the return instant, angles, houses and calendar boundaries can change.
- **No time or interval:** do not default to noon or infer the time from personality, appearance or how a reading “feels”. Offer to look for a record, discuss the method without a chart, or let the user explicitly choose a hypothetical scenario. Label that scenario throughout; it is not a recovered birth time.

For a transition repeated hour, ask which occurrence/UTC offset is intended; `--birth-fold 0` and `1` are distinct candidates. A nonexistent recorded wall time needs clarification, not silent shifting. Use an IANA zone rather than guessing the historical UTC offset.

## Sensitivity first

With consent to an approximate center and a window, run:

```bash
python scripts/rectify.py --birth "1990-05-21 14:30" \
  --birth-tz Europe/Moscow --birth-lat 55.7558 --birth-lon 37.6173 \
  --window 30 --lang en
```

This uses **synthetic example data**, not a default for the user. With no events, it computes natal ASC/MC sensitivity only. The window is ±N elapsed minutes around the selected instant, stepping in UTC so nonexistent local minutes are not invented and repeated-hour occurrences remain distinct. Reports include date and UTC offset. Ask before expanding a search across a date/zone boundary or beyond the range the person meant.

The helper does not compute solar-return uncertainty bounds. To compare return scenarios, run `solar_return.py` separately with each agreed birth-time candidate and the same anniversary year/return place. Label endpoint/midpoint samples as samples, not a proven full range. Do not claim that a house or moment is stable across an unsampled interval.

## Optional event ranking

Only if requested, invite a few dated, non-sensitive milestones the person is comfortable sharing, such as moves, education or job changes. Generic labels are sufficient. Exact dates matter to this particular scoring algorithm; do not turn a remembered month into an invented exact day. Skip undated events or preserve them as context outside the score. Do not treat having fewer than five events as a reason to pressure the person.

Add repeatable arguments such as `--event "2012-08-18|move A"`. The helper rejects duplicate dates (which would overweight one day), dates on/before birth and dates outside its supported year range. The date is represented by noon in the **birth zone**, not an observed event instant. The current method uses slow-planet transits and solar arcs; natal positions and arcs are prepared at the reference birth time rather than recalculated for every minute. These approximations limit interpretation of scores.

Present several candidates and disagreements, not just the top row. Zero scores or tied/very close leaders do not justify selecting one minute. More events can change the ranking; they do not establish validity or guarantee better historical accuracy. Synthetic tests built from the same scoring method check code consistency, not real-world rectification accuracy.

Before using a candidate for a solar return, ask: “Would you like to calculate this as a provisional scenario, keeping your original time alongside it?” Keep the choice explicit, then rerun the calculator. Never overwrite the original birth record or save the selected hypothesis as a fact.

## If the AI cannot execute Python

Explain that this repository's browser calculator currently calculates one chosen birth-time scenario at a time and **does not run event-based rectification**. It can be used to compare agreed scenarios manually. Gather no biography for a computation you cannot perform. Offer the local Python workflow or continue with conceptual explanations.
