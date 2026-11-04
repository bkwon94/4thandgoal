/**
 * Tests for the team picker avatar. A missing avatar and a failed avatar both show the default image.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { afterEach, describe, expect, it } from "vitest";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import type { Team } from "@/lib/api";
import { TeamPicker } from "./team-picker";

const DEFAULT_SRC = AVATAR_FALLBACK;

function team(avatar: string | null): Team {
  return { roster_id: 1, team: "Gridiron Ghosts", manager: "Ana", avatar, players: [] };
}

function renderPicker(avatar: string | null) {
  const { container } = render(
    <TeamPicker label="My team" teams={[team(avatar)]} value={null} disabledId={null} onChange={() => {}} />,
  );
  return container.querySelector("img") as HTMLImageElement;
}

afterEach(cleanup);

describe("TeamPicker avatar", () => {
  it("renders the default avatar when the team has none", () => {
    expect(renderPicker(null).getAttribute("src")).toBe(DEFAULT_SRC);
  });

  it("swaps to the default avatar when a real avatar fails to load", () => {
    const img = renderPicker("https://cdn.test/a.png");
    expect(img.getAttribute("src")).toBe("https://cdn.test/a.png");
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe(DEFAULT_SRC);
  });
});

/* The parent owns the choice, so the test holds it in state like the trade form does. */
function ControlledPicker() {
  const [value, setValue] = useState<number | null>(null);
  return <TeamPicker label="My team" teams={[team(null)]} value={value} disabledId={null} onChange={setValue} />;
}

describe("TeamPicker focus", () => {
  it("moves focus to the checked radio after a click on Change my team", () => {
    render(<ControlledPicker />);
    fireEvent.click(screen.getByRole("radio"));
    fireEvent.click(screen.getByRole("button", { name: "Change my team" }));
    expect(document.activeElement).toBe(screen.getByRole("radio", { checked: true }));
  });
});
