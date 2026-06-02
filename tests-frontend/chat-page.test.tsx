import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Home from "../app/page";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("TechStore chat page", () => {
  it("renders the demo password screen first", () => {
    render(<Home />);

    expect(screen.getByText("Support Chat Demo")).toBeInTheDocument();
    expect(screen.getByLabelText("Demo password")).toBeInTheDocument();
  });

  it("shows customer email input after valid demo password", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ok: true }),
    } as Response);

    render(<Home />);
    fireEvent.change(screen.getByLabelText("Demo password"), {
      target: { value: "demo" },
    });
    fireEvent.click(screen.getByText("Enter demo"));

    await waitFor(() => {
      expect(screen.getByLabelText("Customer email")).toBeInTheDocument();
    });
    expect(
      screen.getByText("Enter any customer email and start a support conversation."),
    ).toBeInTheDocument();
  });

  it("allows a new customer email before sending a message", async () => {
    vi.spyOn(global, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          session_id: "session-1",
          customer_email: "new.customer@example.com",
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          session_id: "session-1",
          assistant_message: "Hello new customer",
          created_at: "2026-06-02T00:00:00Z",
        }),
      } as Response);

    render(<Home />);
    fireEvent.change(screen.getByLabelText("Demo password"), {
      target: { value: "demo" },
    });
    fireEvent.click(screen.getByText("Enter demo"));

    await screen.findByLabelText("Customer email");
    fireEvent.change(screen.getByLabelText("Customer email"), {
      target: { value: "new.customer@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Type your message..."), {
      target: { value: "Hi" },
    });
    fireEvent.click(screen.getByText("Send"));

    await waitFor(() => {
      expect(screen.getByText("Hello new customer")).toBeInTheDocument();
    });
  });
});
