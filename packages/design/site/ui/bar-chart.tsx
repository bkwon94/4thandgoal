/**
 * Bar chart primitive built from @ui-sdk/core: one tab stop, the arrow keys between the bars, and a press that picks a bar.
 * ui-sdk ships no chart, so this part holds only the behavior, and each page draws its own bars inside each bar.
 * Use it when: a row of bars each opens its own detail, and the keyboard moves between bars with the arrows.
 * Do not use it when: the reader picks one of a few modes. Use `SegmentedControl` or `ToggleGroup`.
 */
"use client";

import { createChange, createRovingFocus, definePrimitive, type ChangeDetails } from "@ui-sdk/core";
import { createParts } from "@ui-sdk/react/primitive";

type BarChartOptions = {
  value?: string | null;
  defaultValue?: string | null;
  onValueChange?: (value: string | null, details: ChangeDetails<"item-press">) => void;
};

const barChart = definePrimitive({
  name: "bar-chart",
  options: { value: "value", defaultValue: "value", onValueChange: "callback" },
  controlled: ["value"],
  state: (options: BarChartOptions) => ({
    value: options.value ?? options.defaultValue ?? null,
    focused: null as string | null,
  }),
  sync: (options) => (options.value === undefined ? {} : { value: options.value }),
  api: (context) => {
    const change = createChange(context);
    const roving = createRovingFocus(context, { slot: "bar", key: "focused" });
    return {
      roving,
      pick: (value: string, event?: Event) =>
        change("value", value, { reason: "item-press", event }),
    };
  },
  slots: (slot) => ({
    root: slot({ role: "group" }),
    bar: slot<{ value: string }>({
      props: { value: "string" },
      role: "button",
      focus: "roving",
      attrs: (state, part) => ({
        type: "button",
        tabindex: part.api.roving.tabIndex(state, part),
        "data-selected": part.key === state.value ? "" : undefined,
      }),
      press: ({ api, key }, event) => api.pick(String(key), event),
      on: {
        keydown: (event, { el, api }) => {
          if (el) api.roving.keydown(event, el);
        },
      },
      bind: (el, part) => part.api.roving.bind(el, part),
    }),
  }),
  agent: { actions: ["pick"] },
});

const { Root: BarChart, Bar: BarChartBar } = createParts(barChart, { root: "div", bar: "button" });

export { BarChart, BarChartBar };
