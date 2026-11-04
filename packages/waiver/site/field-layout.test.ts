/**
 * Tests for the drift field layout table. They are pure: they read the six slots and the field box, and no React renders.
 * A slot box holds the headshot, the price tag, the name label, and the full drift, so no headshot covers another at 390.
 */
import { describe, expect, it } from "vitest";
import { FIELD, fieldScale, scaleSlot, SLOTS, slotBox } from "./field-layout";

/* The page column at 390 pixels, less the two 16 pixel gutters. */
const PHONE_FIELD = 390 - 16 * 2;

describe("the field layout", () => {
  it("has six slots, the biggest for rank 1, then two mid sizes, then three small", () => {
    expect(SLOTS).toHaveLength(6);
    const sizes = SLOTS.map((slot) => slot.size);
    expect(sizes[0]).toBeGreaterThan(sizes[1]);
    expect(sizes[1]).toBe(sizes[2]);
    expect(sizes[2]).toBeGreaterThan(sizes[3]);
    expect(new Set(sizes.slice(3)).size).toBe(1);
  });

  it("fits the field in the page column at 390", () => {
    expect(FIELD.width).toBeLessThanOrEqual(PHONE_FIELD);
  });

  it("keeps every slot box, with its drift, inside the field", () => {
    for (const slot of SLOTS) {
      const box = slotBox(slot);
      expect(box.left).toBeGreaterThanOrEqual(0);
      expect(box.top).toBeGreaterThanOrEqual(0);
      expect(box.right).toBeLessThanOrEqual(FIELD.width);
      expect(box.bottom).toBeLessThanOrEqual(FIELD.height);
    }
  });

  it("has no two slot boxes that overlap, with the drift", () => {
    const boxes = SLOTS.map(slotBox);
    for (let a = 0; a < boxes.length; a++) {
      for (let b = a + 1; b < boxes.length; b++) {
        const apart =
          boxes[a].right <= boxes[b].left ||
          boxes[b].right <= boxes[a].left ||
          boxes[a].bottom <= boxes[b].top ||
          boxes[b].bottom <= boxes[a].top;
        expect(apart, `slot ${a + 1} and slot ${b + 1} overlap`).toBe(true);
      }
    }
  });

  it("gives each slot a different drift period, so the headshots never move in step", () => {
    expect(new Set(SLOTS.map((slot) => slot.period)).size).toBe(6);
  });
});

describe("the field scale", () => {
  it("keeps the table size at 358 and wider, and shrinks it under 358", () => {
    expect(fieldScale(358)).toBe(1);
    expect(fieldScale(448)).toBe(1);
    // A 360 phone has 328 pixels inside the gutters.
    expect(fieldScale(328)).toBeCloseTo(328 / 358);
  });

  it("keeps the table size before a measure, when the width reads 0", () => {
    expect(fieldScale(0)).toBe(1);
  });

  it("scales the place, the size, and the drift of a slot, but not its period", () => {
    expect(scaleSlot(SLOTS[0], 0.5)).toEqual({ x: 89.5, y: 35, size: 44, dx: 4, dy: -5, period: 7 });
  });
});
