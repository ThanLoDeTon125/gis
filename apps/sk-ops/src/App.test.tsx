import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("sk-ops App", () => {
  it("renders Web Admin", async () => {
    render(<App />);
    expect(await screen.findByText("Web Admin")).toBeTruthy();
  });
});
