import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, api } from "../api";

function mockFetch(status: number, body: unknown, statusText = "") {
  const fn = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText,
    json: async () => body,
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("requests the /api prefix and returns JSON", async () => {
    const fn = mockFetch(200, { status: "ok" });
    const result = await api.health();
    expect(result).toEqual({ status: "ok" });
    expect(fn.mock.calls[0][0]).toBe("/api/health");
  });

  it("encodes the status filter", async () => {
    const fn = mockFetch(200, []);
    await api.listAssessments("needs revision");
    expect(fn.mock.calls[0][0]).toBe("/api/assessments?status=needs%20revision");
  });

  it("sends the X-Actor header and JSON content type on writes", async () => {
    const fn = mockFetch(200, { id: 1 });
    await api.createAssessment({ title: "t" }, "alice");
    const init = fn.mock.calls[0][1] as RequestInit;
    const headers = init.headers as Headers;
    expect(init.method).toBe("POST");
    expect(headers.get("X-Actor")).toBe("alice");
    expect(headers.get("Content-Type")).toBe("application/json");
  });

  it("throws ApiError with the server detail on failure", async () => {
    mockFetch(422, { detail: "bad actor" }, "Unprocessable");
    await expect(api.summary()).rejects.toMatchObject({
      status: 422,
      message: JSON.stringify("bad actor"),
    });
    await expect(api.summary()).rejects.toBeInstanceOf(ApiError);
  });
});
