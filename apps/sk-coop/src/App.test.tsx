import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("sk-coop App", () => {
  it("renders Web HTX", async () => {
    render(<App />);
    expect(await screen.findByText("Web HTX")).toBeTruthy();
  });
});
