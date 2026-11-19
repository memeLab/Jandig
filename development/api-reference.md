# Jandig API reference

The Jandig server exposes a small read-only HTTP API under `/api/v1/`, used by
the AR viewer and by the Meta Quest MR app. This page documents what it
actually does today.

> **Scope warning.** Everything under `/api/v1/` is **read-only for content**.
> No endpoint creates, updates or deletes markers, objects, artworks, sounds
> or exhibits. The only `POST` endpoints are authentication and the marker
> generator, and the marker generator persists nothing.

## Base URL

| Environment | Base URL |
|---|---|
| Production | `https://jandig.app/api/v1/` |
| Development | `https://dev.jandig.app/api/v1/` |

## Authentication

JWT, via `djangorestframework-simplejwt`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/auth/login/` | `POST` | Exchange `username` + `password` for an access and a refresh token |
| `/api/v1/auth/refresh/` | `POST` | Exchange a `refresh` token for a new access token |
| `/api/v1/auth/verify/` | `POST` | Check that a token is still valid |

Token lifetimes are configured in `src/config/settings.py`:

| Token | Lifetime |
|---|---|
| access | 5 minutes |
| refresh | 1 day |

The access token payload carries three custom claims, added by
`users.serializers.JandigJWTSerializer`: `user_profile_id`, `user_id` and
`username`.

```bash
curl -X POST https://jandig.app/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "someone", "password": "secret"}'
```

```json
{"refresh": "<jwt>", "access": "<jwt>"}
```

> **No endpoint currently requires authentication.** The project defines no
> `permission_classes` anywhere and no `DEFAULT_PERMISSION_CLASSES`, so DRF's
> default `AllowAny` applies and every read below works anonymously. Logging in
> is only useful for reading your own `user_profile_id` out of the token in
> order to filter exhibits by owner. This is safe while the API is read-only
> and the content is public, and it becomes a problem the moment a write
> endpoint is added — see #971.

## Pagination

All list endpoints use `LimitOffsetPagination` with a default page size of
**20** (`PAGE_SIZE` in `src/config/settings.py`).

| Parameter | Meaning |
|---|---|
| `limit` | Number of results to return |
| `offset` | Number of results to skip |

```json
{
  "count": 137,
  "next": "https://jandig.app/api/v1/exhibits/?limit=20&offset=20",
  "previous": null,
  "results": []
}
```

> Note for API clients: `next` and `previous` are absolute URLs built from the
> request host, and may come back over `http://` depending on how the proxy
> forwards the request. Clients that follow them should normalise the scheme.

## Content endpoints

Each of these supports exactly two operations: `GET` on the collection (list)
and `GET` on a single item by numeric id (retrieve).

| Endpoint | Returns |
|---|---|
| `/api/v1/markers/` | Markers, ordered by `id` |
| `/api/v1/objects/` | Augmented objects, ordered by `id` |
| `/api/v1/artworks/` | Artworks (a marker plus an object), ordered by `id` |
| `/api/v1/sounds/` | Sounds, ordered by `id` |
| `/api/v1/exhibits/` | Exhibits, ordered by `-id` |
| `/api/v1/profiles/` | User profiles |

```bash
curl https://jandig.app/api/v1/exhibits/1/
```

### Filtering

Only `/api/v1/exhibits/` accepts query filters. The other endpoints ignore
query parameters other than pagination.

| Parameter | Behaviour |
|---|---|
| `search` | Case-insensitive substring match on the exhibit **name** only — not the slug, not the owner |
| `owner` | Exact match on the owner's **profile id** (an integer). A non-integer value returns an empty result set rather than an error |

```bash
curl "https://jandig.app/api/v1/exhibits/?search=mitologia"
curl "https://jandig.app/api/v1/exhibits/?owner=42"
```

### Response formats

Content endpoints are served by three renderers:

| `?format=` | Result |
|---|---|
| `json` | JSON (the default) |
| `api` | DRF's browsable HTML API |
| `modal` | A rendered HTML modal fragment used by the site itself |

`format=modal` is accepted **only on retrieve**, never on a list — a paginated
response has no single instance for the modal template to render, which used to
produce an HTTP 500. `ModalRetrieveOnlyMixin` enforces that.

### A note on `exhibits`

`ExhibitSerializer` returns `owner` as a **numeric profile id**, not a name. To
display an owner's username you need a second request to
`/api/v1/profiles/<id>/`. This is inconsistent with `Artwork.author`,
`Marker.owner` and `Object.owner`, which are nested objects carrying a
`username`.

The serializer also omits `exhibit_type`, so a client cannot currently tell an
AR exhibit from an MR one through the API.

## Marker generator

| Endpoint | Method |
|---|---|
| `/api/v1/markergenerator/` | `POST` |

Generates a marker image from an uploaded picture and returns it immediately.
**It stores nothing** — no database row, no file in storage.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `source` | file | yes | The image to turn into a marker |
| `inner_border` | `"true"` / `"false"` | no | Add an inner border; defaults to `false` |

The response is **not JSON**: it is an HTML `<img>` tag whose `src` is a
base64-encoded `data:image/png` URI, intended to be dropped straight into a
preview element.

| Status | Meaning |
|---|---|
| `200` | The `<img>` tag |
| `400` | No `source` file in the request |
| `500` | Marker generation failed, with `{"error": "..."}` |

```bash
curl -X POST https://jandig.app/api/v1/markergenerator/ \
  -F "source=@my-image.png" \
  -F "inner_border=true"
```

## Known gaps

* **No OpenAPI/Swagger schema.** Adding `drf-spectacular` is the obvious next
  step, but it cannot be installed cleanly while `exclude-newer = "1 week"` in
  `pyproject.toml` is an invalid value for uv: it breaks `uv add` outright, and
  makes `uv lock` re-resolve the whole dependency tree instead of only the new
  package. That needs fixing first.
* **No write endpoints.** See #971.
* **No permissions layer.** See the authentication section above.
