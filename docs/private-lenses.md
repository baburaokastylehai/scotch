# Private Lenses

A lens is the user's interpretation context.

Public deployments can expose demo lenses. A private lens can be injected through deployment secrets and unlocked using a code.

## Why this design

Putting a private profile in a public repository—even obfuscated—would be security theater. So Scotch keeps private personalization outside Git.

The unlock code is not stored. Only a SHA-256 hash is supplied to the application. After successful verification, Flask stores a signed session marker.

For a production multi-user system, replace this prototype mechanism with real authentication and encrypted per-user storage.
