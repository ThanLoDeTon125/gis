import { createRootRoute, createRoute, createRouter } from "@tanstack/react-router";
import "@sankit/types"; // cross-import proves workspace wiring (empty module) — AC14

const rootRoute = createRootRoute();
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: () => <h1>Web Admin</h1>,
});

export const router = createRouter({ routeTree: rootRoute.addChildren([indexRoute]) });
