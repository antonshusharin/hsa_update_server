# HSA Update Server API Documentation

## Endpoints

### Authentication

#### Login
- **URL:** `/api/v1/login`
- **Method:** POST
- **Description:** Authenticate a user and receive a token.
- **Authentication:** Basic Authentication
- **Returns:** `{"token": Authentication token`

### Releases

#### Get Latest Release
- **URL:** `/api/v1/releases/latest`
- **Method:** GET
- **Description:** Retrieve the latest release.
- **Returns:** Release

#### Upload Release
- **URL:** `/api/v1/releases/upload/<channel>`
- **Method:** POST
- **Description:** Upload a new release to a specific channel.
- **Authentication:** Token required
- **Parameters:**
  - `channel`: The name of the release channel (string)
- **Body:** ZIP file
- **Returns:** Release

#### Get or Delete Release
- **URL:** `/api/v1/releases/<accessibility_version>`
- **Method:** GET, DELETE
- **Description:** Retrieve or delete a specific release.
- **Authentication:** Token required (for DELETE)
- **Parameters:**
  - `accessibility_version`: The accessibility version of the release (integer)
- **Returns:**
  - GET: Release
  - DELETE: No content (204)

### Release Channels

#### List or Create Release Channels
- **URL:** `/api/v1/release-channels`
- **Method:** GET, POST
- **Description:** List all release channels or create a new one.
- **Authentication:** Token required (for POST)
- **Returns:**
  - GET: List of ReleaseChannel
  - POST: ReleaseChannel

#### Get, Update, or Delete Release Channel
- **URL:** `/api/v1/release-channels/<name>`
- **Method:** GET, PUT, PATCH, DELETE
- **Description:** Retrieve, update, or delete a specific release channel.
- **Authentication:** Token required (for PUT, PATCH, DELETE)
- **Parameters:**
  - `name`: The name of the release channel (string)
- **Returns:**
  - GET: ReleaseChannel
  - PUT/PATCH: ReleaseChannel
  - DELETE: No content (204)

#### Add Release to Channel
- **URL:** `/api/v1/release-channels/<channel_name>/add-release/<release_version>`
- **Method:** POST
- **Description:** Add a release to a specific channel.
- **Authentication:** Token required
- **Parameters:**
  - `channel_name`: The name of the release channel (string)
  - `release_version`: The version of the release to add (integer)
- **Returns:** No content (204)

#### Remove Release from Channel
- **URL:** `/api/v1/release-channels/<channel_name>/remove-release/<release_version>`
- **Method:** DELETE
- **Description:** Remove a release from a specific channel.
- **Authentication:** Token required
- **Parameters:**
  - `channel_name`: The name of the release channel (string)
  - `release_version`: The version of the release to remove (integer)
- **Returns:** No content (204)

## Data Types

### Release
- `hearthstone_version`: String
- `accessibility_version`: Integer
- `changelog`: Text
- `upload_time`: DateTime
- `url`: URL (of the release file)

### ReleaseChannel
- `name`: String (Unique, SlugField)
- `description`: Text
- `latest_release`: Nested Release (read-only)


## Authentication

This API uses token-based authentication. To authenticate, include the token in the Authorization header of your requests:

```
Authorization: Token <your_token_here>
```

To obtain a token, use the login endpoint with Basic Authentication.
