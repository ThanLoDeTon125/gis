import { Scalar } from "@scalar/hono-api-reference";
import { Hono } from "hono";
import { describeRoute, openAPIRouteHandler, resolver } from "hono-openapi";
import * as v from "valibot";

const HealthResponseSchema = v.object({
  status: v.literal("ok"),
});

const app = new Hono();

app.get(
  "/health",
  describeRoute({
    tags: ["system"],
    summary: "Health check",
    responses: {
      200: {
        description: "Service is healthy",
        content: {
          "application/json": { schema: resolver(HealthResponseSchema) },
        },
      },
    },
  }),
  (c) => c.json({ status: "ok" as const }),
);

app.get(
  "/openapi.json",
  openAPIRouteHandler(app, {
    documentation: {
      info: {
        title: "Sankit API",
        version: "0.0.0",
        description: "GACP-compliance / traceability platform for Vietnamese medicinal herbs.",
      },
    },
  }),
);

app.get("/docs", Scalar({ url: "/openapi.json", pageTitle: "Sankit API" }));

export default app;
