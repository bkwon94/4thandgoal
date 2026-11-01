/**
 * Tests for useRequest: a late answer after a second call, a change that drops the run, and an unmount during a call.
 * Each test renders the hook and reads only the run that start gives back.
 */
import { cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { useRequest } from "./use-request";

afterEach(() => {
  cleanup();
});

describe("useRequest", () => {
  it("marks the first run stale after a second call", () => {
    const { result } = renderHook(() => useRequest());
    const first = result.current.start();
    const second = result.current.start();
    expect(first.isCurrent()).toBe(false);
    expect(second.isCurrent()).toBe(true);
  });

  it("marks the run stale after a drop", () => {
    const { result } = renderHook(() => useRequest());
    const run = result.current.start();
    result.current.drop();
    expect(run.isCurrent()).toBe(false);
  });

  it("aborts the call and marks the run stale on unmount", () => {
    const { result, unmount } = renderHook(() => useRequest());
    const run = result.current.start();
    expect(run.controller.signal.aborted).toBe(false);
    unmount();
    expect(run.controller.signal.aborted).toBe(true);
    expect(run.isCurrent()).toBe(false);
  });
});
