// Once friendlyspaces.ch is live, the bare pages.dev address only redirects there,
// so search engines and shared links never settle on the preview host.
// Branch / commit previews (<hash>.friendly-spaces.pages.dev) keep working.
export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname === "friendly-spaces.pages.dev") {
    url.hostname = "friendlyspaces.ch";
    return Response.redirect(url.toString(), 301);
  }
  return next();
}
